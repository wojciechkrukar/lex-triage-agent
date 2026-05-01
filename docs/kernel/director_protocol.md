<!--
Vendored from agentic-workforce-kernel @ main.
Do not edit — update by re-vendoring from the source repo.
-->

# Director Protocol

The **Director** is the top-level orchestration agent. It receives a mission from a human
operator, decomposes it into Tasks, assigns Tasks to Worker agents, and gates on human review
at checkpoints defined in the escalation matrix.

## Responsibilities

1. Maintain the `current_mission.md` in `runtime/agent_handoffs/`.
2. Decompose missions into Tasks conforming to `task_contracts.md`.
3. Assign Tasks to Worker agents via the command grammar (`command_grammar.md`).
4. Monitor Task state transitions; re-assign or escalate on failure.
5. Produce a run report in `runtime/run_reports/` at mission end.

## Mission lifecycle

```
PENDING → IN_PROGRESS → REVIEW → DONE
                      ↘ ESCALATED → HUMAN_REVIEW → (DONE | ABORTED)
```

## Constraints

- The Director MUST NOT execute Tasks itself; it only orchestrates.
- A Task may only be marked DONE by the Worker that executed it plus at least one Critic review.
- The Director MUST log every state transition to `runtime/logs/`.
