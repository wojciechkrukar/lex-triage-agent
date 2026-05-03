# Milestones

> Skyfall-style milestone tracker. Director updates on each milestone completion.

| ID | Name | Status | Description |
|----|------|--------|-------------|
| M0 | Bootstrap | ✅ Done | Initial scaffolding: apps skeleton, kernel docs, CI, LLM factory, state schema |
| M1 | Dataset Generator Content | ✅ Done | 100 emails, 12 scenarios, ≥ 20 attachments, 50-image manifest, all M1 KPI gates green (2026-05-01) |
| M2 | Phase 2 Graph Nodes | ✅ Done | Classification (Haiku), Appraisal Creator (Opus), Legal Advisor nodes; all 64 tests green (2026-05-02) |
| M3 | Vision Provider | ✅ Done | GPT-4o multimodal; base64 attachments; text-only fallback; cost tracked (2026-05-02) |
| M4 | Eval Harness | ✅ Done | `legal-triage eval` CLI; baseline in `runtime/benchmarks/`; regression gate (2026-05-02) |
| M5 | HITL UI Handoff | ✅ Done | `hitl_queue.py` with thread-safe depth/alert logic; `hitl_gate.py` enqueues on trigger; interactive `lex_triage_interactive.ipynb` with ipywidgets approve/reject/reclassify UI; auto-mode fallback; 92 tests green (2026-05-02) |
| M6 | Production Precision Target | 🔲 Open | Lead Precision ≥ 90% on tier1 in eval harness |
| M7 | Executive Dashboard Notebook | 🔲 Open | Jupyter notebook: graph topology, KPIs, confusion matrix, cost/latency, CEO summary |
| M8+ | Post-MVP | 🔲 Open | Jurisdiction expansion, multi-language support, CRM integration |

## Milestone exit criteria

See `docs/delivery_kpis.md` for per-milestone KPI exit criteria.

## M0 detail (Done)

- Initial `README.md`, `LICENSE`, `.gitignore`, `.env.example`.
- `apps/dataset-generator/` skeleton with schemas, generator, chokepoint, tests.
- `apps/legal-triage/` skeleton with graph, state, nodes, LLM factory, tests.
- `docs/kernel/` vendored from agentic-workforce-kernel.
- `.github/workflows/` CI pipeline.
- PR #1 merged 2026-05-01.
- PR #2 merged 2026-05-01 (agent governance scaffolding, this PR).
