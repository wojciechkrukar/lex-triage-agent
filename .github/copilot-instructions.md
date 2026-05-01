# Copilot Operating Instructions — lex-triage-agent

## Project purpose
Legal Email Triage: a LangGraph multimodal agentic system that ingests inbound email,
classifies it, and surfaces new personal-injury / accident leads for a law firm with
HITL review and full LangSmith telemetry.

## Repo structure
```
apps/dataset-generator/   Phase 1 — synthetic email + ground-truth label generation
apps/legal-triage/        Phase 2 — LangGraph triage pipeline
docs/kernel/              Vendored governance docs from agentic-workforce-kernel
runtime/                  Agent handoffs, run reports, logs, validation, benchmarks
.github/                  Agent instructions, copilot config
```

## KPI priority order (strict — a lower-rank improvement NEVER justifies a higher-rank regression)
1. Precision on new PI leads
2. Recall on new PI leads
3. E2E latency (< 30 s per email, tier1)
4. Token cost

## Hard rules
- **Never** read, write, or expose `.env` or any file matching `.env.*` (except `.env.example`).
- **Never** touch hidden ground-truth label fields (`_gt_*`) outside `apps/dataset-generator/src/dataset_generator/chokepoint.py`.
- `apps/legal-triage` **MUST NOT** import anything from `apps/dataset-generator`. The triage app is blind to how test data was generated.
- All LLM calls go through `llm_factory.py` in the relevant app. No provider SDK imported directly in node files.
- LLM tier is selected by the `LLM_TIER` env var (`tier1` | `tier2` | `tier3`). See `docs/kernel/state_model.md`.

## LLM tier-selection contract
| Tier | Use case | Typical model |
|------|----------|---------------|
| tier1 | Production, full capability | Claude Opus / GPT-4o |
| tier2 | Dev / cost-optimised | Claude Haiku / GPT-4o-mini |
| tier3 | CI stubs / offline | `stub` (no network) |

`LLM_TIER=tier3` is the default in tests. Never hardcode model names outside `llm_factory.py`.

## Where docs live
- Kernel governance: `docs/kernel/`
- App-level README in each `apps/*/README.md`
- Agent roles: `.github/agents/README.md`

## Telemetry
Every LangGraph node must be wrapped with `@traceable` (langsmith). The `LANGSMITH_PROJECT`
env var controls which project receives traces. Set `LANGSMITH_TRACING=false` in CI unless
explicitly testing telemetry.
