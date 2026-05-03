# Dataset Specification

## Overview

The Phase 1 dataset consists of synthetic emails with hidden ground-truth labels. The `apps/dataset-generator/` app generates these emails using LLMs + the scenario taxonomy below.

## Scenario taxonomy (target: ≥ 12 scenarios)

| ID | Scenario | email_class | Notes |
|----|----------|-------------|-------|
| S01 | Vehicle collision — rear-end on highway | pi_lead | Include police report attachment |
| S02 | Slip and fall — wet floor in retail store | pi_lead | Include medical record attachment |
| S03 | Dog bite — residential property | pi_lead | Include photo of injury |
| S04 | Medical malpractice — surgical error | pi_lead | Complex SoL cues |
| S05 | Workplace injury — construction site fall | pi_lead | Include OSHA report attachment |
| S06 | Defective product — appliance burn injury | pi_lead | Multi-party liability |
| S07 | Pedestrian struck by vehicle | pi_lead | Severity: severe |
| S08 | Premises liability — broken staircase | pi_lead | Include photo attachment |
| S09 | General legal enquiry — contract dispute | general_legal | No PI, no injury |
| S10 | Invoice / billing enquiry | invoice | No PI |
| S11 | Spam / solicitation | spam | Must be clearly spam |
| S12 | Ambiguous — low-confidence PI indication | pi_lead | Triggers HITL |

## Hidden ground-truth label schema

```python
class RawEmailRecord(PublicEmailRecord):
    gt_class: str            # "pi_lead" | "general_legal" | "spam" | "invoice" | "other"
    gt_severity: str         # "none" | "minor" | "moderate" | "severe" | "catastrophic"
    gt_liability_clarity: str  # "clear" | "unclear" | "contested"
    gt_scenario: str         # one of the 12 scenario IDs below (human-readable name)
    gt_has_attachment: bool  # True if the email has image/doc attachments
    gt_jurisdiction: str     # US state code ("CA", "TX", …) or "unknown"
    gt_sol_years: int | None # Statute of limitations in years; None for non-PI classes
```

### Scenario → `gt_scenario` mapping

| Spec ID | `gt_scenario` value | `gt_class` |
|---------|---------------------|-----------|
| S01 | `vehicle_collision_rear_end` | pi_lead |
| S02 | `slip_fall_retail` | pi_lead |
| S03 | `dog_bite` | pi_lead |
| S04 | `medical_malpractice` | pi_lead |
| S05 | `workplace_injury_construction` | pi_lead |
| S06 | `defective_product` | pi_lead |
| S07 | `pedestrian_struck` | pi_lead |
| S08 | `premises_liability_staircase` | pi_lead |
| S09 | `general_legal_contract` | general_legal |
| S10 | `invoice_billing` | invoice |
| S11 | `spam_solicitation` | spam |
| S12 | `ambiguous_pi_low_confidence` | pi_lead |

## Chokepoint invariant

**`_gt_*` fields MUST be stripped by `chokepoint.py` before any email is passed to Phase 2.**
The `test_chokepoint.py` test actively asserts this invariant holds for all 12 scenario types.

## Target volume

- Phase 1 M1: ≥ 100 emails, balanced across all 12 scenarios.
- At least 60% must be PI leads (reflects realistic intake distribution).
- At least 20% must include image/document attachments.
