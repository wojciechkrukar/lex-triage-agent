"""
Chokepoint — the ONLY place that may access ground-truth label fields.

Rules (enforced by tests):
1. strip_labels() MUST remove all gt_* fields from any dict.
2. No other module may read gt_* fields.
3. strip_labels() MUST be called before any email record is written to out/.
"""

from __future__ import annotations

import copy

from dataset_generator.schemas import PublicEmailRecord, RawEmailRecord

_GT_FIELDS = frozenset({
    "gt_class", "gt_severity", "gt_liability_clarity", "gt_scenario",
    "gt_has_attachment", "gt_jurisdiction", "gt_sol_years", "gt_urgency",
})


def strip_labels(record: RawEmailRecord) -> PublicEmailRecord:
    """Remove all ground-truth label fields and return a PublicEmailRecord."""
    data = record.model_dump()
    for field in _GT_FIELDS:
        data.pop(field, None)
    return PublicEmailRecord(**data)


def strip_labels_dict(record: dict) -> dict:
    """Strip ground-truth label fields from a raw dict (for bulk operations)."""
    result = copy.deepcopy(record)
    for field in _GT_FIELDS:
        result.pop(field, None)
    return result


def assert_no_gt_fields(record: dict | PublicEmailRecord) -> None:
    """Raise AssertionError if any gt_* field is present. Used in tests."""
    if isinstance(record, PublicEmailRecord):
        data = record.model_dump()
    else:
        data = record
    leaked = _GT_FIELDS.intersection(data.keys())
    if leaked:
        raise AssertionError(f"Ground-truth fields leaked into public record: {leaked}")
