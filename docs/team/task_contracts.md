# Task Contracts — lex-triage-agent

> Project-specific task templates. For the universal task schema, see `docs/kernel/task_contracts.md`.

## Task Brief template

```
## Task Brief

**Task ID:** <UUID>
**Mission ID:** <UUID>
**Title:** <one-line title>
**Assigned to:** <agent role>
**Priority:** <1=critical | 2=high | 3=normal>
**Phase:** <phase1 | phase2 | infra | docs>
**Target milestone:** <M0–M7+>
**Depends on:** <task IDs or "none">

### Objective
<What must be accomplished. One paragraph. No ambiguity.>

### Inputs
- <file path or data artifact>

### Acceptance criteria
- [ ] <specific, verifiable criterion>
- [ ] CI green after change
- [ ] Tests added/updated
- [ ] Docs updated if topology/schema changed

### Out of scope
- <explicit exclusions to prevent scope creep>
```

## Implementation Completion Report (ICR) template

```
## Implementation Completion Report

**Task ID:** <UUID>
**PR:** #<number>
**Completed by:** <agent>
**Date:** <YYYY-MM-DD>

### What was done
<Summary of changes made.>

### Files changed
- `path/to/file.py` — reason

### Tests
- Added: <list>
- Modified: <list>
- All passing: yes / no

### KPI impact
- Lead Precision: unchanged / +X pp / -X pp (if measured)
- Cost/Email: unchanged / +X% / -X%
- Latency: unchanged / +Xms / -Xms

### Docs updated
- yes / no — list if yes

### Known limitations / follow-up tasks
<Any known gaps or deferred work.>
```

## QA Report template

```
## QA Report

**Task ID:** <UUID>
**PR:** #<number>
**QA Tester:** QA Tester agent
**Date:** <YYYY-MM-DD>

### Test results
- Total tests: <N>
- Passed: <N>
- Failed: <N>
- Skipped: <N>

### Coverage delta
- Before: <X>%
- After: <Y>%

### Graph topology snapshot
- Unchanged: yes / no
- If changed: describe diff and confirm it is intentional

### Hidden-label leak check
- Pass: yes / no

### Recommendation
- [ ] Approve (all tests pass, no regressions)
- [ ] Request changes (list issues)
```

## Eval Report template

```
## Eval Report

**Run ID:** <UUID>
**Date:** <YYYY-MM-DD>
**LLM_TIER:** <tier1 | tier2>
**Dataset:** <name + version>

### KPIs (vs. baseline)

| KPI | Baseline | This run | Delta |
|-----|----------|----------|-------|
| Lead Precision | X% | Y% | ±Z pp |
| Lead Recall | X% | Y% | ±Z pp |
| Spam FPR | X% | Y% | ±Z pp |
| Cost/Email (USD) | $X | $Y | ±Z% |
| Latency P50 (ms) | X | Y | ±Z ms |

### Regressions
- <list any KPI regression with ∆ > threshold>

### Recommendation
- [ ] No regressions — clear for merge
- [ ] Regression detected — block merge, notify Director
```

## Vision Report schema

```python
class VisionReport(TypedDict):
    scene_type: str          # vehicle_collision | slip_fall | medical | property_damage | other
    damage_severity: str     # none | minor | moderate | severe | catastrophic
    injury_indicators: list[str]
    evidence_quality: str    # poor | fair | good | excellent
    confidence: float        # 0–1
    model_used: str
    cost_usd: float
    latency_ms: int
```
