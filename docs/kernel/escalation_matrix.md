<!--
Vendored from agentic-workforce-kernel @ main.
Do not edit — update by re-vendoring from the source repo.
-->

# Escalation Matrix

## Trigger conditions

| Condition | Action | Owner |
|-----------|--------|-------|
| Task fails 3× | Escalate to HITL | Director |
| Confidence < 0.4 | Flag for human review | Worker |
| Cost > $0.50 per email | Alert + pause | Director |
| Latency > 120 s | Log warning, continue | Worker |
| Classification = "ambiguous" | Force HITL | Router |
| Vision model unavailable | Fall back to text-only | VisionAnalyst |
| LANGSMITH_TRACING = false in production | Block deploy | CI |

## Escalation channels

1. `runtime/agent_handoffs/current_mission.md` — updated with escalation note.
2. LangGraph `interrupt()` — pauses the graph for human input.
3. Run report in `runtime/run_reports/` — includes escalation summary.

## De-escalation

Human operator resumes the graph via the LangGraph checkpointer API, providing
a `HumanReviewDecision` in the state.
