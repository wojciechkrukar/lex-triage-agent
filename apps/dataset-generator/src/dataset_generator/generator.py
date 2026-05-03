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
from dataset_generator.schemas import GtClass, GtScenario, GtSeverity, PublicEmailRecord, RawEmailRecord

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

_SCENARIO_SUBJECTS: dict[str, list[str]] = {
    "vehicle_collision_rear_end": [
        "Rear-end collision — need personal injury attorney",
        "Car accident on {date} — seeking legal representation",
        "Whiplash injury after being rear-ended at stoplight",
    ],
    "slip_fall_retail": [
        "Slip and fall at {store} — need legal help",
        "Injured at retail store — wet floor, no warning signs",
        "Fall injury at grocery store — seeking compensation",
    ],
    "dog_bite": [
        "Dog bite attack — need attorney",
        "Serious dog bite injury — seeking legal advice",
        "Neighbor's dog attacked me — need representation",
    ],
    "medical_malpractice": [
        "Medical malpractice — wrong medication prescribed",
        "Surgical error caused serious injury — need attorney",
        "Doctor negligence — misdiagnosis led to further harm",
    ],
    "workplace_injury_construction": [
        "Construction site injury — seeking legal help",
        "Workplace accident — third-party contractor liability",
        "Injured on construction job — workers' comp and lawsuit",
    ],
    "defective_product": [
        "Injured by defective product — need attorney",
        "Product liability claim — device malfunctioned and hurt me",
        "Defective appliance caused burns — seeking compensation",
    ],
    "pedestrian_struck": [
        "Hit by car while crossing street — need legal help",
        "Pedestrian accident — serious injuries from vehicle strike",
        "Driver ran red light and struck me on foot — attorney needed",
    ],
    "premises_liability_staircase": [
        "Fell on broken staircase — premises liability claim",
        "Stairway collapse injury at apartment complex",
        "Injured on unsafe stairs — need legal representation",
    ],
    "ambiguous_pi_low_confidence": [
        "Not sure if I have a case — possible injury",
        "Maybe I need a lawyer — recent incident",
    ],
}

