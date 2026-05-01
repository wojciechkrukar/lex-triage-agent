# Telemetry

## LangSmith tracing

Every LangGraph node is wrapped with `@traceable` (LangSmith). The `LANGSMITH_PROJECT` env var controls which project receives traces.

```python
from langsmith import traceable

@traceable(name="classification_node")
def classification_node(state: EmailTriageState) -> EmailTriageState:
    ...
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGSMITH_API_KEY` | — | LangSmith API key (required for tracing) |
| `LANGSMITH_PROJECT` | `lex-triage-dev` | Project name in LangSmith |
| `LANGSMITH_TRACING` | `false` | Set `true` to enable tracing; `false` in CI |

## Cost and latency accumulation

Each node appends to `EmailTriageState.model_calls`:
```python
state["model_calls"].append({
    "node": "classification",
    "model": "claude-haiku-4-5",
    "cost_usd": 0.0003,
    "latency_ms": 450,
})
state["total_cost_usd"] += 0.0003
state["total_latency_ms"] += 450
```

## CI telemetry policy

`LANGSMITH_TRACING=false` is mandatory in CI. Tests use `LLM_TIER=tier3` (stubs). No live API calls in CI.
