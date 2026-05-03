# Phase 2 Plan — LangGraph Triage Pipeline

## Objective

Build the production triage pipeline: ingest emails, classify PI leads, run multimodal vision analysis, produce a legal appraisal memo via Creator-Critic, and surface confirmed leads via HITL.

## Milestones

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M2 | Classification + Appraisal nodes implemented | TBD |
| M3 | Vision provider (GPT-5.5) implemented | TBD |
| M4 | Eval harness wired to LangSmith | TBD |
| M5 | HITL UI handoff | TBD |
| M6 | Lead Precision ≥ 90% in production eval | TBD || M7 | Executive Dashboard Notebook | TBD |
## M2 exit criteria

- [ ] Classification node live with Claude Haiku 4.5 at tier1.
- [ ] Legal Appraisal Creator node live with Claude Opus 4.7 at tier1.
- [ ] Legal Advisor (Critic) node live with Creator-Critic loop.
- [ ] All nodes have tier3 stubs; CI green.
- [ ] Graph topology snapshot test passes.

## M3 exit criteria

- [ ] `OpenAIVisionProvider` implemented with GPT-5.5 at tier1.
- [ ] Text-only fallback implemented and tested.
- [ ] Vision node cost logged to `EmailTriageState.model_calls`.

## M4 exit criteria

- [ ] LangSmith eval harness computes Lead Precision, Recall, Spam FPR.
- [ ] Baseline stored in `runtime/benchmarks/`.
- [ ] Regression detection: fail if Lead Precision drops > 5pp.

## M7 exit criteria

- [ ] `notebooks/lex_triage_dashboard.ipynb` runs Kernel → Restart and Run All without errors.
- [ ] Graph topology, KPI scorecard, confusion matrix, cost, latency, HITL, and CEO summary sections all render.
- [ ] Notebook degrades gracefully to synthetic demo data when `runtime/benchmarks/latest.json` is absent.

## Key files

| File | Purpose |
|------|--------|
| `apps/legal-triage/src/legal_triage/graph.py` | LangGraph StateGraph definition |
| `apps/legal-triage/src/legal_triage/state.py` | EmailTriageState TypedDict |
| `apps/legal-triage/src/legal_triage/llm_factory.py` | LLM tier resolver |
| `apps/legal-triage/src/legal_triage/nodes/` | Individual node implementations |
| `apps/legal-triage/src/legal_triage/eval.py` | Evaluation harness |
| `notebooks/lex_triage_dashboard.ipynb` | M7 executive dashboard |
