"""
Schemas for synthetic email records.

RawEmailRecord contains hidden ground-truth labels (_gt_*).
PublicEmailRecord is the stripped version safe for the triage analyzer.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


GtClass = Literal["pi_lead", "general_legal", "spam", "invoice", "other"]
GtSeverity = Literal["low", "medium", "high", "critical"]
GtLiabilityClarity = Literal["clear", "unclear", "contested"]
GtScenario = Literal["car_accident", "slip_fall", "workplace", "medical", "other"]


class ImageAttachment(BaseModel):
    filename: str
    content_type: str = "image/jpeg"
    url: str
    license: str
    sha256: str


class PublicEmailRecord(BaseModel):
    """Email record with ground-truth labels stripped — safe for the triage app."""

    email_id: str
    subject: str
    body: str
    sender: str
    attachments: list[ImageAttachment] = Field(default_factory=list)


class RawEmailRecord(PublicEmailRecord):
    """Email record WITH hidden ground-truth labels. NEVER passed to the triage app."""

    _gt_class: GtClass
    _gt_severity: GtSeverity
    _gt_liability_clarity: GtLiabilityClarity
    _gt_scenario: GtScenario

    # Store gt fields as regular attributes (not private) so chokepoint can access them
    gt_class: GtClass
    gt_severity: GtSeverity
    gt_liability_clarity: GtLiabilityClarity
    gt_scenario: GtScenario
