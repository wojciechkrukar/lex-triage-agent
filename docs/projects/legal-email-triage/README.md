# Legal Email Triage — Project Overview

> A LangGraph multimodal agentic system that ingests inbound email, classifies personal-injury leads, and surfaces them for law-firm intake review.

## Quick links

| Document | Purpose |
|----------|---------|
| [architecture.md](architecture.md) | Graph DAG, node descriptions, `EmailTriageState` schema |
| [agents.md](agents.md) | Agent roster with personality column |
| [creator-critic-pairs.md](creator-critic-pairs.md) | Creator-Critic pairing contracts |
| [hitl.md](hitl.md) | Human-in-the-loop design |
| [telemetry.md](telemetry.md) | LangSmith tracing and cost tracking |
| [kpis.md](kpis.md) | KPI definitions and priority order |
| [dataset-spec.md](dataset-spec.md) | Phase 1 scenario taxonomy and label schema |
| [image-sourcing.md](image-sourcing.md) | Image provenance rules |
| [phase-1-plan.md](phase-1-plan.md) | Phase 1 delivery plan |
| [phase-2-plan.md](phase-2-plan.md) | Phase 2 delivery plan |
| [evaluation-harness.md](evaluation-harness.md) | LangSmith eval harness design |

## System summary

```
Email → Ingestion → Classification → Vision (multimodal) → Legal Appraisal (Creator-Critic) → HITL → Router
```

- **Phase 1:** Synthetic email + accident-image dataset with hidden ground-truth labels (`apps/dataset-generator/`).
- **Phase 2:** LangGraph triage pipeline with Creator-Critic appraisal, HITL interrupt, and LangSmith telemetry (`apps/legal-triage/`).

## KPI priority order (strict)

1. Lead Precision on new PI leads
2. Lead Recall on new PI leads
3. Spam False Positive Rate
4. Cost per Email
5. E2E Latency (< 30 s at tier1)

A lower-rank KPI improvement **never** justifies a higher-rank regression.
