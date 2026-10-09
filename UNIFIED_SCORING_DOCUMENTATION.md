# Unified Scoring Engine Documentation -- Zecpath

## Purpose
Combines the three scoring rounds built so far into one hiring-fit
percentage: ATS (Day 13), Screening (Day 26), HR Interview (Day 37).

## Formula
Hiring Fit % = (ATS x w1) + (Screening x w2) + (HR Interview x w3)

Default weights: ATS 0.30, Screening 0.30, HR Interview 0.40.
Role-based profiles shift these. Technical roles use ATS 0.40,
Screening 0.25, HR 0.35. Client-facing roles weight the HR interview
at 0.50. Entry-level roles use 0.35 / 0.30 / 0.35.

## Safeguards
1. Missing round handling: if a round has no score, its weight is
   redistributed across the available rounds (same approach as Day 13).
2. Round floor (from Day 40 testing): any single round below 40 caps the
   category at Moderate Fit, so strong rounds cannot hide a very weak one.
3. Data sufficiency flag: fewer than 2 completed rounds is flagged as
   low confidence.

## Fit Categories
- Strong Fit: 75 and above
- Moderate Fit: 55 to 74
- Weak Fit: below 55

## Verified Results (demo run)
- real_demo (ba_resume_1): ATS 79.8, Screening 83.5, HR 65.5 -> 75.7% Strong Fit
- balanced_strong: 82.0% Strong Fit
- one_weak_round: 69.5% Moderate Fit, flagged for the weak HR round
- missing_hr_round: 78.1% Strong Fit, HR weight redistributed (0.615 / 0.385)
- weak_across_rounds: 40.5% Weak Fit

## Unified Candidate Score Object
One JSON per candidate containing candidate_id, job_id, role_category,
metadata (model_version, timestamp, stage, status), all three round
scores with explanations, the hiring-fit result with flags, the weights
used, and any missing rounds. Status is complete (3 rounds), partial
(1-2 rounds), or pending (none), following the Day 7 metadata standard.

## Known Limitations
- Thresholds (75 / 55) and the floor (40) are starting values, not tuned
  on real hiring outcomes. Same lesson as Day 14: calibrate against
  observed score distributions before production use.
- The demo run links ATS, screening, and HR data by assumption, because
  the earlier days' demo data does not share candidate IDs. The other
  profiles are simulated.