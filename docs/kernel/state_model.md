<!--
Vendored from agentic-workforce-kernel @ main.
Do not edit — update by re-vendoring from the source repo.
-->

# State Model

## TriageState (LangGraph TypedDict)

```python
class TriageState(TypedDict):
    # Input
    email_id: str
    raw_email: str
    attachments: list[dict]          # [{filename, content_type, data_b64}]

    # Classification
    email_class: str | None          # "pi_lead" | "general_legal" | "spam" | "invoice" | "other"
    class_confidence: float | None

    # Vision
    vision_summary: str | None

    # Appraisal
    appraisal_draft: str | None
    appraisal_score: float | None    # 0–1, set by Critic
    appraisal_critique: str | None

    # HITL
    hitl_required: bool
    human_decision: str | None       # "approve" | "reject" | "reclassify"
    human_notes: str | None

    # Routing
    terminal_sink: str | None        # "NewLead" | "GeneralLegal" | "Refused-Spam" | ...

    # Telemetry
    total_cost_usd: float
    total_latency_ms: int
    model_calls: list[dict]          # [{node, model, cost_usd, latency_ms}]

    # Errors
    errors: list[str]
```

## LLM tier contract

| Tier | Env value | Resolver behaviour |
|------|-----------|-------------------|
| tier1 | `LLM_TIER=tier1` | Uses full-capability models (Claude Opus, GPT-4o) |
| tier2 | `LLM_TIER=tier2` | Uses cost-optimised models (Claude Haiku, GPT-4o-mini) |
| tier3 | `LLM_TIER=tier3` | Returns deterministic stubs — no network calls |

All tier resolution happens in `llm_factory.py`. Node files never import provider SDKs directly.
