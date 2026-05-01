# GitHub Flow — lex-triage-agent

## Core rules

1. **Never push to `main` directly.** All changes go through a PR.
2. **One Task Brief per PR.** A PR must reference exactly one Task Brief (GitHub issue or `runtime/agent_handoffs/` document).
3. **PR template required.** Every PR must use `.github/PULL_REQUEST_TEMPLATE.md`.
4. **CI must be green before merge.** No exceptions.
5. **Squash merge preferred** for feature branches to keep `main` history clean.

## Branch lifecycle

```
main
 └─ task/<id>-<slug>   ← created by Implementer from main
     └─ (commits)
     └─ PR opened → reviewed → approved → merged to main → branch deleted
```

## PR checklist (enforced by template)

- [ ] PR class declared (A–E per `docs/team/review_policy.md`)
- [ ] Linked Task Brief (issue number or file path)
- [ ] Implementation Completion Report included
- [ ] Telemetry impact noted (`LANGSMITH_TRACING` unchanged? New spans added?)
- [ ] KPI priority order checked (no lower-rank improvement traded for higher-rank regression)
- [ ] `uv.lock` updated if `pyproject.toml` changed
- [ ] CI green

## Release flow

1. Director confirms all milestone exit criteria are met (`docs/delivery_kpis.md`).
2. Delivery agent issues "Governance Gates Passed".
3. Director issues merge recommendation.
4. Human operator performs the final merge to `main`.
5. Director updates `docs/milestones.md` and `runtime/agent_handoffs/current_mission.md`.

## READ-ONLY zones

### `docs/kernel/**`
Vendored from the agentic-workforce-kernel. All files contain a provenance note at the top. To update:
1. Create a PR with `chore: vendor kernel @ <version>` as title.
2. Include the source commit SHA in the commit message.
3. Requires human approval.

### Cross-app import boundary
`apps/legal-triage` **MUST NOT** import from `apps/dataset-generator`. The triage app is intentionally blind to how test data was generated. This boundary is enforced by `apps/dataset-generator/tests/test_chokepoint.py`.

### `.env` and `.env.*`
Never committed. Only `.env.example` is allowed in version control. All secrets are loaded via `pydantic-settings.BaseSettings`.

## Commit message convention

Follow Conventional Commits:
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation change
- `test:` — test change
- `chore:` — build, CI, or maintenance change
- `refactor:` — code restructuring without behaviour change

Scope optional but recommended: `feat(vision): add OpenAI provider`