_SCENARIO_BODIES: dict[str, list[str]] = {
    "vehicle_collision_rear_end": [
        (
            "Dear Law Office,\n\nI was rear-ended at a stoplight on {date}. "
            "The other driver was clearly at fault and received a citation. "
            "I have been diagnosed with whiplash and a herniated disc. "
            "My medical bills are approximately ${amount} and growing. "
            "I have been unable to work for {weeks} weeks.\n\n"
            "Please advise on my options.\n\nRegards,\n{name}"
        ),
        (
            "Hello,\n\nOn {date} a driver rear-ended my vehicle at high speed on the highway. "
            "My car was totaled and I suffered a concussion and broken collarbone. "
            "The ER visit alone cost ${amount}. I have documentation of the accident "
            "and a police report. I would like to discuss filing a claim.\n\nThank you,\n{name}"
        ),
        (
            "Good morning,\n\nI was stopped at a traffic light on {date} when another vehicle "
            "struck my car from behind. My neck and back injuries have required physical therapy "
            "for {weeks} weeks. Total medical expenses have reached ${amount}. "
            "The at-fault driver's insurance company has already contacted me "
            "but I want independent legal counsel before I respond.\n\n{name}"
        ),
    ],
    "slip_fall_retail": [
        (
            "Hello,\n\nI slipped and fell at {store} on {date} due to a wet floor "
            "with no warning signs posted. I broke my wrist and have been unable "
            "to work for {weeks} weeks. The store manager was notified immediately "
            "and an incident report was filed. I have photos of the scene. "
            "Medical costs so far are ${amount}.\n\nThank you,\n{name}"
        ),
        (
            "Dear Attorney,\n\nOn {date} I was shopping at {store} when I slipped "
            "on a spilled liquid near the dairy aisle. There were no wet-floor cones visible. "
            "I fractured my hip and required surgery costing ${amount}. "
            "I have been off work for {weeks} weeks and face ongoing rehabilitation.\n\n{name}"
        ),
        (
            "Hello,\n\nI am reaching out regarding a fall I had at {store} on {date}. "
            "A display item was left in the walkway and I tripped over it, injuring my knee. "
            "I need surgery and my bills are already ${amount}. "
            "Several employees witnessed the incident. "
            "I would like to understand my legal options.\n\nSincerely,\n{name}"
        ),
    ],
    "dog_bite": [
        (
            "Dear Law Office,\n\nI was attacked by my neighbor's dog on {date} "
            "while walking in front of their property. The dog was off-leash and bit me "
            "on both arms, requiring stitches and reconstructive surgery. "
            "My medical expenses are ${amount}. I have been traumatized and missed "
            "{weeks} weeks of work. The animal control report is on file.\n\n"
            "Please contact me at your earliest convenience.\n\nThank you,\n{name}"
        ),
        (
            "Hello,\n\nOn {date} a dog at a local park attacked me without provocation. "
            "I suffered deep lacerations and a fractured finger. "
            "The owner was present and I have their information. "
            "Hospital bills total ${amount} and I may need follow-up surgery. "
            "I would like to pursue a personal injury claim.\n\n{name}"
        ),
        (
            "Good morning,\n\nI am a mail carrier and was bitten by a client's dog "
            "at their residence on {date}. The bite required an ER visit and {weeks} weeks "
            "of antibiotics plus wound care. Total medical cost: ${amount}. "
            "The dog had bitten a neighbor before — there is a prior incident report. "
            "I need legal advice on my options beyond workers' comp.\n\n{name}"
        ),
    ],
    "medical_malpractice": [
        (
            "Dear Counsel,\n\nI underwent surgery on {date} and the surgeon "
            "operated on the wrong vertebra, causing permanent nerve damage. "
            "I have been unable to work for {weeks} weeks and face lifetime care costs "
            "estimated at ${amount}. I have obtained my medical records "
            "and an independent medical review supports my claim.\n\nSincerely,\n{name}"
        ),
        (
            "Hello,\n\nMy physician prescribed the wrong medication on {date}, "
            "resulting in a severe adverse reaction that hospitalized me for two weeks. "
            "The attending ER doctor confirmed the prescribing error in writing. "
            "My medical bills are ${amount} to date and I am still not fully recovered "
            "after {weeks} weeks.\n\nPlease advise me on filing a malpractice claim.\n\n{name}"
        ),
        (
            "Good morning,\n\nI was misdiagnosed with a minor condition on {date} "
            "when in fact I had a serious infection that spread due to delayed treatment. "
            "The correct diagnosis came {weeks} weeks later after considerable deterioration. "
            "Additional treatment costs reached ${amount}. "
            "I believe the initial physician failed to order standard diagnostic tests.\n\n{name}"
        ),
        (
            "Dear Attorney,\n\nI underwent a routine procedure on {date} and developed "
            "a severe post-operative infection that my surgical team failed to diagnose "
            "for {weeks} weeks. By the time it was identified, it had spread systemically, "
            "requiring emergency re-hospitalization and IV antibiotics. "
            "Total treatment costs are ${amount}. I believe the delayed diagnosis is negligence.\n\n{name}"
        ),
        (
            "Hello,\n\nOn {date} I was administered anesthesia before a routine procedure. "
            "I regained awareness mid-surgery due to an incorrect dosage — "
            "a condition called anesthesia awareness. I am experiencing severe PTSD. "
            "Therapy and follow-up costs to date: ${amount}. I need representation against "
            "the anesthesiologist and the surgical center.\n\n{name}"
        ),
    ],
    "workplace_injury_construction": [
        (
            "Dear Law Office,\n\nI was injured at my construction worksite on {date}. "
            "A subcontractor's employee dropped equipment from scaffolding, "
            "striking me on the head and shoulder. I have a fractured clavicle "
            "and traumatic brain injury. Workers' comp has been filed but I believe "
            "the third-party subcontractor bears direct liability. "
            "Medical bills exceed ${amount}.\n\nRegards,\n{name}"
        ),
        (
            "Hello,\n\nOn {date} I fell through an unsecured floor opening at a "
            "construction site where I was working. OSHA was notified and cited the "
            "general contractor for safety violations. I have been off work for {weeks} weeks "
            "with spinal injuries requiring surgery. Total costs so far: ${amount}.\n\n{name}"
        ),
        (
            "Good morning,\n\nA crane malfunction on {date} caused a steel beam to swing "
            "and hit me while I was working in a designated safe zone. "
            "I suffered multiple broken ribs and a punctured lung. "
            "The incident report documents that the crane had failed a recent safety inspection. "
            "I have been out of work {weeks} weeks and bills are at ${amount}.\n\n{name}"
        ),
        (
            "Dear Law Office,\n\nI am an agricultural worker who was seriously injured on {date} "
            "when the tractor I was operating overturned in a drainage ditch. "
            "The tractor lacked a functioning ROPS (rollover protection structure) despite OSHA "
            "requirements. I suffered multiple rib fractures, a collapsed lung, and head injuries. "
            "I have been hospitalized for {weeks} weeks. Medical bills are ${amount}. "
            "Both the farm owner and the equipment lessor may bear liability.\n\n{name}"
        ),
        (
            "Hello,\n\nI was injured on {date} while performing cleanup inside a grain bin "
            "at the facility where I work. The required confined-space entry permit procedure "
            "was not followed — no attendant, no retrieval equipment, no air monitoring. "
            "I suffered crush injuries to my lower body requiring surgery costing ${amount}. "
            "I have been on disability for {weeks} weeks. A prior incident at the same facility "
            "was documented by OSHA two years ago.\n\n{name}"
        ),
        (
            "Good morning,\n\nOn {date} I was exposed to organophosphate pesticides while "
            "working on a farm. My employer provided no PPE and did not inform workers of "
            "the spraying schedule. I suffered acute pesticide poisoning requiring hospitalization. "
            "Treatment costs are ${amount} and I face potential long-term neurological effects. "
            "I have been unable to work for {weeks} weeks.\n\n{name}"
        ),
    ],
    "defective_product": [
        (
            "Dear Attorney,\n\nI purchased a power tool that malfunctioned on {date}, "
            "ejecting a fragment that struck my eye. I have lost partial vision in that eye "
            "and face ongoing treatment. My current medical bills are ${amount}. "
            "I have preserved the defective tool and have the original purchase receipt. "
            "I have been on disability for {weeks} weeks.\n\nThank you,\n{name}"
        ),
        (
            "Hello,\n\nAn electric space heater I bought caught fire on {date} "
            "while operating normally. I suffered second-degree burns on my hands and arms "
            "requiring hospitalization. The heater model has since been recalled. "
            "Medical expenses total ${amount}. I would like to pursue a product liability claim.\n\n{name}"
        ),
        (
            "Good morning,\n\nI was using a children's car seat when the harness buckle "
            "failed during a minor collision on {date}. My child was thrown forward "
            "and sustained a concussion and arm fractures. "
            "Total pediatric care costs are ${amount} and we have had {weeks} weeks "
            "of follow-up appointments. There are other reports of the same buckle failure online.\n\n{name}"
        ),
    ],
    "pedestrian_struck": [
        (
            "Dear Law Office,\n\nI was struck by a vehicle while crossing a marked "
            "crosswalk on {date}. The driver ran a red light at full speed. "
            "I suffered a broken pelvis, femur fracture, and internal bleeding. "
            "I have been hospitalized for {weeks} weeks with bills totaling ${amount}. "
            "The police report confirms the driver was at fault.\n\nSincerely,\n{name}"
        ),
        (
            "Hello,\n\nOn {date} I was hit by a reversing delivery truck in a parking lot "
            "while walking to my car. The driver did not check for pedestrians. "
            "I have a shattered ankle requiring surgery and extensive physical therapy. "
            "Medical costs so far: ${amount}. I missed {weeks} weeks of work.\n\n{name}"
        ),
        (
            "Good morning,\n\nI was jogging on the sidewalk on {date} when a car jumped "
            "the curb and hit me. The driver had been texting — witnesses confirmed this "
            "and it is noted in the police report. I have head trauma and a broken leg. "
            "My bills are ${amount} and rising. I need an attorney to handle my claim.\n\n{name}"
        ),
    ],
    "premises_liability_staircase": [
        (
            "Dear Attorney,\n\nI fell down a broken staircase at my apartment building "
            "on {date}. The handrail had been loose for months and I had complained "
            "to management in writing before the incident. I broke my ankle and tailbone. "
            "Medical bills are ${amount} and I have been unable to work for {weeks} weeks. "
            "I have written notice records sent to the landlord.\n\nThank you,\n{name}"
        ),
        (
            "Hello,\n\nWhile visiting a commercial office building on {date}, "
            "I slipped on a staircase where several steps had cracked tile "
            "and no non-slip strips were installed. I suffered a knee ligament tear "
            "requiring surgery costing ${amount}. I have documentation of prior complaints "
            "about that staircase.\n\n{name}"
        ),
        (
            "Good morning,\n\nI was injured at a hotel on {date} when a staircase railing "
            "gave way and I fell two floors. I am currently hospitalized with spinal injuries "
            "and the prognosis is uncertain. Initial medical bills alone are ${amount}. "
            "I have been informed I may face {weeks} weeks of inpatient rehabilitation. "
            "The hotel management has already attempted to have me sign a release form.\n\n{name}"
        ),
    ],
    "ambiguous_pi_low_confidence": [
        (
            "Hi,\n\nI had an incident recently and I'm not really sure if it qualifies "
            "for a lawyer. Something happened on {date} and I may have gotten hurt, "
            "but I haven't seen a doctor yet. I'm not sure who was at fault, if anyone. "
            "Just wanted to check if it's worth pursuing.\n\nThanks,\n{name}"
        ),
        (
            "Hello,\n\nI'm not sure if I need legal help. I was in a situation on {date} "
            "where I might have been injured. I don't have any medical records or bills yet. "
            "I'm not sure there's anything here, but a friend said I should reach out.\n\n{name}"
        ),
        (
            "Dear Sir/Madam,\n\nSomething happened to me recently and I'm not certain "
            "whether it was anyone's fault. I didn't feel great afterward but I'm not sure "
            "if it was related to the incident on {date}. I don't have documentation. "
            "Is this something you would even look at?\n\nRegards,\n{name}"
        ),
    ],
}

