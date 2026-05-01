# Escalation Matrix — lex-triage-agent

> Project-specific escalation rules. For universal rules, see `docs/kernel/escalation_matrix.md`.

## Director-owned decisions

These conditions trigger escalation to the Director; no human is required unless the Director cannot resolve.

| Condition | Trigger | Director action |
|-----------|---------|-----------------|
| Task fails 3× | Third FAILED transition | Re-assign or decompose task; log in run report |
| Lead Precision drops ≤ 5pp | Eval report shows regression | Investigate cause; block merge if regression is in current PR |
| Vision provider unavailable | Vision node returns error | Enable text-only fallback; monitor for recovery |
| HITL queue depth > 10 | Queue depth alert | Pause new intake; prioritise HITL review |
| Classification confidence < 0.4 | Classification node output | Force HITL for affected email |
| Cost/email > $0.50 | Per-email cost accumulator | Alert; review model selection; do not pause automatically |
| E2E latency > 30 s at tier1 | Latency accumulator | Log warning; investigate bottleneck node |
| Prompt-injection attempt detected | Legal Advisor or Critic flag | Quarantine email; log; notify human if repeated |
| Scenario taxonomy change requested | Dataset Curator PR | Require Eval Engineer sign-off before merge |

## Human-required decisions

These conditions cannot be resolved by agents alone; the Director must pause and request human operator input.

| Condition | Trigger | Action |
|-----------|---------|--------|
| Dataset hidden-label leak | `_gt_*` field found outside `chokepoint.py` | **Immediate halt.** No eval runs until human signs off on cleanup. |
| Multimodal cost spike > 2× baseline | Vision node cost doubles vs. last run | Halt vision runs; notify human before resuming |
| Higgsfield enabled in production | `ENABLE_HIGGSFIELD=true` detected in prod deploy | Reject deploy; require human approval |
| New LLM provider added | PR adds provider outside `llm_factory.py` | Block PR; human must approve provider onboarding |
| Lead Precision regression > 5pp | Eval report shows > 5pp drop | Block merge; human reviews before any further eval runs |
| Prompt injection from email body confirmed | Security review confirms injection | Quarantine dataset; human security review required |
| HITL queue depth > 20 | Queue depth alert | Suspend new email intake; human operator must process queue |
| Scenario taxonomy change invalidates baseline | Eval baseline would need reset | Human approval required before taxonomy merge |
| Image-sourcing licence change | Non-public-domain source proposed | Human legal/IP review required |
| `docs/kernel/**` modified | PR touches vendored kernel docs | Human must approve provenance bump |

## Escalation channels

1. `runtime/agent_handoffs/current_mission.md` — Director updates status and blockers.
2. LangGraph `interrupt()` — pauses the graph for human input at the HITL gate.
3. `runtime/run_reports/` — mission-end summary includes all escalation events.
4. PR comment — Director leaves a blocking comment on the relevant PR.

## De-escalation

Human operator resumes the graph via the LangGraph checkpointer API, providing a `HumanReviewDecision` in the state (`approve` | `reject` | `reclassify`).
