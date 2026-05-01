# KPIs

## Priority order (strict)

> A lower-rank KPI improvement **never** justifies a higher-rank regression.

| Rank | KPI | Description | Target |
|------|-----|-------------|--------|
| 1 | **Lead Precision** | Of emails classified as PI leads, % that are true PI leads | ≥ 90% at tier1 |
| 2 | **Lead Recall** | Of true PI leads, % correctly identified | ≥ 85% at tier1 |
| 3 | **Spam FPR** | % of non-spam emails incorrectly classified as spam | ≤ 2% |
| 4 | **Cost per Email** | Average USD per email processed end-to-end | ≤ $0.10 at tier1 |
| 5 | **E2E Latency** | Wall-clock time from ingestion to routing decision | < 30 s at tier1 |

## Regression thresholds

| KPI | Director-escalation threshold | Human-required threshold |
|-----|------------------------------|--------------------------|
| Lead Precision | > 2pp drop vs. baseline | > 5pp drop vs. baseline |
| Lead Recall | > 3pp drop vs. baseline | > 8pp drop vs. baseline |
| Spam FPR | > 1pp increase vs. baseline | > 3pp increase vs. baseline |
| Cost/Email | > 50% increase vs. baseline | > 100% increase vs. baseline |
| E2E Latency | > 50% increase vs. baseline | > 2× baseline |

## Measurement

KPIs are computed by the Eval Engineer using:
1. Phase 1 hidden ground-truth labels (stripped through `chokepoint.py` for the triage app; used directly for eval comparison).
2. LangSmith eval harness (see `evaluation-harness.md`).
3. Baseline stored in `runtime/benchmarks/`.
