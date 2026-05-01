# Director Protocol — lex-triage-agent

> Project-specific extension of `docs/kernel/director_protocol.md`. Read the kernel doc first for universal rules; this file adds project-specific startup checks, dispatch details, and escalation thresholds.

## Startup checklist

When beginning any Director session, execute in order:

1. **Read** `runtime/agent_handoffs/current_mission.md` — note current Mission ID, status, owner, and blockers.
2. **Check** `TODO.md` at repo root — identify Open items and their target milestones.
3. **Verify** `LLM_TIER` env var is set appropriately:
   - `tier3` for any CI or automated run.
   - `tier1` or `tier2` for human-supervised development sessions.
4. **Check** `runtime/benchmarks/` for the latest eval baseline — note current Lead Precision.
5. **Review** open PRs — confirm no PR is blocked waiting for Director action.

## Dispatch loop

```
FOR each open task in TODO.md (sorted by milestone priority):
  IF task is BLOCKED → surface blocker, attempt resolution or escalate
  IF task is PENDING and owner is identified → dispatch Task Brief to owner agent
  IF task has no owner → route via Triage agent
  AFTER each dispatch → update runtime/agent_handoffs/current_mission.md
END
```

## Project-specific escalation thresholds

| Condition | Threshold | Response |
|-----------|-----------|----------|
| Lead Precision regression | > 5pp drop vs. last baseline | Halt dispatch; notify human; log in run report |
| Vision provider unavailable | 100% of calls fail | Enable text-only fallback; notify human if > 1 h |
| Hidden-label leak detected | Any occurrence | Immediate halt; human review required before resuming |
| Higgsfield enabled in production | `ENABLE_HIGGSFIELD=true` in prod | Reject deploy; escalate to human |
| New LLM provider added | Any PR adding provider outside `llm_factory.py` | Block PR; request correction |
| HITL queue depth | > 20 unreviewed | Pause new intake; alert human operator |
| Scenario taxonomy change | Any modification to dataset-spec.md | Require Eval Engineer sign-off before merging |
| Image-sourcing licence change | Any non-public-domain source added | Require human approval |

## Merge recommendation criteria

The Director may issue a merge recommendation only when all of the following are true:
1. CI is green (pytest + ruff + CodeQL).
2. Reviewer has approved with no unresolved comments.
3. Delivery agent has issued "Governance Gates Passed".
4. PR class-appropriate additional reviewers have approved (see `docs/team/review_policy.md`).
5. For Class C–E PRs: QA Tester has submitted a QA Report.
6. For Class E PRs (LLM tier matrix or chokepoint change): human approval required.

## Run report format

At mission end, produce `runtime/run_reports/YYYY-MM-DD-<mission-id>.md` with:
- Mission ID and objective
- Tasks dispatched, completed, failed, escalated
- KPI delta (Lead Precision before/after if eval was run)
- Total LLM cost (USD) and latency (ms) accumulated in state
- Open items carried forward to next mission
