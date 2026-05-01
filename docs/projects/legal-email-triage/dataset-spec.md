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
class GroundTruthLabel(TypedDict):
    _gt_class: str           # "pi_lead" | "general_legal" | "spam" | "invoice" | "other"
    _gt_severity: str        # "none" | "minor" | "moderate" | "severe" | "catastrophic"
    _gt_scenario_id: str     # "S01" – "S12"
    _gt_has_attachment: bool
    _gt_jurisdiction: str    # US state code or "unknown"
    _gt_sol_years: int | None  # Statute of limitations in years
```

## Chokepoint invariant

**`_gt_*` fields MUST be stripped by `chokepoint.py` before any email is passed to Phase 2.**
The `test_chokepoint.py` test actively asserts this invariant holds for all 12 scenario types.

## Target volume

- Phase 1 M1: ≥ 100 emails, balanced across all 12 scenarios.
- At least 60% must be PI leads (reflects realistic intake distribution).
- At least 20% must include image/document attachments.
