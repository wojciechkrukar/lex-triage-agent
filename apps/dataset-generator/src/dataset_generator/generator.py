"""
Synthetic email generator.

Generates RawEmailRecord instances with ground-truth labels.
All emails are passed through chokepoint.strip_labels() before being exported.
"""

from __future__ import annotations

import random
import uuid
from typing import Iterator


def _make_uuid(rng: random.Random) -> str:
    """Generate a deterministic UUID from the seeded RNG."""
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))

from dataset_generator.chokepoint import strip_labels
from dataset_generator.image_manifest import get_images_for_scenario
from dataset_generator.schemas import GtClass, GtScenario, PublicEmailRecord, RawEmailRecord

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

_PI_SUBJECTS = [
    "I was injured in a car accident last week",
    "Slip and fall at grocery store — need legal help",
    "Workplace injury — forklift accident",
    "Injured by defective product",
    "Medical malpractice — wrong medication",
    "Hit by drunk driver, severe injuries",
    "Dog bite attack — need attorney",
    "Truck accident on I-95",
    "Construction site fall",
    "Rear-ended at stoplight — whiplash",
]

_PI_BODIES = [
    (
        "Dear Law Office,\n\nI was involved in a serious car accident on {date}. "
        "The other driver ran a red light and T-boned my vehicle. I suffered a broken arm "
        "and multiple lacerations. I have medical bills of approximately ${amount} so far. "
        "The other driver was cited for the violation. Please advise on my options.\n\n"
        "Regards,\n{name}"
    ),
    (
        "Hello,\n\nI slipped and fell at {store} on {date} due to a wet floor with no warning signs. "
        "I broke my wrist and have been unable to work for {weeks} weeks. "
        "The store manager was notified immediately. I have photos of the scene.\n\n"
        "Thank you,\n{name}"
    ),
    (
        "Good morning,\n\nI was injured at my workplace on {date}. A forklift operator "
        "struck me while I was in a designated pedestrian zone. I have a fractured pelvis "
        "and extensive soft tissue damage. Workers' comp has been filed but I believe "
        "the third-party contractor is also liable.\n\n{name}"
    ),
]

_SPAM_SUBJECTS = [
    "YOU HAVE WON $1,000,000 — CLAIM NOW",
    "Cheap Rolex watches — limited time offer",
    "URGENT: Your account needs verification",
    "Make money from home — guaranteed",
    "Nigerian prince needs your help",
    "Enlarge your practice instantly",
    "Free vacation — click here",
]

_SPAM_BODIES = [
    "Congratulations! You have been selected to receive a cash prize. Click here to claim.",
    "LIMITED TIME OFFER: Designer watches at 90% off. No questions asked shipping worldwide.",
    "Dear Friend, I am a prince from Nigeria and I need your assistance to transfer funds.",
]

_INVOICE_SUBJECTS = [
    "Invoice #INV-2024-0892 — Legal Research Services",
    "Invoice for January retainer fee",
    "Payment due: court reporter services",
    "Billing statement — expert witness fee",
]

_INVOICE_BODIES = [
    "Please find attached invoice #{inv} for services rendered during {month}. "
    "Total due: ${amount}. Payment terms: Net 30.",
    "This is a reminder that invoice #{inv} is due on {date}. "
    "Please remit payment to our billing department.",
]

_GENERAL_LEGAL_SUBJECTS = [
    "Contract review needed",
    "Employment dispute question",
    "Landlord-tenant issue",
    "Business formation inquiry",
    "Immigration question",
]

_GENERAL_LEGAL_BODIES = [
    "Dear Counsel,\n\nI have a contract that I would like you to review before signing. "
    "It is a commercial lease agreement for our new office space.\n\nThank you,\n{name}",
    "Hello,\n\nI am having a dispute with my employer regarding wrongful termination. "
    "Could you advise on my options?\n\n{name}",
]

_OTHER_SUBJECTS = [
    "Thank you for your service",
    "Holiday party invitation",
    "Updated firm directory",
    "New partner announcement",
    "Bar association newsletter",
]

_OTHER_BODIES = [
    "Please join us for the annual holiday party on December 15th at 6 PM.",
    "We are pleased to announce the addition of a new partner to our firm.",
]

# ---------------------------------------------------------------------------
# Senders
# ---------------------------------------------------------------------------

_FIRST_NAMES = ["James", "Maria", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda"]
_LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]


def _random_name(rng: random.Random) -> str:
    return f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"


def _random_email(rng: random.Random) -> str:
    name = _random_name(rng).lower().replace(" ", ".")
    return f"{name}@{rng.choice(_DOMAINS)}"


