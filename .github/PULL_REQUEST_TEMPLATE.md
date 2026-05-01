## PR Class

<!-- Select the class per docs/team/review_policy.md -->
- [ ] A — Documentation only
- [ ] B — Test-only change
- [ ] C — Node logic change (graph node code, prompt templates)
- [ ] D — State schema or graph topology change
- [ ] E — LLM tier matrix or chokepoint change (requires human approval)

## Linked Task Brief

<!-- Issue number or path to Task Brief file -->
Closes #

## Summary

<!-- One paragraph: what changed and why -->

## Implementation Completion Report

<!-- Paste ICR from docs/team/task_contracts.md template, or write inline -->

### What was done

### Files changed

### Tests
- [ ] New tests added
- [ ] Existing tests pass (`uv run --package <app> pytest -q`)

## Telemetry impact

<!-- Did this change add/remove LangSmith spans? Change LLM_TIER behaviour? -->
- [ ] No telemetry impact
- [ ] Added span(s): 
- [ ] `LANGSMITH_TRACING` still env-var-only (not hardcoded)

## KPI priority order check

<!-- Confirm no lower-rank KPI gain traded for higher-rank regression -->
- [ ] Lead Precision unaffected or improved
- [ ] Lead Recall unaffected or improved
- [ ] No model names hardcoded outside `llm_factory.py`

## Merge blockers (all must be clear)

- [ ] CI green (pytest + ruff + CodeQL)
- [ ] `apps/legal-triage` does NOT import from `apps/dataset-generator`
- [ ] No `_gt_*` fields outside `chokepoint.py`
- [ ] `docs/kernel/**` NOT modified (or provenance bump included)
- [ ] `uv.lock` updated if `pyproject.toml` changed
