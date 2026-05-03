# Lex Triage Agent — Technical Walkthrough

> **Interview demo guide.** This document walks through every layer of the system — from synthetic dataset generation to the live LangGraph pipeline — explaining *what* each piece does, *why* it was designed that way, and *where* in the code it lives.

---

## 1. What the project solves

A personal-injury law firm receives hundreds of inbound emails per day. Most are spam, invoices, or general legal inquiries. Hidden inside that noise are **new PI leads** — potential clients who have just been in an accident and need representation. Missing a lead means lost revenue; wrongly flagging a non-lead as a lead wastes attorney time.

This system automates the triage step:

1. An email arrives.
2. A multi-agent LangGraph pipeline classifies it, analyses any photo attachments, writes a legal appraisal, and stress-tests that appraisal.
3. If the email looks like a PI lead, it is held for attorney review (Human-in-the-Loop) before being committed to the intake CRM.
4. All decisions are logged to LangSmith for full auditability.

**KPI priority order (strict — a lower-rank gain never justifies a higher-rank regression):**

| # | KPI |
|---|-----|
| 1 | Precision on new PI leads |
| 2 | Recall on new PI leads |
| 3 | E2E latency < 30 s at tier1 |
| 4 | Token cost |

---

## 2. Repo map

```
apps/dataset-generator/   Phase 1 — synthetic labelled email corpus
apps/legal-triage/        Phase 2 — LangGraph inference pipeline
notebooks/                Interactive runner + executive dashboard
runtime/benchmarks/       Evaluation results (JSON, versioned)
docs/kernel/              Governance docs (Director protocol, state model)
```

The two apps are **intentionally isolated** — the triage pipeline has zero imports from the dataset generator, making the evaluation blind to how the test data was produced.

---

## 3. Phase 1 — Synthetic Dataset Generator

### Why synthetic data?

Real client emails contain PII and are privileged. Synthetic data lets us build, iterate, and evaluate the pipeline without touching real cases.

### Twelve ground-truth scenarios

| Code | Scenario |
|------|---------|
| S01 | Vehicle collision — rear-end |
| S02 | Slip and fall — retail |
| S03 | Dog bite |
| S04 | Medical malpractice |
| S05 | Workplace injury — construction |
| S06 | Defective product |
| S07 | Pedestrian struck by vehicle |
| S08 | Premises liability — staircase |
| S09 | General legal — contract |
| S10 | Invoice / billing |
| S11 | Spam solicitation |
| S12 | Ambiguous PI (low confidence) |

S01–S08 are true PI leads. S09–S12 are distractors. S12 is intentionally ambiguous to stress-test uncertainty handling.

### Schema — the data firewall

Two Pydantic models enforce separation ([`schemas.py`](apps/dataset-generator/src/dataset_generator/schemas.py)):

```
RawEmailRecord          ← internal only; contains all gt_* fields
    └─ stripped by chokepoint.strip_labels()
PublicEmailRecord       ← the only thing the triage pipeline ever sees
```

Hidden ground-truth fields on `RawEmailRecord`:

| Field | Values |
|-------|--------|
| `gt_class` | `pi_lead \| general_legal \| spam \| invoice \| other` |
| `gt_scenario` | one of the 12 codes above |
| `gt_severity` | `none \| minor \| moderate \| severe \| catastrophic` |
| `gt_liability_clarity` | `clear \| unclear \| contested` |
| `gt_urgency` | 1–10 |
| `gt_jurisdiction`, `gt_sol_years` | metadata |

### The chokepoint

[`chokepoint.py`](apps/dataset-generator/src/dataset_generator/chokepoint.py) is the **only module** that may touch `gt_*` fields. It exposes three functions:

- `strip_labels(record)` — takes `RawEmailRecord`, pops every gt field, returns `PublicEmailRecord`.
- `strip_labels_dict(record)` — same for raw dicts (used in the eval harness).
- `assert_no_gt_fields(record)` — used in tests to enforce the firewall never leaks.

This is enforced by a test suite (`test_chokepoint.py`). Any module outside the generator that imports a `gt_*` field fails CI.

### Template-based generation

[`generator.py`](apps/dataset-generator/src/dataset_generator/generator.py) holds two dicts of string templates per scenario:

