# Human-in-the-Loop Design

## Overview

The system uses `langgraph.interrupt()` to pause the graph and request human input at the HITL Gate node. Humans review the appraisal draft and make a routing decision.

## When HITL is triggered

| Condition | Trigger |
|-----------|---------|
| Appraisal score ≥ 0.65 (normal flow) | After each successful Creator-Critic cycle |
| Appraisal score < 0.65 after 3 iterations | Maximum iterations reached |
| Jurisdiction outside US domestic | Legal Advisor flag |
| Fatality-level severity | Legal Advisor flag |
| Prompt injection suspected | Legal Advisor or Critic flag |
| Email class = ambiguous | Classification node output |

## Human decisions

| Decision | State update | Graph continuation |
|----------|-------------|-------------------|
| `approve` | `human_decision = "approve"` | Router → NewLead |
| `reject` | `human_decision = "reject"` | Router → Refused |
| `reclassify` | `human_decision = "reclassify"` | Back to Classification node |

## HITL queue management

- Maximum queue depth: 20 unreviewed emails.
- At depth > 10: Director is alerted.
- At depth > 20: new email intake is paused; human operator must process queue.
- Queue state is persisted via the LangGraph checkpointer (PostgreSQL recommended for production).

## Resume API

The human operator resumes the graph via the LangGraph checkpointer:
```python
# Resume with approve
graph.update_state(config, {"human_decision": "approve", "human_notes": "Clear PI case"})
graph.invoke(None, config)
```
