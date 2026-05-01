# Milestones

> Skyfall-style milestone tracker. Director updates on each milestone completion.

| ID | Name | Status | Description |
|----|------|--------|-------------|
| M0 | Bootstrap | ✅ Done | Initial scaffolding: apps skeleton, kernel docs, CI, LLM factory, state schema |
| M1 | Dataset Generator Content | 🔲 Open | 100 emails, 12 scenarios, ≥ 20 attachments, image manifest |
| M2 | Phase 2 Graph Nodes | 🔲 Open | Classification, Appraisal Creator, Legal Advisor nodes implemented |
| M3 | Vision Provider | 🔲 Open | GPT-5.5 OpenAI vision provider + text-only fallback |
| M4 | Eval Harness | 🔲 Open | LangSmith harness wired, baseline established, regression detection active |
| M5 | HITL UI Handoff | 🔲 Open | HITL queue UI, human reviewer workflow, queue depth monitoring |
| M6 | Production Precision Target | 🔲 Open | Lead Precision ≥ 90% on tier1 in eval harness |
| M7+ | Post-MVP | 🔲 Open | Jurisdiction expansion, multi-language support, CRM integration |

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
