# Dataset Data Sources & Compliance

> This document is the authoritative record of every external data source used
> (or referenced) in this project.  It exists specifically to answer audit and
> compliance questions — including HIPAA — and must be updated whenever a new
> source is introduced.

---

## 1. HIPAA Position Statement

**All patient-facing content in this system is 100% synthetic.**

No real patient, provider, claimant, attorney, or case is represented anywhere
in this dataset.  Every email body, name, sender address, dollar amount, date,
and injury description was generated algorithmically using the templates in
`apps/dataset-generator/src/dataset_generator/generator.py`.

Under the HIPAA Privacy Rule (45 CFR Part 164), the system processes **no
Protected Health Information (PHI)**.  The demonstration dataset is not derived
from, and does not contain, any of the 18 PHI identifiers listed in
45 CFR § 164.514(b)(2).

If medical images are sourced for attachment simulation (see §5 below), they
come exclusively from **de-identified, open-access** repositories as detailed
in that section.

---

## 2. Synthetic Email Text

| Generator | Location | Method |
|-----------|----------|--------|
| Email bodies | `apps/dataset-generator/src/dataset_generator/generator.py` | Template-based Python `str.format()` with seeded `random.Random` |
| Scenario taxonomy | `apps/dataset-generator/src/dataset_generator/schemas.py` | Hand-authored type literals; no external corpus |
| Ground-truth labels | `apps/dataset-generator/src/dataset_generator/chokepoint.py` | Injected deterministically; stripped before export |

**Seed reproducibility:** All generation runs use `--seed` (default 42).
The output of any run can be exactly reproduced by re-running with the same
`--count` and `--seed`.

---

## 3. Background Noise Inspiration

The following public datasets were studied to understand the **tone, structure,
and vocabulary** of realistic noise email classes.  **No text from these
datasets was copied into the generator.** They informed only the template style.

### 3.1 Enron Email Dataset (Billing / Corporate Noise)

| Field | Value |
|-------|-------|
| URL | https://www.cs.cmu.edu/~enron/ |
| Description | ~500 k internal Enron Corp emails released via FERC/DOJ in 2001 |
| License | Public domain (produced via government legal process) |
| Usage | Informed tone, subject-line style, and billing dispatch patterns for the `invoice` and `general_legal` noise classes |
| PHI | None; no patient data present |

### 3.2 UCI SpamBase Dataset (Spam / Marketing Noise)

| Field | Value |
|-------|-------|
| URL | https://archive.ics.uci.edu/dataset/94/spambase |
| Description | 4 601 labeled spam/non-spam email feature vectors from Hewlett-Packard Labs |
| License | CC BY 4.0 |
| Usage | Informed vocabulary distribution and structural features used in the `spam_solicitation` scenario templates |
| PHI | None; feature-vector representation only, no full email bodies |

---

## 4. Legal Reasoning Vocabulary

### 4.1 LegalBench (Hugging Face)

| Field | Value |
|-------|-------|
| URL | https://huggingface.co/datasets/nguha/legalbench |
| Paper | Guha et al., "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models" (NeurIPS 2023) |
| License | CC BY 4.0 |
| Usage | Informed legal terminology, cause-of-action vocabulary, and representative phrasing used in PI scenario templates and classification prompt design |
| PHI | None; law school benchmark tasks |

---

## 5. Accident Scenario Seeds (AgInjuryNews)

| Field | Value |
|-------|-------|
| URL | http://aginjurynews.org/ |
| Description | News aggregator for agricultural and occupational injury incidents across the US |
| License | News articles (fair use / public interest); **no text reproduced** |
| Usage | Informed realistic accident types added to the `workplace_injury_construction` scenario: tractor rollovers, grain-bin engulfments, pesticide exposure, PTO shaft entanglements.  Specific article text was **not** copied; scenario body templates were independently authored. |
| PHI | None; journalism, not medical records |

---

## 6. Medical & Radiology Images (ROCO Dataset)

> **Default state: DISABLED.**  Medical imaging integration requires
> `ENABLE_ROCO_IMAGES=true` and installation of the `datasets` package.

| Field | Value |
|-------|-------|
| Dataset name | Radiology Objects in COntext (ROCO) |
| Citation | Pelka O, Koitka S, Rückert CM, Nensa F, Friedrich CM. *Radiology Objects in COntext (ROCO): A Multimodal Image Dataset.* MICCAI Workshop LABELS 2018. DOI: 10.1007/978-3-030-01364-6\_20 |
| PMC article | https://pmc.ncbi.nlm.nih.gov/articles/PMC11208523/ |
| HuggingFace | https://huggingface.co/datasets/robailleo/medical-imaging-combined |
| Kaggle mirror | https://www.kaggle.com/datasets/virajbagal/roco-dataset |
| Source corpus | PubMed Central (PMC) open-access articles |
| License | CC BY 4.0 (inherited from PMC open-access terms) |
| De-identification | **De-identified by the original journal publishers prior to PMC indexing.** The ROCO authors performed additional filtering; no faces, names, or 18-identifier PHI fields (45 CFR § 164.514) are present in the published dataset. |
| Our usage | Referenced via `MedicalImagingProvider` class in `image_manifest.py`.  When enabled, image stubs are attached to synthetic `medical_malpractice` and `defective_product` emails to simulate multimodal attachments in the demo. The de-identified images are never paired with real patient data. |
| PHI risk assessment | **Negligible.** Source images are radiological figures from published academic papers; de-identified before publication; no re-identification pathway exists in our processing pipeline. |

---

## 7. General-Purpose Photograph Images (Wikimedia Commons)

Photos attached to simulated emails (vehicle crashes, wet-floor signs, etc.)
are sourced from Wikimedia Commons.  Each image in the manifest is recorded
with its license in
`apps/dataset-generator/src/dataset_generator/image_manifest.py`.

All selected images are published under:
- **CC0 / Public Domain**
- **CC BY 2.0 / 3.0 / 4.0**
- **CC BY-SA 2.0 / 3.0 / 4.0**

None of the Wikimedia images contain identifiable faces or PHI.

---

## 8. Real-Image Enrichment Samples (12 Emails)

The 12 records in `out/emails_real_images.jsonl` were produced by
`scripts/enrich_with_real_images.py`, which downloads thumbnails from
Wikimedia Commons via the MediaWiki API.  Licenses and filenames are recorded
per-entry in the JSONL and inline in the script.

No external image database beyond Wikimedia Commons was accessed during
enrichment.

---

## 9. Compliance Summary Table

| Concern | Mitigation | Status |
|---------|-----------|--------|
| HIPAA PHI in email bodies | 100% synthetic text, no real names/dates/case numbers | ✅ Compliant |
| HIPAA PHI in attached images | ROCO images de-identified by publishers; Wikimedia images are public photos without PHI | ✅ Compliant |
| Copyright in email templates | All templates independently authored; no text copied from external corpora | ✅ Compliant |
| Copyright in attached images | All images carry CC BY / CC0 licenses; attribution recorded in manifest | ✅ Compliant |
| Right-to-be-forgotten (GDPR) | No real individuals; synthetic personas cannot be subject of erasure requests | ✅ N/A |
| Data minimization | Ground-truth labels are stripped via `chokepoint.py` before any export to the triage app | ✅ By design |

---

## 10. Contact & Version

| Field | Value |
|-------|-------|
| Document owner | Director Agent / Project Maintainer |
| Last updated | 2026-05-01 |
| Schema version | Phase 1 v1.0 |

Questions about data provenance should be directed to the project maintainer.
Additions to this document are required before any new external data source
is integrated into the pipeline.
