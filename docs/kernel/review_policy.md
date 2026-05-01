<!--
Vendored from agentic-workforce-kernel @ main.
Do not edit — update by re-vendoring from the source repo.
-->

# Review Policy

## Code review

- Every PR requires at least one human approval before merge.
- PRs touching `chokepoint.py` or `llm_factory.py` require two approvals.
- Automated Copilot review is advisory only; it does not substitute for human review.
- CodeQL scan must be clean (zero high/critical alerts).

## Output review (agent outputs)

- Every LangGraph node output is logged to LangSmith (via `@traceable`).
- AppraisalCreator output is reviewed by AppraisalCritic before reaching HITL Gate.
- HITL Gate pauses the graph; a human reviews the appraisal summary before the Router runs.
- NewLead terminal sink triggers a Slack/email notification (stub in Phase 1).

## Evaluation harness

- Phase 1 synthetic emails carry ground-truth labels (`_gt_*`).
- After a run, the evaluation harness (Phase 2) compares Router decisions to ground truth.
- Precision/recall on PI leads is reported in `runtime/benchmarks/`.
- A regression gate in CI blocks merge if precision on PI leads drops below 0.90.
