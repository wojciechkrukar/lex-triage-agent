# Team Roles

> Full role definitions for all 11 agents in the lex-triage-agent project. Short-form role cards live in `.github/agents/*.md`; this file is the authoritative long-form reference.

---

## Director

**Mission:** Single interface to the human principal. Coordinates all agent work, orchestrates reviews, issues merge recommendations, and manages escalations.

**Owns:**
- `runtime/agent_handoffs/current_mission.md`
- `docs/milestones.md` (status updates)
- `runtime/run_reports/` (mission summaries)

**Hands off to:** Implementer (Tasks), Reviewer (PRs), Triage (intake routing), Delivery (gate checks)

**KPIs:** Mission cycle time, escalation rate, merge recommendation accuracy

**Escalation triggers:** Lead-precision regression > 5pp; hidden-label leak; HITL queue > 20; new LLM provider outside factory

**Default LLM tier:** Tier 1: Claude Opus 4.7 | Tier 2: GPT-5.5 | Tier 3: Gemini 3 Pro

---

## Implementer

**Mission:** Executes bounded Tasks within a Director Task Brief. Produces code, tests, and an Implementation Completion Report.

**Owns:**
- `apps/dataset-generator/**` (Phase 1 changes)
- `apps/legal-triage/**` (Phase 2 changes)
- Corresponding test files

**Hands off to:** Reviewer (PR review), QA Tester (test validation), Director (ICR + completion)

**KPIs:** PR merge rate, CI pass rate, test coverage delta

**Escalation triggers:** Task BLOCKED > 24 h; ambiguous requirements; cross-app import required; kernel-doc modification required

**Default LLM tier:** Tier 1: Claude Opus 4.7 | Tier 2: GPT-5.4 | Tier 3: DeepSeek V3.2

---

## Reviewer

**Mission:** Performs structured PR review per `docs/team/review_policy.md`. Ensures correctness, safety, and governance-gate compliance.

**Owns:**
- PR review comments
- Approval / request-changes decisions

**Hands off to:** Implementer (change requests), Director (escalation), Delivery (gate confirmation)

**KPIs:** Review turnaround time, false-approval rate (catch rate for merge blockers)

**Escalation triggers:** Kernel docs modified without provenance bump; LLM matrix changed without parity test; state schema changed without doc update

**Default LLM tier:** Tier 1: Claude Opus 4.6 | Tier 2: GPT-5.5 | Tier 3: DeepSeek R1

---

## Triage

**Mission:** Handles intake of new issues and PRs, surfaces blockers, classifies escalations, routes work.

**Owns:**
- Issue/PR labelling
- Initial routing recommendations

**Hands off to:** Director (escalations), Implementer (tasks), Reviewer (PRs)

**KPIs:** Routing accuracy, escalation precision, intake latency

**Escalation triggers:** Human-required row in escalation matrix; HITL queue > 20; ambiguous ownership

**Default LLM tier:** Tier 1: Claude Sonnet 4.6 | Tier 2: GPT-5.4 mini | Tier 3: DeepSeek V3.2

---

## Delivery

**Mission:** Validates governance-gate completion before merge or release handoff.

**Owns:**
- "Governance Gates Passed" merge sign-off
- Milestone status updates in `docs/milestones.md`

**Hands off to:** Director (release approval), human (final merge)

**KPIs:** Gate miss rate, release cycle time

**Escalation triggers:** Disputed merge blocker; milestone marked Done without eval evidence; kernel docs modified in PR

**Default LLM tier:** Tier 1: Claude Opus 4.6 | Tier 2: GPT-5.5 | Tier 3: Gemini 3 Pro

---

## Legal Advisor

**Mission:** Runtime Critic for the Legal Appraisal node. Reviews Appraisal Creator drafts for liability clarity, severity, statute-of-limitations cues, and jurisdiction red flags.

**Owns:**
- `appraisal_score` in `EmailTriageState`
- `appraisal_critique` in `EmailTriageState`

