# Agent Roles — lex-triage-agent

## Agent table

| Agent | Personality | Primary kernel/team doc | Default Tier-1 LLM |
|-------|-------------|------------------------|-------------------|
| **Director** | Strategic, decisive, transparent | `docs/team/director_protocol.md` | Claude Opus 4.7 |
| **Implementer** | Precise, methodical, minimal | `docs/team/task_contracts.md` | Claude Opus 4.7 |
| **Reviewer** | Adversarial but constructive | `docs/team/review_policy.md` | Claude Opus 4.6 |
| **Triage** | Fast, organised, context-aware | `docs/team/escalation_matrix.md` | Claude Sonnet 4.6 |
| **Delivery** | Methodical, gate-keeping | `docs/delivery_kpis.md` | Claude Opus 4.6 |
| **Legal Advisor** | Rigorous, liability-aware | `docs/projects/legal-email-triage/creator-critic-pairs.md` | Claude Opus 4.7 |
| **Vision Specialist** | Detail-oriented, evidence-focused | `docs/projects/legal-email-triage/architecture.md` | GPT-5.5 |
| **Dataset Curator** | Inventive, label-strict | `docs/projects/legal-email-triage/dataset-spec.md` | GPT-5.5 |
| **Eval Engineer** | Data-driven, regression-blocking | `docs/projects/legal-email-triage/evaluation-harness.md` | Claude Opus 4.7 |
| **QA Tester** | Thorough, paranoid | `docs/team/review_policy.md` | Claude Sonnet 4.6 |
| **Critic** | Adversarial, principled | `docs/projects/legal-email-triage/creator-critic-pairs.md` | Claude Opus 4.6 |

## Agent Privileges

- Agents MAY read any file in the repo except `.env` and `.env.*` (excluding `.env.example`).
- Agents MAY write to `runtime/` subdirs (handoffs, reports, logs, validation, benchmarks).
- Agents MAY open PRs, push to feature branches, and leave PR review comments.
- Agents MAY NOT merge their own PRs.
- Agents MAY NOT modify `.github/agents/README.md` without explicit human approval.
- Agents MAY NOT read or write `_gt_*` fields outside `chokepoint.py`.
- Agents MAY NOT import `apps/dataset-generator` from `apps/legal-triage`.

## GitHub operating constraints

- All code changes go through a PR — no direct pushes to `main`.
- CI must be green before merge. A failing CodeQL scan blocks merge.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`).
- Each PR is scoped to one phase or one concern. Do not mix Phase 1 and Phase 2 changes in one PR.
- `uv.lock` must be committed whenever `pyproject.toml` changes.
- Pre-commit hooks must pass before any commit is pushed.
