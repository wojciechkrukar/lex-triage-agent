#!/usr/bin/env python3
"""
enrich_with_real_images.py

Downloads real public-domain accident images from Wikimedia, creates
RawEmailRecord entries with the image content embedded as base64, and writes
enriched records to the dataset files.

Outputs:
  out/emails_real_images.jsonl         — public (no GT labels)
  out/emails_real_images_gt.jsonl      — with GT labels (eval harness only)
  out/images/                          — image files saved locally

Decoy strategy: ~25% of enriched records are non-PI emails that also carry
image attachments, so the triage model cannot learn "image attachment → PI lead".

Usage:
  uv run --package dataset-generator python scripts/enrich_with_real_images.py [--out-dir apps/dataset-generator/out]
"""

from __future__ import annotations

import argparse
import random
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import requests

# Make sure the src package is on the path when running as a script.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dataset_generator.chokepoint import assert_no_gt_fields, strip_labels
from dataset_generator.image_downloader import DownloadResult, download_image, sha256_hex, to_b64
from dataset_generator.schemas import ImageAttachment, PublicEmailRecord, RawEmailRecord

# ---------------------------------------------------------------------------
# Wikimedia API helpers
# ---------------------------------------------------------------------------

_API_HEADERS = {
    "User-Agent": (
        "lex-triage-agent/1.0 (legal-email-triage dataset generator; "
        "educational synthetic data; non-commercial)"
    ),
}


def resolve_wikimedia_thumbs(filenames: list[str], width: int = 960) -> dict[str, str]:
    """
    Batch-query Wikimedia Commons API for thumbnail URLs.
    Returns {filename: thumb_url}.  Missing entries are omitted.
    """
    if not filenames:
        return {}
    titles = "|".join(f"File:{f}" for f in filenames)
    params = {
        "action": "query",
        "prop": "imageinfo",
        "iiprop": "url|thumburl",
        "iiurlwidth": width,
        "titles": titles,
        "format": "json",
    }
    try:
        resp = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers=_API_HEADERS,
            timeout=20,
        )
        data = resp.json()
    except Exception as e:
        print(f"  [WARNING] Wikimedia API error: {e}")
        return {}

    result: dict[str, str] = {}
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title", "")
        info = page.get("imageinfo", [{}])[0]
        thumb = info.get("thumburl", "")
        if thumb:
            # Store under bare filename (strip "File:" prefix)
            bare = title.removeprefix("File:").replace(" ", "_")
            result[bare] = thumb
    return result


# ---------------------------------------------------------------------------
# Image catalog
# Each entry defines one IMAGE + the email story wrapped around it.
# wiki_filename: bare filename on Wikimedia Commons (used for thumb lookup)
# direct_url:    non-Wikimedia or Special:FilePath fallback URL
# ---------------------------------------------------------------------------

