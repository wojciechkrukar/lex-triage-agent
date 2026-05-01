# Collaboration Rules — lex-triage-agent

## Branch naming

| Branch type | Pattern | Example |
|------------|---------|---------|
| Feature / task | `task/<short-id>-<slug>` | `task/42-add-vision-node` |
| Phase 1 work | `phase1/<slug>` | `phase1/expand-scenario-taxonomy` |
| Phase 2 work | `phase2/<slug>` | `phase2/classification-node` |
| Eval work | `eval/<slug>` | `eval/langsmith-harness-v2` |
| Documentation | `docs/<slug>` | `docs/update-team-roles` |
| Bugfix | `fix/<slug>` | `fix/chokepoint-leak` |
| Infra / CI | `infra/<slug>` | `infra/add-codeql-scan` |

Never push to `main`. All work goes through PRs.

## Parallel work rules

- **Phase 1 and Phase 2 MUST NOT be in the same PR.** The isolation between `apps/dataset-generator` and `apps/legal-triage` is a hard invariant.
- Two agents MAY work in parallel on Phase 1 and Phase 2 simultaneously, as long as they do not share state.
- Two agents MAY NOT modify the same file in parallel — coordinate via Task Brief dependencies.
- The Director MUST update `runtime/agent_handoffs/current_mission.md` when dispatching parallel tasks so each agent knows the full in-flight picture.

## Who touches what

| Path | Authorised agents |
|------|------------------|
| `apps/dataset-generator/**` | Dataset Curator + Implementer |
| `apps/legal-triage/**` | Implementer (all nodes), Vision Specialist (vision node), Legal Advisor (appraisal nodes) |
| `docs/kernel/**` | Director only (provenance bump required) |
| `docs/team/**` | Director + Reviewer |
| `docs/projects/legal-email-triage/**` | Director, Vision Specialist (architecture.md), Dataset Curator (dataset-spec.md, image-sourcing.md), Eval Engineer (evaluation-harness.md, kpis.md) |
| `docs/llm-roster.md` | Director only |
| `runtime/agent_handoffs/**` | Director |
| `runtime/run_reports/**` | Director |
| `runtime/benchmarks/**` | Eval Engineer |
| `runtime/logs/**` | Any agent (append-only) |
| `.github/agents/**` | Director (with human approval for README.md) |
| `.github/workflows/**` | Implementer + Director |
| `TODO.md` | Director |

## Conflict resolution

1. If two agents' branches conflict in the same file, the Director arbitrates.
2. Director assigns ownership of the conflicting file to one agent for the duration of the task.
3. The other agent waits for the owning agent's PR to merge before resuming.
4. If the conflict involves `docs/kernel/**`, escalate to human.

## READ-ONLY zones

- `docs/kernel/**` — vendored from the kernel. All files have provenance notes at the top. Changes require a kernel-version bump in the same PR, subject to human approval.
- `apps/legal-triage` MUST NOT import anything from `apps/dataset-generator`. The triage app is blind to how test data was generated. This is enforced by the label-leak test in `apps/dataset-generator/tests/test_chokepoint.py`.
