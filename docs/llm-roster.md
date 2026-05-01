# LLM Roster

> Authoritative tier matrix for all agent roles. A parity test enforces this file stays in sync with `ROLE_TIER_MATRIX` in `apps/legal-triage/src/legal_triage/llm_factory.py`.

## Tier semantics

| Tier | Env value | Use case |
|------|-----------|----------|
| tier1 | `LLM_TIER=tier1` | Production, full capability |
| tier2 | `LLM_TIER=tier2` | Dev / cost-optimised |
| tier3 | `LLM_TIER=tier3` | CI stubs / offline — no network calls |

Default: `LLM_TIER=tier3` in all CI environments.

## Role matrix

| Role | Tier 1 | Tier 2 | Tier 3 |
|------|--------|--------|--------|
| Director / Architect | Claude Opus 4.7 | GPT-5.5 | Gemini 3 Pro |
| Implementer / Coder | Claude Opus 4.7 | GPT-5.4 | DeepSeek V3.2 |
| Reviewer (PR-level) | Claude Opus 4.6 | GPT-5.5 | DeepSeek R1 |
| Critic (runtime, generic) | Claude Opus 4.6 | GPT-5.5 | Qwen 3.5 |
| Classifier (fast email triage node) | Claude Haiku 4.5 | Gemini 3 Flash | Llama 4 Scout |
| Classification Critic / Triage | Claude Sonnet 4.6 | GPT-5.4 mini | DeepSeek V3.2 |
| Vision Specialist | GPT-5.5 | Claude Opus 4.6 | Gemini 3 Pro Vision |
| Legal Appraisal Creator | Claude Opus 4.7 | GPT-5.5 | Gemini 3 Pro |
| Legal Advisor / Legal Appraisal Critic | Claude Opus 4.7 | GPT-5.5 | Gemini 3 Pro |
| QA Tester | Claude Sonnet 4.6 | GPT-5.4 | DeepSeek V3.2 |
| Dataset Curator | GPT-5.5 | Claude Sonnet 4.6 | Llama 4 Maverick |
| Eval Engineer | Claude Opus 4.7 | GPT-5.5 | DeepSeek V3.2 |

## Fallback semantics

1. If the Tier-1 key is missing or the provider returns 4xx, the factory drops to Tier-2 and emits a structured LangSmith warning span.
2. If Tier-2 also fails, the factory drops to Tier-3 (stub) and sets `EmailTriageState.errors` with a fallback notice.
3. No silent degradation — every fallback is logged to `runtime/logs/`.

## Override knobs

- Global: `LLM_TIER=tier1|tier2|tier3` in `.env`.
- Per-call: `get_llm(role="vision_specialist", tier_override="tier2")`.
- Test: `LLM_TIER=tier3` is always used in pytest; stubs return deterministic fixtures.

## Rationale

- **Anthropic Opus** is the default for roles requiring deep reasoning, legal judgment, or agentic coding. Consistently leads SWE-bench Verified, GPQA Diamond, and agentic tool-use evals (2025–2026).
- **GPT-5.5** leads the Vision Specialist slot — strongest published results on accident-scene and document interpretation (ARC-AGI-2 visual reasoning, 2026).
- **Claude Haiku / Gemini Flash** for the Classifier node: 30–100× cheaper per call vs. Opus; paired with a heavier Critic node for uncertain cases.
- **Open-weights Tier 3** (DeepSeek, Qwen, Llama 4) for on-prem / PII-constrained deployments. Quality delta is quantified by the eval harness.
- **Higgsfield** is optional, behind `ENABLE_HIGGSFIELD=false`, for synthetic dataset image augmentation only — never as the primary vision analyzer.
