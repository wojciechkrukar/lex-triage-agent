# Dataset Generator

Generates ~100 synthetic emails across legal-injury scenarios and distractors.

## Usage

```bash
uv run dataset-gen --out apps/dataset-generator/out/emails.jsonl --count 100
```

## Ground-truth labels

Each raw email carries hidden fields:

| Field | Values |
|-------|--------|
| `_gt_class` | `pi_lead`, `general_legal`, `spam`, `invoice`, `other` |
| `_gt_severity` | `low`, `medium`, `high`, `critical` |
| `_gt_liability_clarity` | `clear`, `unclear`, `contested` |
| `_gt_scenario` | `car_accident`, `slip_fall`, `workplace`, `medical`, `other` |

**These fields are stripped by `chokepoint.py` before any analyzer sees them.**
The stripped emails are written to `out/`. Raw emails (with GT) never leave the generator.
