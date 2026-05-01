# Agent Roles — lex-triage-agent

## Agent table

| Agent | Personality | Responsibilities |
|-------|-------------|-----------------|
| **Copilot** | Precise, conservative | Code scaffolding, PR review, CI fixes |
| **DataGen** | Inventive, label-strict | Synthetic email generation (Phase 1) |
| **Classifier** | Analytical, skeptical | Email classification node (Phase 2) |
| **VisionAnalyst** | Methodical, detail-oriented | Image/attachment analysis (Phase 2) |
| **AppraisalCreator** | Thorough, structured | Legal appraisal drafting (Phase 2) |
| **AppraisalCritic** | Adversarial, rigorous | Appraisal critique & scoring (Phase 2) |
| **HITLGate** | Deferential, transparent | Human-in-the-loop interrupt (Phase 2) |
| **Router** | Fast, deterministic | Terminal sink routing (Phase 2) |

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