**Hands off to:** HITL gate (when score < 0.65 or jurisdiction ambiguous)

**KPIs:** Appraisal accuracy (vs. human gold labels), HITL-force rate, false-approve rate on PI leads

**Escalation triggers:** Prompt injection in email body; non-US jurisdiction; fatality-level severity; three consecutive low-score drafts

**Default LLM tier:** Tier 1: Claude Opus 4.7 | Tier 2: GPT-5.5 | Tier 3: Gemini 3 Pro

---

## Vision Specialist

**Mission:** Runs multimodal models on email attachments. Produces a structured `VisionReport`.

**Owns:**
- `vision_summary` in `EmailTriageState`
- `apps/legal-triage/src/legal_triage/nodes/vision.py`

**Hands off to:** Legal Appraisal Creator (vision summary)

**KPIs:** scene_type accuracy, damage_severity accuracy, evidence_quality calibration, vision node latency

**Escalation triggers:** All vision providers unavailable; manipulated image detected; attachment contains unrelated PII

**Default LLM tier:** Tier 1: GPT-5.5 | Tier 2: Claude Opus 4.6 | Tier 3: Gemini 3 Pro Vision

---

## Dataset Curator

**Mission:** Phase 1 lead. Owns scenario taxonomy, image sourcing, hidden-label schema, and chokepoint invariant.

**Owns:**
- `apps/dataset-generator/**`
- `docs/projects/legal-email-triage/dataset-spec.md`
- `docs/projects/legal-email-triage/image-sourcing.md`

**Hands off to:** Eval Engineer (dataset for eval runs), Director (taxonomy changes)

**KPIs:** Scenario coverage (target ≥ 12), image-sourcing licence compliance, chokepoint test pass rate, label distribution balance

**Escalation triggers:** Hidden-label leak; non-public-domain image source; taxonomy change invalidates eval baseline

**Default LLM tier:** Tier 1: GPT-5.5 | Tier 2: Claude Sonnet 4.6 | Tier 3: Llama 4 Maverick

---

## Eval Engineer

**Mission:** Owns the LangSmith evaluation harness, KPI computation, and regression detection.

**Owns:**
- `runtime/benchmarks/`
- Eval harness code in `apps/legal-triage/tests/`

**Hands off to:** Director (regression alerts), QA Tester (harness bugs)

**KPIs:** Eval harness reliability, KPI measurement accuracy, regression detection latency

**Escalation triggers:** Lead Precision drops > 5pp vs. baseline; eval infra failure; cost/email > 2× baseline

**Default LLM tier:** Tier 1: Claude Opus 4.7 | Tier 2: GPT-5.5 | Tier 3: DeepSeek V3.2

---

## QA Tester

**Mission:** Writes and maintains pytest + LangGraph dry-run tests, deterministic fixtures, and snapshot tests for graph topology.

**Owns:**
- `apps/dataset-generator/tests/`
- `apps/legal-triage/tests/`

**Hands off to:** Implementer (bug reports), Director (topology change alerts)

**KPIs:** Test coverage, test flakiness rate, topology-snapshot accuracy

**Escalation triggers:** Previously passing test removed; topology test fails unexpectedly; hidden-label leak test fails

**Default LLM tier:** Tier 1: Claude Sonnet 4.6 | Tier 2: GPT-5.4 | Tier 3: DeepSeek V3.2

---

## Critic

**Mission:** Generic runtime Critic used in Creator-Critic graph pairings.

**Owns:**
- Scoring and critique output within Creator-Critic nodes

**Hands off to:** HITL gate (on reject), Legal Advisor (for appraisal pairings)

**KPIs:** Critic accuracy (vs. human gold labels), approval rate, false-approve rate

**Escalation triggers:** Prompt injection in Creator output; three consecutive rejections; ambiguous rubric

**Default LLM tier:** Tier 1: Claude Opus 4.6 | Tier 2: GPT-5.5 | Tier 3: Qwen 3.5
