# Legal Triage App

LangGraph `StateGraph` pipeline that classifies inbound email and routes new PI leads for HITL review.

## Graph

```
Ingestion → Classification → [Vision] → Appraisal Creator → Appraisal Critic → HITL Gate → Router → {NewLead | GeneralLegal | Refused-Spam | Refused-Invoice | Refused-Other}
```

## Usage

```bash
# Export Mermaid diagram
uv run legal-triage --export-mermaid

# Process a single email (stub mode)
LLM_TIER=tier3 uv run legal-triage --email-file path/to/email.json
```

## LLM Tiers

Set `LLM_TIER` env var:
- `tier1` — full capability (Claude Opus / GPT-4o)
- `tier2` — cost-optimised (Claude Haiku / GPT-4o-mini)
- `tier3` — deterministic stubs, no network (default in tests)
