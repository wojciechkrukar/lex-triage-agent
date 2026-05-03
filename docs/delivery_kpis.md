# Delivery KPIs

> Per-milestone exit criteria mapped to the strict KPI priority order in `docs/projects/legal-email-triage/kpis.md`.

## KPI priority reminder

1. Lead Precision (**never** regress this for any other gain)
2. Lead Recall
3. Spam FPR
4. Cost per Email
5. E2E Latency

---

## M0 — Bootstrap (Done)

- [x] All tests pass (`pytest -q`).
- [x] CI pipeline green.
- [x] No hardcoded secrets.
- [x] No hardcoded model names outside `llm_factory.py`.

## M1 — Dataset Generator Content

- [ ] ≥ 100 emails generated, all 12 scenarios covered.
- [ ] `test_chokepoint.py` passes for all 12 scenario types.
- [ ] Image manifest: ≥ 50 images with documented public-domain provenance.
- [ ] Dataset balance: ≥ 60% PI leads, ≤ 15% spam.
- [ ] No `_gt_*` fields reachable downstream of `chokepoint.py`.
- [ ] CI green.

## M2 — Phase 2 Graph Nodes

- [ ] Classification node: Lead Precision ≥ 80% on M1 dataset (tier3 stubs acceptable for CI; tier1 for milestone validation).
- [ ] Legal Appraisal Creator: appraisal drafts structured per template in `docs/team/task_contracts.md`.
- [ ] Legal Advisor: appraisal scores calibrated (mean score ≥ 0.7 on true PI leads, ≤ 0.4 on non-PI).
- [ ] All nodes have tier3 stubs; CI green.
- [ ] Graph topology snapshot test passes.

## M3 — Vision Provider

- [ ] Vision node: scene_type accuracy ≥ 80% on test attachment set.
- [ ] Text-only fallback: graph completes successfully with no attachments.
- [ ] Vision cost per email ≤ $0.05 at tier1.

## M4 — Eval Harness

- [ ] LangSmith harness computes all 5 KPIs from `docs/projects/legal-email-triage/kpis.md`.
- [ ] Baseline established and committed to `runtime/benchmarks/baseline.json`.
- [ ] Regression detection: eval fails if Lead Precision drops > 5pp.
- [ ] Lead Precision ≥ 85% at tier1 on full M1 dataset.
- [ ] Lead Recall ≥ 80% at tier1.

## M5 — HITL UI Handoff

- [ ] HITL queue depth monitored; alert at > 10.
- [ ] Human reviewer can resume graph via checkpointer API.
- [ ] Queue depth > 20 triggers intake suspension.

## M6 — Production Precision Target

- [ ] Lead Precision ≥ 90% at tier1 on held-out test set.
- [ ] Lead Recall ≥ 85% at tier1.
- [ ] Spam FPR ≤ 2%.
- [ ] Cost/Email ≤ $0.10 at tier1.
- [ ] E2E Latency < 30 s at tier1 (P50).

## M7 — Executive Dashboard Notebook

- [ ] `notebooks/lex_triage_dashboard.ipynb` runs end-to-end without errors (Kernel → Restart and Run All).
- [ ] §1 Graph topology rendered with correct nodes and edges.
- [ ] §2 KPI scorecard gauges populated from `runtime/benchmarks/latest.json`.
- [ ] §3 Confusion matrix rendered with correct class labels.
- [ ] §4 Per-node cost breakdown visible (requires tier1 eval run).
- [ ] §5 Latency histogram with P50/P90/P95 markers.
- [ ] §6 HITL queue analytics with alert thresholds visible.
- [ ] §7 CEO one-page summary card printed with correct business-impact estimates.
- [ ] Notebook gracefully falls back to synthetic demo data if no real eval results are present.