- `_SCENARIO_SUBJECTS` — 2–3 subject-line templates with `{date}`, `{store}` placeholders.
- `_SCENARIO_BODIES` — 2–3 multi-paragraph body templates with `{date}`, `{amount}`, `{weeks}`, `{name}` placeholders.

A seeded `random.Random` fills placeholders with realistic values (medical costs $3k–$85k, realistic dates, attorney names). Output is written to `apps/dataset-generator/out/emails_gt.jsonl` (with labels) and `emails.jsonl` (labels stripped).

### Optional: real images

[`image_downloader.py`](apps/dataset-generator/src/dataset_generator/image_downloader.py) and [`image_manifest.py`](apps/dataset-generator/src/dataset_generator/image_manifest.py) attach Creative Commons photos (accident scenes, medical imagery) to PI emails as base64-encoded `ImageAttachment` objects. This enables end-to-end multimodal evaluation without using proprietary imagery.

---

## 4. Phase 2 — LangGraph Triage Pipeline

### Graph topology

```
START
  └─► ingestion
        └─► classification
              ├─ (has attachments?) ─► vision ──┐
              └─ (no attachments)  ─────────────┤
                                                 ▼
                                         appraisal_creator
                                                 │
                                         appraisal_critic
                                                 │
                                          hitl_gate
                                         ╱         ╲
                              (hitl_required)    (no hitl)
                                   │                 │
                               INTERRUPT          router
                                                     │
                                                    END
                             ┌──────────────────────┤
                             ▼                       ▼
                          NewLead            GeneralLegal
                         Refused-Spam       Refused-Invoice
                         Refused-Other
```

Implemented in [`graph.py`](apps/legal-triage/src/legal_triage/graph.py) as a LangGraph `StateGraph`. All nodes share a single `TriageState` TypedDict.

---

### 4.1 Shared state — `TriageState`

[`state.py`](apps/legal-triage/src/legal_triage/state.py) defines the object that flows through every node:

```python
class TriageState(TypedDict):
    # Input
    email_id: str
    raw_email: str
    attachments: list[dict]        # [{filename, content_type, data_b64}]

    # Classification
    email_class: str | None        # "pi_lead" | "general_legal" | "spam" | "invoice" | "other"
    class_confidence: float | None

    # Vision
    vision_summary: str | None

    # Appraisal
    appraisal_draft: str | None
    appraisal_score: float | None  # 0–1, set by Critic
    appraisal_critique: str | None

    # HITL
    hitl_required: bool
    human_decision: str | None     # "approve" | "reject" | "reclassify"
    human_notes: str | None

    # Routing
    terminal_sink: str | None      # "NewLead" | "GeneralLegal" | "Refused-*"

    # Telemetry
    total_cost_usd: float
    total_latency_ms: int
    model_calls: list[ModelCall]

    # Errors
    errors: list[str]
```

Each node returns only the keys it modifies; LangGraph merges them into the shared state. `total_cost_usd` and `total_latency_ms` are running accumulators — every node adds its own timing and LLM cost.

---

### 4.2 Node walk-through

#### Node 1 — `ingestion_node`
**File:** [`nodes/ingestion.py`](apps/legal-triage/src/legal_triage/nodes/ingestion.py)  
**LLM call:** none

Validates that `raw_email` is non-empty, strips whitespace, records `latency_ms`. Decorated with `@traceable(name="ingestion")` so LangSmith captures it as a named span.

---

#### Node 2 — `classification_node`
**File:** [`nodes/classification.py`](apps/legal-triage/src/legal_triage/nodes/classification.py)  
**LLM:** `claude-haiku-4-5` (tier1/tier2) — fast and cheap; acts as the precision gate  
**LLM call:** 1× text completion

**Prompt** (inline constant `_CLASSIFICATION_PROMPT`):
```
You are a legal email classifier. Classify the following email into exactly
one of these categories:
- pi_lead: New personal injury or accident lead
- general_legal: General legal inquiry (not PI)
- spam: Spam, junk, or unsolicited commercial email
- invoice: Invoice, billing statement, or payment request
- other: Anything else

Return ONLY the category name, nothing else.

EMAIL:
{email}
```