_SPAM_SUBJECTS = [
    "YOU HAVE WON $1,000,000 — CLAIM NOW",
    "Cheap Rolex watches — limited time offer",
    "URGENT: Your account needs verification",
    "Make money from home — guaranteed",
    "Nigerian prince needs your help",
    "Enlarge your practice instantly",
    "Free vacation — click here",
    "IRS NOTICE: Unpaid tax liability — take action NOW",
    "Your Social Security benefit is suspended",
    "CONGRATULATIONS — Final Winner: $850,000 lottery award",
    "Re: Class action settlement — you may be owed $$$",
    "URGENT: Your Microsoft account will be suspended in 24 hours",
    "Earn $5,000/week from home — no experience needed",
    "Medical alert: You qualify for a free knee brace",
    "Debt consolidation — reduce your payments by 60%",
    "UNCLAIMED INHERITANCE: You have been named as beneficiary",
    "Exclusive crypto investment — guaranteed 340% returns",
    "You may be eligible for a talcum powder class action",
    "Student loan forgiveness — application expires in 48 hours",
    "HELP!!",
    "question",
    "urgent",
    "hi",
    "please respond",
]

_SPAM_BODIES = [
    "Congratulations! You have been selected to receive a cash prize. Click here to claim.",
    "LIMITED TIME OFFER: Designer watches at 90% off. No questions asked shipping worldwide.",
    "Dear Friend, I am a prince from Nigeria and I need your assistance to transfer funds.",
    (
        "FINAL NOTICE FROM IRS COLLECTIONS DIVISION\n\n"
        "Your IRS Account has been flagged for unpaid tax liability of $4,302.00. "
        "Failure to respond within 24 hours will result in wage garnishment and asset seizure. "
        "Call 1-800-XXX-XXXX immediately to speak with an IRS agent.\n\n"
        "Do NOT ignore this notice."
    ),
    (
        "Dear Account Holder,\n\n"
        "Our records indicate unusual activity on your bank account. "
        "To prevent suspension, verify your identity by clicking the secure link below: "
        "http://secure-verify-account.net/verify\n\n"
        "Failure to verify within 48 hours will result in permanent account suspension."
    ),
    (
        "Congratulations!\n\n"
        "You have been randomly selected as our MONTHLY SWEEPSTAKES WINNER. "
        "Your prize: $850,000 USD will be transferred directly to your account. "
        "To claim, reply with your full name, mailing address, "
        "and a processing fee of $299 via Western Union."
    ),
    (
        "ATTENTION: Class Action Settlement Notice\n\n"
        "You may be entitled to compensation if you or a family member used Brand X medication "
        "between 2010 and 2020. Thousands of claimants have ALREADY received settlements "
        "averaging $14,500. NO out-of-pocket cost to you. "
        "Reply to claim your FREE case review."
    ),
    (
        "Exclusive invitation to our Crypto Wealth Program.\n\n"
        "Our AI-powered trading algorithm returned 340% over the last 12 months. "
        "Limited to 50 new members only. Minimum investment: $500. "
        "Results guaranteed or your money back.\n\nReply INVEST to reserve your spot."
    ),
    (
        "You may qualify for a FREE knee brace, back brace, or diabetic shoes "
        "at NO COST to you through Medicare. "
        "Call 1-888-XXX-XXXX to check your eligibility today. "
        "This offer expires in 72 hours."
    ),
    (
        "STUDENT LOAN FORGIVENESS UPDATE\n\n"
        "New federal programs have been approved. You may qualify for up to $20,000 in relief. "
        "Apply now before the deadline: studentloanrelief-gov.co/apply\nDeadline: 48 hours."
    ),
    (
        "UNCLAIMED ESTATE NOTICE\n\n"
        "You have been identified as a potential beneficiary of an unclaimed estate "
        "valued at $1.2 million. To proceed, our probate attorneys require verification "
        "of your identity and a nominal administration fee of $450.\n\n"
        "Reply with your date of birth and Social Security number to begin."
    ),
    (
        "Hi,\n\nI came across your firm online. I was recently injured and I think "
        "I might have a case but I'm not sure who to call. A friend said I should reach out "
        "to a lawyer but I don't know what kind. I'm not sure it's worth anything. "
        "Can someone call me back? I'll explain more when I talk to someone. Thanks"
    ),
]

