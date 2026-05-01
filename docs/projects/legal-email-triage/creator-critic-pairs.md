# Creator-Critic Pairs

## Overview

The system uses the Creator-Critic pattern for the Legal Appraisal step. A Creator drafts an appraisal memo; a Critic (Legal Advisor) scores it. Iteration continues until the score exceeds the threshold or the maximum iteration count is reached.

## Pair: Legal Appraisal

| Role | Node | Model (tier1) | Threshold |
|------|------|--------------|-----------|
| Creator | `appraisal_creator` | Claude Opus 4.7 | — |
| Critic | `legal_advisor` | Claude Opus 4.7 | score ≥ 0.65 |

### Pairing contract

1. Creator receives `EmailTriageState` (including `vision_summary` if available).
2. Creator produces `appraisal_draft` — a structured legal memo covering:
   - Incident summary
   - Liability indicators
   - Severity assessment
   - Statute-of-limitations cues
   - Jurisdiction flags
   - Recommended next action
3. Critic receives draft and scores on four dimensions (0–1 each):
   - Liability clarity
   - Severity accuracy
   - SoL completeness
   - Jurisdiction flags
4. `appraisal_score` = weighted average (weights: 0.3, 0.3, 0.2, 0.2).
5. If score ≥ 0.65: advance to HITL gate.
6. If score < 0.65: return to Creator with `appraisal_critique`.
7. Maximum iterations: 3. After 3, force HITL regardless of score.

### Automatic HITL triggers (bypasses iteration)

- Jurisdiction outside US domestic.
- Severity appears fatality-level.
- Suspected prompt-injection content in email body.
- Three consecutive low-score drafts.