The response is stripped to lowercase and validated against `_VALID_CLASSES`. Anything unrecognised defaults to `"other"` and logs an error. Confidence is a simple heuristic — `0.95` for stubs, `0.7` for real models — kept intentionally coarse because the appraisal critic provides a better quality signal downstream.

---

#### Node 3 — `vision_node` *(conditional — only when `attachments` is non-empty)*
**File:** [`nodes/vision.py`](apps/legal-triage/src/legal_triage/nodes/vision.py)  
**LLM:** `gpt-4o` (tier1) / `gpt-4o-mini` (tier2) — OpenAI used for all vision roles  
**LLM call:** 1× multimodal completion

**Prompt text** (inline constant `_VISION_TEXT_PROMPT`):
```
You are a legal scene analyst reviewing images attached to an email.
Describe any visible damage, injuries, or hazards relevant to a
personal injury claim. Be concise (max 3 sentences).

Context: {email_class} claim
Attachments: {attachment_count} image(s)
```

For real LLMs the node builds a LangChain `HumanMessage` with interleaved `text` + `image_url` content parts — each image is passed as a `data:{content_type};base64,{data}` URI. For `StubLLM` (tier3), the plain text string is passed directly. The result (`vision_summary`) is injected into the appraisal prompt in the next node.

---

#### Node 4 — `appraisal_creator_node`
**File:** [`nodes/appraisal_creator.py`](apps/legal-triage/src/legal_triage/nodes/appraisal_creator.py)  
**LLM:** `claude-opus-4-5` (tier1) — most capable model in the chain; high precision is paramount  
**LLM call:** 1× long-form completion

**Prompt** (inline constant `_APPRAISAL_PROMPT`):
```
You are a senior legal intake specialist. Draft a concise appraisal
for the following email classified as a personal injury lead.

EMAIL:
{email}

VISION NOTES (if any):
{vision_summary}

Your appraisal should cover:
1. Incident type and date (if mentioned)
2. Alleged injuries and severity
3. Liability assessment (clear/unclear/contested)
4. Recommended next step (intake call, request documents, decline)

Be factual and professional. Max 200 words.
```

`{vision_summary}` is either the vision node's analysis or `"No attachments."`. The result is `appraisal_draft`.

**Why Opus here?** This is the output attorneys will read. Precision on PI leads is KPI #1 — the creator runs once per email and its quality directly determines whether an attorney bothers opening the file.

---

#### Node 5 — `appraisal_critic_node`
**File:** [`nodes/appraisal_critic.py`](apps/legal-triage/src/legal_triage/nodes/appraisal_critic.py)  
**LLM:** `claude-opus-4-5` (tier1)  
**LLM call:** 1× structured completion

**Prompt** (inline constant `_CRITIC_PROMPT`):
```
You are an adversarial legal reviewer. Critique the following appraisal
draft and assign a quality score.

APPRAISAL DRAFT:
{appraisal_draft}

Respond in exactly this format:
SCORE: <float between 0.0 and 1.0>
CRITIQUE: <one paragraph critique>
```

The `SCORE:` line is extracted with a regex. It becomes `appraisal_score` (0–1), which the HITL gate uses as a signal. This implements the **creator-critic pattern**: the creator optimises for completeness, the critic stress-tests for accuracy — together they surface the emails where a human attorney really must look.

---

#### Node 6 — `hitl_gate_node`
**File:** [`nodes/hitl_gate.py`](apps/legal-triage/src/legal_triage/nodes/hitl_gate.py)  
**LLM call:** none

HITL review is triggered if **any** of:
- `email_class == "pi_lead"` — every new PI lead always gets attorney eyes
- `appraisal_score < 0.7`
- `class_confidence < 0.6`

When triggered, the gate calls `hitl_queue.enqueue()` (thread-safe counter). The LangGraph conditional edge function `hitl_gate_condition` then returns `"interrupt"`, which causes the graph to suspend and return control to the caller. The caller (notebook runner or CLI) collects the attorney's decision and resumes the graph.

**Production vs demo:** Setting `HITL_AUTO_APPROVE=true` bypasses the gate entirely and injects `human_decision="approve"` — useful for batch eval and CI, never for real casework.