_INVOICE_SUBJECTS = [
    "Invoice #INV-2024-0892 — Legal Research Services",
    "Invoice for January retainer fee",
    "Payment due: court reporter services",
    "Billing statement — expert witness fee",
    "Re: Q3 billing dispute — MTF Energy contract",
    "Outstanding balance: retainer services Q4 2024",
    "FWD: Accounts payable — overdue invoice 60+ days",
    "Statement of account — December 2024",
    "Reminder: Invoice #{inv} net 30 overdue",
    "Re: billing for deposition coverage",
    "Expense report attached — litigation support services",
    "Updated billing schedule for active matter",
    "Second notice: payment outstanding",
    "Invoice correction — revised total",
]

_INVOICE_BODIES = [
    "Please find attached invoice #{inv} for services rendered during {month}. "
    "Total due: ${amount}. Payment terms: Net 30.",
    "This is a reminder that invoice #{inv} is due on {date}. "
    "Please remit payment to our billing department.",
    (
        "Hi,\n\n"
        "Following up on invoice #{inv} sent last month. The balance of ${amount} "
        "remains outstanding as of today. Per our engagement letter, payment is due "
        "within thirty days. Please process by end of week "
        "or advise if there is a billing dispute.\n\nThanks,\nAccounts Receivable"
    ),
    (
        "Please see below for your monthly billing summary for {month}.\n\n"
        "  Legal research & drafting:          $3,400.00\n"
        "  Deposition transcript:              $1,200.00\n"
        "  Expert witness coordination:          $850.00\n"
        "  Administrative / copying:             $175.00\n"
        "  ─────────────────────────────────────────────\n"
        "  TOTAL DUE (#{inv}):              ${amount}\n\n"
        "Payment terms: Net 30. ACH and check accepted."
    ),
    (
        "Team,\n\n"
        "A couple of billing items before end of month:\n\n"
        "1. The Henderson deposition invoice came back disputed — client says they "
        "   never authorized the rush transcript. Please pull the engagement authorization "
        "   and follow up before the 15th.\n\n"
        "2. The Wilkins matter invoice #{inv} (${amount}) is now at 45 days. "
        "   Moving to collections if no response by Friday.\n\n"
        "3. Expert witness for the Garcia trial confirmed — fee schedule attached.\n\n"
        "— Billing"
    ),
    (
        "Dear Sir/Madam,\n\n"
        "Our records indicate no payment has been received for invoice #{inv} "
        "dated {date}, totaling ${amount}. This account is now {weeks} days past due.\n\n"
        "Please remit immediately to avoid referral to a collections agency. "
        "If you believe this is in error, please reply with documentation.\n\n"
        "Billing Department\nLex & Associates LLP"
    ),
    (
        "Hello,\n\nPlease find attached a revised invoice #{inv} for {month}. "
        "The previous version contained an error in the expert witness line item. "
        "Corrected total: ${amount}. We apologize for any inconvenience. "
        "Net 30 payment terms apply.\n\nBilling"
    ),
]