def _random_date(rng: random.Random) -> str:
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return f"2024-{month:02d}-{day:02d}"


# ---------------------------------------------------------------------------
# Generators per class
# ---------------------------------------------------------------------------

def _make_pi_lead(rng: random.Random) -> RawEmailRecord:
    scenario: GtScenario = rng.choice(["car_accident", "slip_fall", "workplace", "medical", "other"])
    name = _random_name(rng)
    body_template = rng.choice(_PI_BODIES)
    body = body_template.format(
        date=_random_date(rng),
        amount=rng.randint(5000, 150000),
        name=name,
        store=rng.choice(["Walmart", "Kroger", "Target", "Costco"]),
        weeks=rng.randint(2, 16),
    )
    attachments = get_images_for_scenario(scenario) if rng.random() < 0.4 else []
    severity = rng.choice(["low", "medium", "high", "critical"])
    liability = rng.choice(["clear", "unclear", "contested"])
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=rng.choice(_PI_SUBJECTS),
        body=body,
        sender=_random_email(rng),
        attachments=attachments,
        gt_class="pi_lead",
        gt_severity=severity,
        gt_liability_clarity=liability,
        gt_scenario=scenario,
    )


def _make_spam(rng: random.Random) -> RawEmailRecord:
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=rng.choice(_SPAM_SUBJECTS),
        body=rng.choice(_SPAM_BODIES),
        sender=f"noreply@{rng.choice(['spam.biz', 'promo.net', 'deals.xyz'])}",
        attachments=[],
        gt_class="spam",
        gt_severity="low",
        gt_liability_clarity="clear",
        gt_scenario="other",
    )


def _make_invoice(rng: random.Random) -> RawEmailRecord:
    body = rng.choice(_INVOICE_BODIES).format(
        inv=rng.randint(1000, 9999),
        month=rng.choice(["January", "February", "March"]),
        amount=rng.randint(500, 10000),
        date=_random_date(rng),
    )
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=rng.choice(_INVOICE_SUBJECTS),
        body=body,
        sender=f"billing@{rng.choice(['legalservices.com', 'courtreporters.net', 'expertwitness.org'])}",
        attachments=[],
        gt_class="invoice",
        gt_severity="low",
        gt_liability_clarity="clear",
        gt_scenario="other",
    )


def _make_general_legal(rng: random.Random) -> RawEmailRecord:
    name = _random_name(rng)
    body = rng.choice(_GENERAL_LEGAL_BODIES).format(name=name)
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=rng.choice(_GENERAL_LEGAL_SUBJECTS),
        body=body,
        sender=_random_email(rng),
        attachments=[],
        gt_class="general_legal",
        gt_severity="low",
        gt_liability_clarity="unclear",
        gt_scenario="other",
    )


def _make_other(rng: random.Random) -> RawEmailRecord:
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=rng.choice(_OTHER_SUBJECTS),
        body=rng.choice(_OTHER_BODIES),
        sender=f"info@{rng.choice(['lawfirm.com', 'barassociation.org', 'legalnetwork.net'])}",
        attachments=[],
        gt_class="other",
        gt_severity="low",
        gt_liability_clarity="clear",
        gt_scenario="other",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_CLASS_FACTORIES = {
    "pi_lead": _make_pi_lead,
    "spam": _make_spam,
    "invoice": _make_invoice,
    "general_legal": _make_general_legal,
    "other": _make_other,
}

# Distribution: ~40% PI leads, rest split among distractors
_CLASS_DISTRIBUTION: list[GtClass] = (
    ["pi_lead"] * 40
    + ["spam"] * 20
    + ["invoice"] * 15
    + ["general_legal"] * 15
    + ["other"] * 10
)


def generate_raw_emails(count: int = 100, seed: int = 42) -> list[RawEmailRecord]:
    """Generate `count` raw email records with ground-truth labels."""
    rng = random.Random(seed)
    classes = (_CLASS_DISTRIBUTION * (count // len(_CLASS_DISTRIBUTION) + 1))[:count]
    rng.shuffle(classes)
    return [_CLASS_FACTORIES[cls](rng) for cls in classes]


def generate_public_emails(count: int = 100, seed: int = 42) -> list[PublicEmailRecord]:
    """Generate stripped (no GT labels) email records safe for the triage app."""
    return [strip_labels(r) for r in generate_raw_emails(count, seed)]


def stream_public_emails(count: int = 100, seed: int = 42) -> Iterator[PublicEmailRecord]:
    """Stream stripped email records one at a time."""
    for record in generate_raw_emails(count, seed):
        yield strip_labels(record)