**Queue safety:** `hitl_queue.py` fires alert callbacks at depth > 10 (Director alert) and depth > 20 (intake suspension per firm policy). The queue is a thread-locked in-process counter — in a real deployment this would be a database row.

---

#### Node 7 — `router_node`
**File:** [`nodes/router.py`](apps/legal-triage/src/legal_triage/nodes/router.py)  
**LLM call:** none (deterministic map)

```python
"pi_lead"        → "NewLead"
"general_legal"  → "GeneralLegal"
"spam"           → "Refused-Spam"
"invoice"        → "Refused-Invoice"
"other"          → "Refused-Other"
```

Human override takes precedence: `reject → "Refused-Other"`, `reclassify → "GeneralLegal"`. The result is `terminal_sink` — the only field downstream CRM integration needs to read.

---

### 4.3 LLM Factory — `llm_factory.py`

[`llm_factory.py`](apps/legal-triage/src/legal_triage/llm_factory.py) is the **only file** that imports LangChain provider SDKs. No node file ever calls `ChatAnthropic` or `ChatOpenAI` directly.

**Tier matrix:**

| Role | Tier 1 | Tier 2 | Tier 3 |
|------|--------|--------|--------|
| classifier | `claude-haiku-4-5` | `claude-haiku-4-5` | `StubLLM` |
| vision | `gpt-4o` | `gpt-4o-mini` | `StubLLM` |
| appraisal_creator | `claude-opus-4-5` | `claude-haiku-4-5` | `StubLLM` |
| appraisal_critic | `claude-opus-4-5` | `claude-haiku-4-5` | `StubLLM` |
| router | `claude-haiku-4-5` | `claude-haiku-4-5` | `StubLLM` |

`get_llm(role)` reads `LLM_TIER` from env, selects the model map, and returns `ChatAnthropic`, `ChatOpenAI`, or `StubLLM`. If the required API key is absent it silently falls back to `StubLLM` with a warning — so the notebook works out of the box without credentials.

**`StubLLM`** is a deterministic offline stand-in:
- Classifier role: runs a keyword-matching heuristic over the `EMAIL:` section of the prompt (spam → invoice → general_legal → pi_lead → other, first match wins). This makes tier3 eval metrics meaningful — the confusion matrix reflects real classification logic, not noise.
- All other roles: return hardcoded canned responses that pass downstream parsing (e.g. `"SCORE: 0.85\nCRITIQUE: …"`).

**`extract_cost(message, model_name)`** reads `response_metadata` from the returned `AIMessage` (both Anthropic and OpenAI token-usage formats are handled) and multiplies by a pricing lookup table. Falls back to 0.0 for stubs.

---

## 5. Evaluation harness

[`eval.py`](apps/legal-triage/src/legal_triage/eval.py) runs the full pipeline against the GT JSONL dataset:

1. Loads `emails_gt.jsonl` (or `emails_demo_gt.jsonl`), strips gt_ fields before passing each record to the pipeline.
2. Runs `graph.invoke(initial_state(...))` per record.
3. Compares `terminal_sink` vs `expected_sink` (derived from `gt_class`).
4. Computes KPIs:
   - **Lead Precision** = TP / (TP + FP)
   - **Lead Recall** = TP / (TP + FN)
   - **Spam FPR** (non-spam refused-as-spam rate)
   - P50 / P90 / P95 latency
   - Total + mean cost USD
5. Writes `runtime/benchmarks/<timestamp>.json` and symlinks to `latest.json`.
6. **Regression gate**: if `baseline.json` exists and Lead Precision drops > 5 pp, exits with code 1 — blocks the merge.

Run via CLI: `uv run legal-triage eval --dataset apps/dataset-generator/out/emails_demo_gt.jsonl --save-baseline`

---

## 6. The Notebooks

### `lex_triage_dashboard.ipynb` — Executive Dashboard

Reads `runtime/benchmarks/latest.json` (or generates synthetic demo data if missing) and renders:

- **§1** — Live Plotly graph topology (nodes + edges, colour-coded by type)
- **§2** — KPI scorecard with RAG status (green/amber/red vs targets)
- **§3** — Confusion matrix heatmap (sklearn + Plotly)
- **§4** — Per-node cost breakdown bar chart
- **§5** — Latency histogram with P50/P90/P95 annotations
- **§6** — HITL queue analytics (approve/reject/reclassify distribution)
- **§7** — CEO one-page summary table

