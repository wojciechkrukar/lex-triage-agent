# Current Mission

**Mission ID:** M1-DATASET-CONTENT-001
**Status:** PENDING
**Assigned agent:** Dataset Curator
**Started:** —
**Last updated:** 2026-05-01

## Objective

Phase 1 — Expand the synthetic dataset generator to produce ≥ 100 emails with hidden ground-truth labels and image attachments, covering all 12 scenario types.

## Task Brief reference

See open issue: `#TODO: [phase1/dataset-curator]` in `TODO.md`

## Acceptance criteria (M1 exit)

- [ ] ≥ 100 synthetic emails generated across all 12 scenarios.
- [ ] ≥ 20 emails include image/document attachments.
- [ ] Image manifest: ≥ 50 public-domain images with documented provenance.
- [ ] Dataset balance: ≥ 60% PI leads, ≤ 15% spam.
- [ ] `test_chokepoint.py` passes for all 12 scenario types.
- [ ] CI green.

## Blockers

None currently identified.

## Notes

- Higgsfield is available for synthetic image augmentation (`ENABLE_HIGGSFIELD=false` by default; set to `true` in `.env` to enable for local development only — never in CI).
- All images must be documented in `apps/dataset-generator/src/dataset_generator/image_manifest.py`.
- `_gt_*` fields must only exist in `apps/dataset-generator/` and must be stripped by `chokepoint.py` before any data leaves Phase 1.

## Previous mission

- [DONE] Bootstrap (PR #1 + PR #2): initial scaffolding + agent governance scaffolding.
