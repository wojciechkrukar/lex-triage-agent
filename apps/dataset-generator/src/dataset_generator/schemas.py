"""
Schemas for synthetic email records.

RawEmailRecord contains hidden ground-truth labels (_gt_*).
PublicEmailRecord is the stripped version safe for the triage analyzer.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


GtClass = Literal["pi_lead", "general_legal", "spam", "invoice", "other"]
GtSeverity = Literal["none", "minor", "moderate", "severe", "catastrophic"]
GtLiabilityClarity = Literal["clear", "unclear", "contested"]
GtScenario = Literal[
    "vehicle_collision_rear_end",   # S01
    "slip_fall_retail",             # S02
    "dog_bite",                     # S03
    "medical_malpractice",          # S04
    "workplace_injury_construction", # S05
    "defective_product",            # S06
    "pedestrian_struck",            # S07
    "premises_liability_staircase", # S08
    "general_legal_contract",       # S09
    "invoice_billing",              # S10
    "spam_solicitation",            # S11
    "ambiguous_pi_low_confidence",  # S12
]


class ImageAttachment(BaseModel):
    filename: str
    content_type: str = "image/jpeg"
    url: str
    license: str
    sha256: str
    scenario_ids: list[str] = Field(default_factory=list)
    # Populated after downloading the image locally
    data_b64: str = ""          # base64-encoded image bytes (640px thumbnail)
    description: str = ""       # human-readable description of what the image shows


class PublicEmailRecord(BaseModel):
    """Email record with ground-truth labels stripped — safe for the triage app."""

    email_id: str
    subject: str
    body: str
    sender: str
    attachments: list[ImageAttachment] = Field(default_factory=list)


class RawEmailRecord(PublicEmailRecord):
    """Email record WITH hidden ground-truth labels. NEVER passed to the triage app."""

    # Store gt fields as regular attributes so chokepoint can access and strip them
    gt_class: GtClass
    gt_severity: GtSeverity
    gt_liability_clarity: GtLiabilityClarity
    gt_scenario: GtScenario
    gt_has_attachment: bool = False
    gt_jurisdiction: str = "unknown"
    gt_sol_years: int | None = None
    gt_urgency: int = 5  # 1 (low) – 10 (extreme); derived from class + severity