_GENERAL_LEGAL_SUBJECTS = [
    "Contract review needed",
    "Employment dispute question",
    "Landlord-tenant issue",
    "Business formation inquiry",
    "Immigration question",
    "Re: NDA for the Henderson acquisition",
    "Trademark registration — new brand name",
    "Vendor agreement renewal — need legal sign-off",
    "Subpoena received — what do we do?",
    "Non-compete question — ex-employee situation",
    "Re: settlement offer in the Williams matter",
    "Data breach notification requirement",
    "HOA dispute — can they really do this?",
    "Will and estate planning consultation",
    "Divorce and asset division question",
]

_GENERAL_LEGAL_BODIES = [
    "Dear Counsel,\n\nI have a contract that I would like you to review before signing. "
    "It is a commercial lease agreement for our new office space.\n\nThank you,\n{name}",
    "Hello,\n\nI am having a dispute with my employer regarding wrongful termination. "
    "Could you advise on my options?\n\n{name}",
    (
        "Hi,\n\nWe received a subpoena this morning regarding the Henderson matter. "
        "Nobody here is sure whether we need outside counsel or if in-house can handle it. "
        "Given the timeline (response due in 20 days), wanted to loop you in early. "
        "Can we set up a call this week?\n\nThanks,\n{name}"
    ),
    (
        "Hello,\n\nOne of our former sales managers just announced they are joining a "
        "direct competitor. They signed a non-compete agreement six months ago. "
        "I want to understand our options and whether it is enforceable in this state.\n\n{name}"
    ),
    (
        "Hi,\n\nWe are acquiring a small tech company and need a standard NDA drafted "
        "before the due diligence phase begins next week. "
        "Nothing complex — mutual confidentiality, two-year term, standard carve-outs. "
        "Can your team turn this around in 48 hours?\n\nBest,\n{name}"
    ),
    (
        "Good afternoon,\n\nI am a small business owner and my landlord is threatening to "
        "evict me for alleged lease violations I do not believe are valid. "
        "The lease expires in 8 months and I have been a tenant for 6 years with no prior issues. "
        "I would like to understand my rights before responding to their notice.\n\n{name}"
    ),
    (
        "Dear Attorney,\n\nI received a settlement offer of $18,500 from the opposing party "
        "in our ongoing contract dispute. My exposure if we go to trial is uncertain. "
        "I would like a second opinion on whether to accept or continue litigating.\n\n{name}"
    ),
    (
        "Hello,\n\nMy mother passed away last month without a formal will. "
        "She had real estate and several bank accounts. My siblings and I do not agree "
        "on how to divide the estate. I would like to understand what probate looks like "
        "in this state and whether we need an attorney to proceed.\n\n{name}"
    ),
]

