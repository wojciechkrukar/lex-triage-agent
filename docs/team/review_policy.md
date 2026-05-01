# Review Policy — lex-triage-agent

> Project-specific extension of `docs/kernel/review_policy.md`.

## PR class matrix

| Class | Description | Required reviewers | Additional requirements |
|-------|-------------|-------------------|------------------------|
| **A** | Documentation only (no code change) | 1 × Director or Reviewer | None |
| **B** | Test-only change (no production code) | 1 × QA Tester | QA Report |
| **C** | Node logic change (graph node code, prompt templates) | 1 × Reviewer + 1 × Legal Advisor (if appraisal node) | QA Report |
| **D** | State schema or graph topology change (`EmailTriageState`, edges, nodes added/removed) | 1 × Reviewer + 1 × Director | QA Report + architecture.md update |
| **E** | LLM tier matrix change OR chokepoint change (`llm_factory.py`, `llm-roster.md`, `chokepoint.py`) | 1 × Reviewer + 1 × Director + human approval | Parity test passing + label-leak test passing |

## Merge blockers (apply to all classes)

A PR MUST NOT be merged if any of the following are true:
- [ ] CI is failing (any of: pytest, ruff, CodeQL).
- [ ] `apps/legal-triage` imports from `apps/dataset-generator`.
- [ ] Any `_gt_*` field appears outside `chokepoint.py` in the diff.
- [ ] `docs/kernel/**` is modified without a provenance-bump commit.
- [ ] `uv.lock` is not updated when `pyproject.toml` changes.
- [ ] `LANGSMITH_TRACING=true` is hardcoded (must be env var only).
- [ ] A model name is hardcoded outside `llm_factory.py`.

## Additional merge blockers per class

- **Class C:** At least one new test covers the changed node logic.
- **Class D:** `docs/projects/legal-email-triage/architecture.md` updated to reflect topology change.
- **Class E:** Parity test between `docs/llm-roster.md` and `ROLE_TIER_MATRIX` in `llm_factory.py` passes; label-leak test passes.

## Review checklist (for Reviewer)

1. Classify the PR (A–E).
2. Verify all merge blockers are clear.
3. Confirm `uv.lock` is up to date.
4. Confirm no hardcoded secrets or model names.
5. Confirm `LLM_TIER=tier3` is used in all new tests.
6. Check diff for unintended scope creep.
7. Leave explicit verdict: **Approved** or **Changes Requested** with specific issues.