No API keys needed (`LLM_TIER=tier3`, `HITL_AUTO_APPROVE=true`). Designed to be shown live in an interview or management review without touching production.

### `lex_triage_interactive.ipynb` — Live Pipeline Runner

Actually executes the pipeline. The `HitlBatchRunner` class drives a two-stage loop:

**Stage 1:** `graph.invoke(initial_state(...))` — runs every node up to `hitl_gate`.  
**Stage 2:** if `hitl_required` and no decision yet, either:
- **Auto mode** — score-based heuristic (`≥ 0.75 → approve`, `< 0.35 → reject`, else random weighted by `auto_approve_rate` slider).
- **Interactive mode** — renders a styled HTML review card (email subject, sender, body snippet, appraisal draft, score), shows three `ipywidgets` buttons (Approve / Reject / Reclassify), and `await`s an `asyncio.Future` that resolves on button click. `nest_asyncio` enables `asyncio.run()` inside Jupyter's event loop.

After the run, inline charts match the dashboard's full KPI suite.

---

## 7. Telemetry

Every node function is decorated with `@traceable(name="<node>")` from LangSmith. This produces a trace tree where each node is a named span with timing, input/output snapshots, and cost. The `LANGSMITH_PROJECT` env var routes all traces to the correct LangSmith project. `LANGSMITH_TRACING=false` disables all telemetry in CI.

---

## 8. Key design decisions worth discussing

| Decision | Rationale |
|----------|-----------|
| **LangGraph `StateGraph` over a simple chain** | Enables conditional branching (vision bypass), graph interrupt for HITL, and clean node isolation. Each node is a pure function returning only the keys it changes. |
| **Creator-critic appraisal pair** | A single LLM appraisal is overconfident. The critic adds an independent quality signal (`appraisal_score`) that the HITL gate uses to decide whether an attorney review is mandatory — turning model uncertainty into a workflow signal. |
| **Chokepoint pattern for ground truth** | A single module that is the only allowed reader/writer of `gt_*` fields, enforced by tests. Prevents accidental label leakage from the dataset generator into the evaluator. |
| **Tier3 stubs with real heuristics** | CI runs fully offline. The stub classifier uses keyword matching over the same prompt text the real LLM receives, so the confusion matrix in the dashboard reflects genuine classification logic even without API keys. |
| **`llm_factory.py` as the model boundary** | All provider SDK imports are centralised. Swapping a model (e.g. Haiku → Gemini) is a one-line change in the factory; no node files change. |
| **HITL as a first-class graph node** | The interrupt pattern (LangGraph `END` on `hitl_required`) means the graph state is fully serialisable at the pause point — enabling durable HITL queues in a production deployment without re-running prior nodes. |
| **Regression gate in the eval harness** | Lead Precision is KPI #1. The harness exits with code 1 if it drops > 5 pp vs baseline, blocking merges that harm the KPI the firm cares most about. |

---

## 9. Running the demo

```bash
# 1. Install dependencies (no API keys needed for tier3)
uv sync

# 2. Run all tests
uv run pytest -q

# 3. Generate synthetic dataset
uv run dataset-generator generate --n 100 --seed 42

# 4. Run evaluation (tier3 stubs, no network)
LLM_TIER=tier3 uv run legal-triage eval \
    --dataset apps/dataset-generator/out/emails_demo_gt.jsonl \
    --save-baseline

# 5. Open the dashboard notebook (shows charts from latest.json)
jupyter lab notebooks/lex_triage_dashboard.ipynb

# 6. Open the interactive runner (live pipeline with HITL widgets)
jupyter lab notebooks/lex_triage_interactive.ipynb
```

For real model calls, set `LLM_TIER=tier1`, `ANTHROPIC_API_KEY`, and `OPENAI_API_KEY` in `.env`.

---

*This project demonstrates: LangGraph multi-agent orchestration, creator-critic agent patterns, multimodal LLM integration, Human-in-the-Loop workflow design, evaluation harness with regression gating, LangSmith telemetry, and a clean chokepoint data-firewall pattern.*
