# Phase 1 Plan — Synthetic Dataset Generator

## Objective

Build a dataset generator that produces synthetic emails with hidden ground-truth labels, suitable for evaluating the Phase 2 triage pipeline.

## Milestones

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M0 | Initial scaffolding (done) | 2026-05-01 |
| M1 | 100 emails, 12 scenarios, ≥ 20 with attachments | TBD |

## M1 exit criteria

- [ ] ≥ 100 synthetic emails generated and stored.
- [ ] All 12 scenario types represented.
- [ ] ≥ 20 emails include image/document attachments.
- [ ] `test_chokepoint.py` passes for all 12 scenario types.
- [ ] Image manifest contains ≥ 50 public-domain images with documented provenance.
- [ ] Dataset is balanced: ≥ 60% PI leads, ≤ 15% spam.

## Open tasks

See `TODO.md` for current open items tagged `[phase1/...]`.

## Key files

| File | Purpose |
|------|---------|
| `apps/dataset-generator/src/dataset_generator/schemas.py` | Pydantic schemas including ground-truth labels |
| `apps/dataset-generator/src/dataset_generator/generator.py` | Email generation logic |
| `apps/dataset-generator/src/dataset_generator/chokepoint.py` | Hidden-label stripper (chokepoint invariant) |
| `apps/dataset-generator/src/dataset_generator/image_manifest.py` | Image provenance catalogue |
| `apps/dataset-generator/tests/test_chokepoint.py` | Label-leak tests |
