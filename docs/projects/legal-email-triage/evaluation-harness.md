# Evaluation Harness

## Overview

The LangSmith evaluation harness measures triage-pipeline quality against the Phase 1 hidden ground-truth labels. It runs outside the production pipeline, using tier1 or tier2 models, with hidden labels accessed directly (not through the chokepoint).

## Architecture

```
Phase 1 dataset (with _gt_* labels)
         │
         ▼
  Harness: strip visible email → run Phase 2 pipeline (LLM_TIER=tier1) → compare output to _gt_*
         │
         ▼
  KPI computation (Precision, Recall, FPR, Cost, Latency)
         │
         ▼
  LangSmith trace + runtime/benchmarks/<run-id>.json
```

## KPI computation

```python
precision = true_positives / (true_positives + false_positives)
recall    = true_positives / (true_positives + false_negatives)
spam_fpr  = false_spam_positives / total_non_spam
```

## Regression detection

After each run:
1. Load baseline from `runtime/benchmarks/baseline.json`.
2. Compare Lead Precision. If delta < -0.05 (> 5pp drop): set exit code 1; notify Director.
3. Update `runtime/benchmarks/latest.json`.

## Running the harness

```bash
# Full eval run (tier1, live API)
LLM_TIER=tier1 LANGSMITH_TRACING=true uv run --package legal-triage python -m legal_triage eval

# CI smoke test (tier3, stubs, no API)
LLM_TIER=tier3 LANGSMITH_TRACING=false uv run --package legal-triage pytest apps/legal-triage/tests/ -q
```

## Baseline management

- `runtime/benchmarks/baseline.json` — committed baseline; updated by Eval Engineer after each milestone.
- `runtime/benchmarks/latest.json` — overwritten on each eval run; not committed.
- `runtime/benchmarks/<run-id>.json` — archived run results; committed for audit trail.