_OTHER_SUBJECTS = [
    "Thank you for your service",
    "Holiday party invitation",
    "Updated firm directory",
    "New partner announcement",
    "Bar association newsletter",
    "Continuing legal education schedule",
    "Office closure — Memorial Day",
    "Firm retreat — September dates",
    "Welcome our new paralegal",
    "IT maintenance window this Saturday",
]

_OTHER_BODIES = [
    "Please join us for the annual holiday party on December 15th at 6 PM.",
    "We are pleased to announce the addition of a new partner to our firm.",
    "The firm will be closed on Memorial Day, May 27th. All urgent matters should be "
    "addressed before the holiday weekend.",
    "Reminder: Q3 CLE credits are due by December 31st. "
    "Please submit your certificates to HR no later than December 15th.",
    "Please welcome Sarah Chen, our new paralegal, who joins us from Kirkland & Ellis. "
    "Sarah will be supporting the litigation team starting Monday.",
]

# ---------------------------------------------------------------------------
# Senders
# ---------------------------------------------------------------------------

_FIRST_NAMES = [
    "James", "Maria", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "Carlos", "Aisha", "Wei", "Fatima", "Dmitri", "Elena", "Jamal", "Sofia",
    "Thomas", "Angela", "Kevin", "Brenda", "Marcus", "Yuki", "Hector", "Denise",
    "Samuel", "Rosa", "Nathan", "Priya", "Derek", "Ingrid",
]
_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
]
_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]

# ---------------------------------------------------------------------------
# Noise engineering
# ---------------------------------------------------------------------------

def _inject_typos(rng: random.Random, text: str, count: int = 2) -> str:
    """Randomly swap / drop / double letters inside words (simulates rushed typing)."""
    words = text.split()
    if len(words) < 5:
        return text
    for _ in range(count):
        idx = rng.randint(2, len(words) - 2)
        word = words[idx]
        if len(word) > 3 and word.isalpha():
            op = rng.choice(["swap", "drop", "double"])
            i = rng.randint(1, len(word) - 2)
            if op == "swap":
                w = list(word)
                w[i], w[i + 1] = w[i + 1], w[i]
                word = "".join(w)
            elif op == "drop":
                word = word[:i] + word[i + 1 :]
            else:
                word = word[:i] + word[i] + word[i:]
            words[idx] = word
    return " ".join(words)


def _apply_realistic_noise(
    rng: random.Random,
    subject: str,
    body: str,
    *,
    noise_prob: float = 0.20,
) -> tuple[str, str]:
    """Apply real-world distortion at *noise_prob* probability.

    Distortions (each applied independently with lower sub-probability):
    - Vague subject override ("HELP!!", "question", "urgent", …)
    - ALL-CAPS rage section in the body
    - Letter-level typos
    """
    if rng.random() >= noise_prob:
        return subject, body

    # Vague subject (40% of noisy emails)
    if rng.random() < 0.40:
        subject = rng.choice([
            "HELP!!!", "help", "question", "urgent", "need advice",
            "please respond", "URGENT MATTER", "hi", "question for you",
            "calling about my situation", "re: my issue", "please call me",
        ])

    # ALL-CAPS rant on one line (25% of noisy emails)
    if rng.random() < 0.25:
        lines = [ln for ln in body.split("\n") if ln.strip()]
        if lines:
            rage = rng.choice(lines)
            body = body.replace(rage, rage.upper(), 1)

    # Typos (30% of noisy emails)
    if rng.random() < 0.30:
        body = _inject_typos(rng, body, count=rng.randint(1, 3))

    return subject, body