_CATALOG: list[dict] = [
    # -------------------------------------------------------------------------
    # VEHICLE COLLISION
    # -------------------------------------------------------------------------
    {
        "wiki_filename": "Car_Accident_in_Sofia.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/d/d9/Car_Accident_in_Sofia.jpg",
        "filename": "car_accident_sofia.jpg",
        "license": "CC BY-SA 4.0",
        "scenario_ids": ["vehicle_collision_rear_end"],
        "description": (
            "Multi-vehicle rear-end collision on a city street; sedan with severely "
            "crumpled front hood and deployed airbag visible at the scene."
        ),
        "subject": "Car accident photos attached — need legal help urgently",
        "body": (
            "Dear Law Office,\n\n"
            "I am writing to seek legal representation following a serious car accident "
            "that occurred on {date}. A driver behind me failed to stop at a red light "
            "and rear-ended my vehicle at high speed.\n\n"
            "I have attached a photograph taken immediately after the collision. As you "
            "can see, the front-end damage is severe — the hood is completely crumpled "
            "and the airbag deployed on impact. I was taken by ambulance to the "
            "emergency room and diagnosed with whiplash and two fractured ribs.\n\n"
            "My medical bills are already over ${amount}. I have been unable to work for "
            "{weeks} weeks. The at-fault driver was issued a citation at the scene.\n\n"
            "Please advise on next steps.\n\nRespectfully,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "severe",
        "gt_liability_clarity": "clear",
        "gt_scenario": "vehicle_collision_rear_end",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 2,
    },
    {
        "wiki_filename": "Car_crash_at_night.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/8/86/Car_crash_at_night.jpg",
        "filename": "car_crash_night.jpg",
        "license": "CC BY 4.0",
        "scenario_ids": ["vehicle_collision_rear_end"],
        "description": (
            "Multi-vehicle crash at a street signal at night; man examines wreckage "
            "under streetlights; at least two cars involved."
        ),
        "subject": "Nighttime collision — photo evidence attached",
        "body": (
            "Hello,\n\n"
            "I was involved in a multi-vehicle accident on {date} at approximately 11 PM. "
            "I am attaching a photograph from the scene.\n\n"
            "The crash occurred at an intersection when a vehicle ran through a red light "
            "and struck my car. As the photo shows, there were multiple vehicles involved "
            "and the damage was extensive. I struck my head on the side window and have "
            "been experiencing persistent headaches and neck pain — my doctor suspects a "
            "concussion.\n\n"
            "I have ${amount} in medical costs so far and am off work. The police report "
            "is available upon request.\n\n"
            "Thank you,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "moderate",
        "gt_liability_clarity": "clear",
        "gt_scenario": "vehicle_collision_rear_end",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 2,
    },
    {
        "wiki_filename": "Japanese_car_accident.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Japanese_car_accident.jpg",
        "filename": "car_accident_intersection.jpg",
        "license": "CC BY-SA 2.0",
        "scenario_ids": ["vehicle_collision_rear_end"],
        "description": (
            "Front-to-side collision at an urban intersection; airbag deployed on "
            "driver side; significant structural damage to bonnet and door panel."
        ),
        "subject": "T-bone collision — photos and medical records attached",
        "body": (
            "Dear Counsel,\n\n"
            "I am reaching out regarding a serious intersection collision I was involved "
            "in on {date}. The attached photo shows the vehicle I was driving after impact.\n\n"
            "A second driver ran a stop sign and struck my vehicle driver-side. The airbag "
            "deployed. I suffered a dislocated shoulder and lacerations to my left arm. "
            "I have been in physical therapy for {weeks} weeks.\n\n"
            "Total medical expenses to date: ${amount}. I believe the other driver was "
            "entirely at fault. Two witnesses provided statements to police.\n\n"
            "Kind regards,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "severe",
        "gt_liability_clarity": "clear",
        "gt_scenario": "vehicle_collision_rear_end",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 2,
    },
    {
        "wiki_filename": "Toyota_car_accident_Japan.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Toyota_car_accident_Japan.jpg",
        "filename": "vehicle_front_damage.jpg",
        "license": "CC BY-SA 3.0",
        "scenario_ids": ["pedestrian_struck"],
        "description": (
            "Vehicle with significant front-end damage at a roadside; collapsed "
            "radiator grille and hood consistent with striking a pedestrian or fixed object."
        ),
        "subject": "I was hit by a car while in a crosswalk — seeking attorney",
        "body": (
            "Dear Law Office,\n\n"
            "I am a pedestrian who was struck by a vehicle on {date} while legally "
            "crossing in a marked crosswalk.\n\n"
            "I have attached a photo of the vehicle that struck me, taken by a bystander "
            "moments after the collision. The front-end damage is extensive, indicating "
            "the driver did not brake before impact. I was transported by ambulance with "
            "a fractured pelvis and torn ligaments in my left knee.\n\n"
            "I have been hospitalised for {weeks} weeks with bills exceeding ${amount}. "
            "The driver was cited for failure to yield. A traffic camera captured the "
            "incident.\n\n"
            "I would like to discuss my options for a personal-injury claim.\n\n"
            "Sincerely,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "catastrophic",
        "gt_liability_clarity": "clear",
        "gt_scenario": "pedestrian_struck",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 2,
    },
    # -------------------------------------------------------------------------
    # MEDICAL MALPRACTICE
    # -------------------------------------------------------------------------
    {
        "wiki_filename": "Cardiac_surgery_operating_room.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Cardiac_surgery_operating_room.jpg",
        "filename": "cardiac_surgery_or.jpg",
        "license": "CC BY-SA 4.0",
        "scenario_ids": ["medical_malpractice"],
        "description": (
            "Cardiac surgery operating room with surgical team, sterile draping, "
            "monitoring equipment, and open-chest procedure in progress."
        ),
        "subject": "Surgical error during cardiac procedure — seeking legal advice",
        "body": (
            "Dear Law Office,\n\n"
            "I am writing on behalf of my father who underwent cardiac bypass surgery "
            "on {date}. He suffered a preventable post-operative infection due to what "
            "we believe was a breach of sterile protocol.\n\n"
            "I have attached a photograph of the hospital's operating theatre taken during "
            "a pre-surgical walkthrough. My father developed a severe sternal wound "
            "infection that required a second surgery {weeks} weeks later. He is now "
            "disabled and unable to resume his normal life.\n\n"
            "We have documentation showing a nursing staff shortage on the day of the "
            "procedure. Total medical costs and lost income exceed ${amount}.\n\n"
            "Please advise on whether we have a viable malpractice claim.\n\n"
            "Regards,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "catastrophic",
        "gt_liability_clarity": "unclear",
        "gt_scenario": "medical_malpractice",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 2,
    },
    {
        "wiki_filename": "Oral_surgery_operating_room.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Oral_surgery_operating_room.jpg",
        "filename": "oral_surgery_or.jpg",
        "license": "CC BY-SA 4.0",
        "scenario_ids": ["medical_malpractice"],
        "description": (
            "Out-patient oral surgery room with surgical chair, instrument tray, "
            "overhead light, and sterile equipment."
        ),
        "subject": "Nerve damage after oral surgery — photo of facility attached",
        "body": (
            "Hello,\n\n"
            "I underwent a routine wisdom tooth extraction on {date} at a dental surgery "
            "centre. Following the procedure I experienced permanent numbness in my lower "
            "lip and chin, which my neurologist has diagnosed as permanent inferior "
            "alveolar nerve damage.\n\n"
            "I have attached a photo of the operating room where the procedure was "
            "performed. According to my specialist, this type of nerve injury is rare "
            "if proper imaging and surgical technique are followed.\n\n"
            "I have incurred ${amount} in specialist consultations and will require "
            "ongoing treatment. I have been off work for {weeks} weeks.\n\n"
            "Can you assess whether I have grounds for a negligence claim?\n\n"
            "Thank you,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "moderate",
        "gt_liability_clarity": "unclear",
        "gt_scenario": "medical_malpractice",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 2,
    },
    # -------------------------------------------------------------------------
    # CONSTRUCTION / WORKPLACE — long Wikimedia filename; use wiki_filename
    # -------------------------------------------------------------------------
    {
        "wiki_filename": (
            "W.B._Olson_Construction_workers_haulted_work_to_discuss_fall_safety_on_ladders_and_"
            "scaffolding_at_a_restoration_site_in_Evanston,_Ill._(14405917474).jpg"
        ),
        "original_url": (
            "https://upload.wikimedia.org/wikipedia/commons/8/81/"
            "W.B._Olson_Construction_workers_haulted_work_to_discuss_fall_safety_on_ladders_and_"
            "scaffolding_at_a_restoration_site_in_Evanston%2C_Ill._%2814405917474%29.jpg"
        ),
        "filename": "construction_scaffolding_evanston.jpg",
        "license": "CC BY 2.0",
        "scenario_ids": ["workplace_injury_construction"],
        "description": (
            "Construction workers on multi-story scaffolding at a restoration site in "
            "Evanston, IL, discussing ladder and fall safety; scaffolding lacks full "
            "guardrails on one side."
        ),
        "subject": "Fall from scaffolding — photo attached, need construction accident lawyer",
        "body": (
            "Dear Law Firm,\n\n"
            "I am a construction worker who fell from scaffolding on {date} at a "
            "restoration site in Illinois. I am attaching a photograph of the scaffolding "
            "setup at the time of the accident.\n\n"
            "As you can see in the photo, the scaffolding on one side lacked the required "
            "guardrails under OSHA 29 CFR 1926.502. I fell approximately 12 feet and "
            "sustained a fractured wrist, two broken ribs, and a herniated disc at L4-L5.\n\n"
            "The general contractor has workers' compensation coverage, but I believe the "
            "scaffolding subcontractor is also liable as a third party. My medical bills "
            "total ${amount} and I have been unable to work for {weeks} weeks.\n\n"
            "I would like to discuss both my workers' comp claim and any third-party "
            "negligence action available to me.\n\n"
            "Thank you,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "severe",
        "gt_liability_clarity": "contested",
        "gt_scenario": "workplace_injury_construction",
        "gt_jurisdiction": "IL",
        "gt_sol_years": 2,
    },
    # -------------------------------------------------------------------------
    # SLIP AND FALL — resolved via Wikimedia API
    # -------------------------------------------------------------------------
    {
        "wiki_filename": "Yellow_wet_floor_caution_sign_in_English.JPG",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Yellow_wet_floor_caution_sign_in_English.JPG",
        "filename": "wet_floor_sign.jpg",
        "license": "Public Domain",
        "scenario_ids": ["slip_fall_retail"],
        "description": (
            "Portable yellow plastic wet floor caution sign on a commercial tile floor; "
            "sign reads CAUTION WET FLOOR with slip-hazard pictogram."
        ),
        "subject": "Slip and fall at grocery store — evidence photos attached",
        "body": (
            "Hello,\n\n"
            "I am writing regarding a slip-and-fall accident at a {store} on {date}. "
            "I am attaching a photograph of the wet floor warning sign that was placed "
            "AFTER my fall — it was not present when I slipped on a large liquid spill "
            "near the produce section.\n\n"
            "I fell hard on my left side, fracturing my wrist and bruising my hip. The "
            "store manager acknowledged the spill had been unreported for over 20 minutes. "
            "A witness provided a written statement to store management.\n\n"
            "I have ${amount} in emergency room and orthopaedic bills and have been "
            "unable to perform my job for {weeks} weeks.\n\n"
            "Please let me know if you can take my case.\n\nThank you,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "moderate",
        "gt_liability_clarity": "clear",
        "gt_scenario": "slip_fall_retail",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 3,
    },
    {
        "wiki_filename": "Wet_floor_-_piso_mojado.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/1/18/Wet_floor_-_piso_mojado.jpg",
        "filename": "wet_floor_bilingual.jpg",
        "license": "CC BY 2.0",
        "scenario_ids": ["slip_fall_retail"],
        "description": (
            "Bilingual wet floor caution sign on a tile floor; reads CAUTION / PISO "
            "MOJADO; sign positioned in commercial building corridor."
        ),
        "subject": "Injury from fall in shopping mall — I need an attorney",
        "body": (
            "Dear Law Office,\n\n"
            "I am reaching out after suffering an injury from a fall at a shopping mall "
            "on {date}. I am attaching a photo of a wet floor sign — an identical sign "
            "was present at the scene but placed BEHIND a column and not visible from "
            "my direction of travel.\n\n"
            "I slipped on a freshly mopped floor and fell backwards, striking my head "
            "on a display stand. I was treated for a mild concussion and soft-tissue "
            "injuries to my lower back. My physician has recommended four weeks of "
            "physical therapy.\n\n"
            "My lost wages and medical costs total ${amount}. I have been off work for "
            "{weeks} weeks. Please advise on my options.\n\nSincerely,\n{name}"
        ),
        "gt_class": "pi_lead",
        "gt_severity": "moderate",
        "gt_liability_clarity": "clear",
        "gt_scenario": "slip_fall_retail",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": 3,
    },
    # -------------------------------------------------------------------------
    # DECOY — general_legal with image (non-PI)
    # -------------------------------------------------------------------------
    {
        "wiki_filename": "Business_agreement_handshake_at_coffee_shop.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Business_agreement_handshake_at_coffee_shop.jpg",
        "filename": "contract_signing.jpg",
        "license": "CC0",
        "scenario_ids": ["general_legal_contract"],
        "description": (
            "Two people shaking hands over a document at an office table; business "
            "agreement or contract signing."
        ),
        "subject": "Commercial lease review — contract photo attached for reference",
        "body": (
            "Dear Counsel,\n\n"
            "I am a small business owner looking to have a commercial lease agreement "
            "reviewed before signing. I have attached a photo of the signing ceremony "
            "from my previous lease to give you context on the parties involved.\n\n"
            "The new lease is for 3,200 sq ft of office space in downtown Chicago. "
            "The landlord has included several non-standard clauses around fit-out costs "
            "and early termination penalties that I am not comfortable with.\n\n"
            "Could you review the contract? I anticipate fairly straightforward work. "
            "Please let me know your hourly rate and availability.\n\nThank you,\n{name}"
        ),
        "gt_class": "general_legal",
        "gt_severity": "none",
        "gt_liability_clarity": "clear",
        "gt_scenario": "general_legal_contract",
        "gt_jurisdiction": "IL",
        "gt_sol_years": None,
    },
    # -------------------------------------------------------------------------
    # DECOY — spam with image (fake legal notice)
    # -------------------------------------------------------------------------
    {
        "wiki_filename": "Legal_Contract_&_Signature_-_Warm_Tones.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Legal_Contract_%26_Signature_-_Warm_Tones.jpg",
        "filename": "fake_legal_notice.jpg",
        "license": "CC BY 2.0",
        "scenario_ids": ["spam_solicitation"],
        "description": (
            "Close-up of a printed legal contract with a signature in warm-toned"
            " photography; used here as a fake legal notice attachment in spam."
        ),
        "subject": "URGENT: Legal Action Pending Against You — Document Attached",
        "body": (
            "DEAR RECIPIENT,\n\n"
            "You have been identified in a pending legal matter. Attached is a copy "
            "of the legal notice that has been filed against you. You MUST respond "
            "within 48 hours to avoid further action.\n\n"
            "To settle this matter immediately, click the link below and provide "
            "your personal details and bank account number for verification.\n\n"
            "Failure to respond will result in IMMEDIATE LEGAL PROCEEDINGS.\n\n"
            "Regards,\nLegal Enforcement Division"
        ),
        "gt_class": "spam",
        "gt_severity": "none",
        "gt_liability_clarity": "clear",
        "gt_scenario": "spam_solicitation",
        "gt_jurisdiction": "unknown",
        "gt_sol_years": None,
    },
    # -------------------------------------------------------------------------
    # DECOY — invoice with image
    # -------------------------------------------------------------------------
    {
        "wiki_filename": "GoldenGateBridge-001.jpg",
        "original_url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg",
        "filename": "invoice_property_photo.jpg",
        "license": "CC BY-SA 2.0",
        "scenario_ids": ["invoice_billing"],
        "description": (
            "Photograph attached to a property inspection invoice for a real estate "
            "valuation in the San Francisco Bay Area."
        ),
        "subject": "Invoice #INV-2026-0312 — Property Inspection Report Attached",
        "body": (
            "Dear Client,\n\n"
            "Please find attached Invoice #INV-2026-0312 for property inspection "
            "services rendered in connection with the {store} commercial property "
            "valuation completed on {date}.\n\n"
            "We have also included a site photograph for your records. "
            "Total invoice amount: ${amount}. Payment terms: Net 30.\n\n"
            "Please remit to our billing department. If you have any questions, "
            "do not hesitate to contact us.\n\n"
            "Kind regards,\n{name}\nInspection Services Division"
        ),
        "gt_class": "invoice",
        "gt_severity": "none",
        "gt_liability_clarity": "clear",
        "gt_scenario": "invoice_billing",
        "gt_jurisdiction": "CA",
        "gt_sol_years": None,
    },
]

# ---------------------------------------------------------------------------
# Template fill helpers
# ---------------------------------------------------------------------------

_FIRST_NAMES = ["James", "Maria", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda"]
_LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
_STORES = ["Walmart", "Kroger", "Target", "Costco", "Walgreens"]
_INJURIES = ["fractured wrist", "broken collarbone", "herniated disc", "torn ligament", "concussion"]


def _rng_name(rng: random.Random) -> str:
    return f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"


def _rng_email(rng: random.Random) -> str:
    name = _rng_name(rng).lower().replace(" ", ".")
    return f"{name}@{rng.choice(_DOMAINS)}"


def _rng_date(rng: random.Random) -> str:
    return f"2024-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"


def _fill_body(template: str, rng: random.Random) -> str:
    return template.format(
        date=_rng_date(rng),
        name=_rng_name(rng),
        amount=rng.randint(8000, 200000),
        weeks=rng.randint(2, 20),
        store=rng.choice(_STORES),
        injury=rng.choice(_INJURIES),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich dataset with real downloaded images")
    parser.add_argument("--out-dir", type=Path, default=Path("apps/dataset-generator/out"))
    parser.add_argument("--seed", type=int, default=99)
    parser.add_argument("--dry-run", action="store_true", help="Skip downloads, just report catalog")
    args = parser.parse_args()

    out_dir: Path = args.out_dir
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)

    # ------------------------------------------------------------------
    # Batch-resolve Wikimedia thumbnail URLs via the Commons API
    # ------------------------------------------------------------------
    wiki_filenames = [e["wiki_filename"] for e in _CATALOG if "wiki_filename" in e]
    print(f"Resolving {len(wiki_filenames)} Wikimedia thumbnails via API...", flush=True)
    thumb_map = resolve_wikimedia_thumbs(wiki_filenames)
    missing = [f for f in wiki_filenames if f not in thumb_map]
    if missing:
        print(f"  [WARNING] No thumb URL returned for: {missing}")
    print(f"  Resolved {len(thumb_map)} thumbnail URLs.\n")

    public_path = out_dir / "emails_real_images.jsonl"
    gt_path = out_dir / "emails_real_images_gt.jsonl"

    records_public: list[PublicEmailRecord] = []
    records_gt: list[RawEmailRecord] = []

    print(f"Processing {len(_CATALOG)} catalog entries...\n")

    for entry in _CATALOG:
        scenario = entry["gt_scenario"]
        filename = entry["filename"]

        # Determine download URL: prefer API thumb for Wikimedia files,
        # fall back to direct_url for Special:FilePath entries.
        wiki_fn = entry.get("wiki_filename")
        if wiki_fn:
            download_url: Optional[str] = thumb_map.get(wiki_fn)
            if not download_url:
                print(f"  [{scenario}] {filename} — no thumb URL, SKIPPED")
                continue
        else:
            download_url = entry["direct_url"]

        print(f"  [{scenario}] Downloading {filename}...", end=" ", flush=True)

        if args.dry_run:
            print("SKIP (dry-run)")
            continue

        result: DownloadResult | None = download_image(download_url)

        if result is None:
            print("FAILED — skipped")
            time.sleep(1)
            continue
        # Save image locally
        img_path = img_dir / filename
        img_path.write_bytes(result.data)

        sha = sha256_hex(result.data)
        b64 = to_b64(result.data)
        size_kb = len(result.data) // 1024

        print(f"OK  ({size_kb} KB, {result.content_type}, sha256={sha[:12]}…)")

        # Polite delay between Wikimedia requests to avoid rate-limiting
        time.sleep(2)

        attachment = ImageAttachment(
            filename=filename,
            content_type=result.content_type,
            url=entry["original_url"],
            license=entry["license"],
            sha256=sha,
            scenario_ids=entry["scenario_ids"],
            data_b64=b64,
            description=entry["description"],
        )

        email_id = str(uuid.uuid4())
        subject = entry["subject"]
        body = _fill_body(entry["body"], rng)
        sender_email = _rng_email(rng)

        raw = RawEmailRecord(
            email_id=email_id,
            subject=subject,
            body=body,
            sender=sender_email,
            attachments=[attachment],
            gt_class=entry["gt_class"],
            gt_severity=entry["gt_severity"],
            gt_liability_clarity=entry["gt_liability_clarity"],
            gt_scenario=entry["gt_scenario"],
            gt_has_attachment=True,
            gt_jurisdiction=entry["gt_jurisdiction"],
            gt_sol_years=entry["gt_sol_years"],
        )
        records_gt.append(raw)

        public = strip_labels(raw)
        assert_no_gt_fields(public)
        records_public.append(public)

    if args.dry_run:
        return

    # Write outputs
    with public_path.open("w") as f:
        for r in records_public:
            f.write(r.model_dump_json() + "\n")

    with gt_path.open("w") as f:
        for r in records_gt:
            f.write(r.model_dump_json() + "\n")

    pi_count = sum(1 for r in records_gt if r.gt_class == "pi_lead")
    decoy_count = sum(1 for r in records_gt if r.gt_class != "pi_lead")

    print(f"\n{'='*60}")
    print(f"Generated {len(records_public)} enriched email records")
    print(f"  PI leads with real accident images : {pi_count}")
    print(f"  Decoy (non-PI with images)         : {decoy_count}")
    print(f"Public  -> {public_path}")
    print(f"GT copy -> {gt_path}")
    print(f"Images  -> {img_dir}/")
    print(f"\nTo combine with the base dataset:")
    print(f"  cat {out_dir}/emails.jsonl {public_path} > {out_dir}/emails_combined.jsonl")


if __name__ == "__main__":
    main()