# ---------------------------------------------------------------------------
# Urgency computation
# ---------------------------------------------------------------------------

_URGENCY_RANGE: dict[tuple[str, str], tuple[int, int]] = {
    ("pi_lead", "catastrophic"): (9, 10),
    ("pi_lead", "severe"):       (7, 9),
    ("pi_lead", "moderate"):     (5, 7),
    ("pi_lead", "minor"):        (3, 5),
    ("pi_lead", "none"):         (2, 4),
    ("spam", "none"):            (1, 2),
    ("invoice", "none"):         (1, 3),
    ("general_legal", "none"):   (2, 4),
    ("other", "none"):           (1, 2),
}


def _urgency(rng: random.Random, gt_class: str, gt_severity: str) -> int:
    lo, hi = _URGENCY_RANGE.get((gt_class, gt_severity), (1, 3))
    return rng.randint(lo, hi)


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
# Scenario / jurisdiction data
# ---------------------------------------------------------------------------

_PI_SCENARIOS: list[GtScenario] = [
    "vehicle_collision_rear_end",
    "slip_fall_retail",
    "dog_bite",
    "medical_malpractice",
    "workplace_injury_construction",
    "defective_product",
    "pedestrian_struck",
    "premises_liability_staircase",
    "ambiguous_pi_low_confidence",
]

_US_JURISDICTIONS = ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI"]

# PI statutes of limitations vary 2–3 years across most US states (simplified)
_PI_SOL_YEARS = [2, 3]

# ---------------------------------------------------------------------------
# Generators per class
# ---------------------------------------------------------------------------

def _make_pi_lead(rng: random.Random) -> RawEmailRecord:
    scenario: GtScenario = rng.choice(_PI_SCENARIOS)
    name = _random_name(rng)
    body_template = rng.choice(_SCENARIO_BODIES[scenario])
    body = body_template.format(
        date=_random_date(rng),
        amount=rng.randint(5000, 150000),
        name=name,
        store=rng.choice(["Walmart", "Kroger", "Target", "Costco", "Home Depot", "Walgreens"]),
        weeks=rng.randint(2, 16),
    )
    subject = rng.choice(_SCENARIO_SUBJECTS[scenario])
    subject, body = _apply_realistic_noise(rng, subject, body, noise_prob=0.18)
    attachments = get_images_for_scenario(scenario) if rng.random() < 0.50 else []
    severity: GtSeverity = rng.choice(["minor", "moderate", "severe", "catastrophic"])
    liability = rng.choice(["clear", "unclear", "contested"])
    jurisdiction = rng.choice(_US_JURISDICTIONS)
    sol_years = rng.choice(_PI_SOL_YEARS)
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=subject,
        body=body,
        sender=_random_email(rng),
        attachments=attachments,
        gt_class="pi_lead",
        gt_severity=severity,
        gt_liability_clarity=liability,
        gt_scenario=scenario,
        gt_has_attachment=bool(attachments),
        gt_jurisdiction=jurisdiction,
        gt_sol_years=sol_years,
        gt_urgency=_urgency(rng, "pi_lead", severity),
    )


def _make_spam(rng: random.Random) -> RawEmailRecord:
    subject = rng.choice(_SPAM_SUBJECTS)
    body = rng.choice(_SPAM_BODIES)
    subject, body = _apply_realistic_noise(rng, subject, body, noise_prob=0.30)
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=subject,
        body=body,
        sender=f"noreply@{rng.choice(['spam.biz', 'promo.net', 'deals.xyz', 'alerts.co', 'notify.info'])}",
        attachments=[],
        gt_class="spam",
        gt_severity="none",
        gt_liability_clarity="clear",
        gt_scenario="spam_solicitation",
        gt_has_attachment=False,
        gt_jurisdiction="unknown",
        gt_sol_years=None,
        gt_urgency=_urgency(rng, "spam", "none"),
    )


def _make_invoice(rng: random.Random) -> RawEmailRecord:
    body = rng.choice(_INVOICE_BODIES).format(
        inv=rng.randint(1000, 9999),
        month=rng.choice(["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]),
        amount=rng.randint(500, 10000),
        date=_random_date(rng),
        weeks=rng.randint(30, 90),
        name=_random_name(rng),
    )
    subject = rng.choice(_INVOICE_SUBJECTS).format(inv=rng.randint(1000, 9999))
    subject, body = _apply_realistic_noise(rng, subject, body, noise_prob=0.10)
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=subject,
        body=body,
        sender=f"billing@{rng.choice(['legalservices.com', 'courtreporters.net', 'expertwitness.org', 'legalfees.biz', 'invoices.law'])}",
        attachments=[],
        gt_class="invoice",
        gt_severity="none",
        gt_liability_clarity="clear",
        gt_scenario="invoice_billing",
        gt_has_attachment=False,
        gt_jurisdiction="unknown",
        gt_sol_years=None,
        gt_urgency=_urgency(rng, "invoice", "none"),
    )


def _make_general_legal(rng: random.Random) -> RawEmailRecord:
    name = _random_name(rng)
    body = rng.choice(_GENERAL_LEGAL_BODIES).format(name=name)
    subject = rng.choice(_GENERAL_LEGAL_SUBJECTS)
    subject, body = _apply_realistic_noise(rng, subject, body, noise_prob=0.12)
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=subject,
        body=body,
        sender=_random_email(rng),
        attachments=[],
        gt_class="general_legal",
        gt_severity="none",
        gt_liability_clarity="unclear",
        gt_scenario="general_legal_contract",
        gt_has_attachment=False,
        gt_jurisdiction="unknown",
        gt_sol_years=None,
        gt_urgency=_urgency(rng, "general_legal", "none"),
    )


def _make_other(rng: random.Random) -> RawEmailRecord:
    return RawEmailRecord(
        email_id=_make_uuid(rng),
        subject=rng.choice(_OTHER_SUBJECTS),
        body=rng.choice(_OTHER_BODIES),
        sender=f"info@{rng.choice(['lawfirm.com', 'barassociation.org', 'legalnetwork.net'])}",
        attachments=[],
        gt_class="other",
        gt_severity="none",
        gt_liability_clarity="clear",
        gt_scenario="general_legal_contract",
        gt_has_attachment=False,
        gt_jurisdiction="unknown",
        gt_sol_years=None,
        gt_urgency=_urgency(rng, "other", "none"),
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

# M1 distribution: ≥60% PI leads (required by test suite's M1 exit-criteria gates)
_DIST_M1: list[GtClass] = (
    ["pi_lead"] * 60
    + ["spam"] * 15
    + ["invoice"] * 10
    + ["general_legal"] * 10
    + ["other"] * 5
)

# Realistic distribution: 30% PI / 70% noise (matches real law-firm inbox)
# Use with --realistic-split CLI flag for the 5 000-record demo dataset.
_DIST_REALISTIC: list[GtClass] = (
    ["pi_lead"] * 30
    + ["spam"] * 25
    + ["invoice"] * 25
    + ["general_legal"] * 15
    + ["other"] * 5
)

# Alias kept for backward-compat; default stays at M1 so all CI tests pass
_CLASS_DISTRIBUTION = _DIST_M1


def generate_raw_emails(
    count: int = 100,
    seed: int = 42,
    realistic_split: bool = False,
) -> list[RawEmailRecord]:
    """Generate `count` raw email records with ground-truth labels.

    Args:
        count: Number of emails to generate.
        seed: Random seed for reproducibility.
        realistic_split: When True, use the 30/70 PI/noise distribution that
            mirrors a real inbox (demo mode).  When False (default), use the
            60% PI distribution required by M1 exit-criteria tests.
    """
    rng = random.Random(seed)
    dist = _DIST_REALISTIC if realistic_split else _DIST_M1
    classes = (dist * (count // len(dist) + 1))[:count]
    rng.shuffle(classes)
    return [_CLASS_FACTORIES[cls](rng) for cls in classes]


def generate_public_emails(
    count: int = 100,
    seed: int = 42,
    realistic_split: bool = False,
) -> list[PublicEmailRecord]:
    """Generate stripped (no GT labels) email records safe for the triage app."""
    return [strip_labels(r) for r in generate_raw_emails(count, seed, realistic_split)]


def stream_public_emails(
    count: int = 100,
    seed: int = 42,
    realistic_split: bool = False,
) -> Iterator[PublicEmailRecord]:
    """Stream stripped email records one at a time."""
    for record in generate_raw_emails(count, seed, realistic_split):
        yield strip_labels(record)
