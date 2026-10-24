# Unified Scoring Engine v2 -- Zecpath (Day 51)

## Purpose
Combine five evaluation rounds into one Hiring Fit Score (percentage):
ATS, Screening, HR Interview, Technical Interview, Machine Test.
Extends the Day 41 engine from three rounds to five. Day 41 files are unchanged.

## Formula
Hiring Fit % = sum of (round score x weight used)
Weight used = role weight rescaled so the weights of the scored rounds add up to 1.0.

## Role weights
| Role | ATS | Screening | HR | Technical | Machine test |
|---|---|---|---|---|---|
| default | 0.15 | 0.20 | 0.25 | 0.25 | 0.15 |
| technical | 0.10 | 0.15 | 0.15 | 0.30 | 0.30 |
| client_facing | 0.15 | 0.20 | 0.40 | 0.15 | 0.10 |
| entry_level | 0.15 | 0.25 | 0.20 | 0.20 | 0.20 |
| senior | 0.10 | 0.10 | 0.20 | 0.35 | 0.25 |

## Normalization across candidate profiles
1. Every round score is on the same 0 to 100 scale. A value outside that range is
   ignored and flagged.
2. Missing rounds are left out and their weight is shared by the other rounds.
   Nothing is invented. A candidate with 3 rounds and a candidate with 5 rounds
   are both scored on a 0 to 100 scale.
3. A round marked low reliability counts for half of its weight.
4. Weights depend on the role, so candidates are compared inside the same role.
5. Rank among candidates for the same job uses category first, then percentage.
   Only final results are ranked.

## Safeguards
| Safeguard | Rule |
|---|---|
| Round floor | Any round below 40 caps the category at Moderate Fit |
| Preliminary result | Fewer than 3 scored rounds: flagged preliminary and capped at Moderate Fit |
| Low reliability | Round counted at half weight, with a flag |
| Invalid score | Ignored and flagged |

## Fit categories
- Strong Fit: 75 and above
- Moderate Fit: 55 to below 75
- Weak Fit: below 55

## Transparency
Every unified score object stores, for each round: score, weight used and points
contributed. The points add up to the hiring-fit percentage, so anyone can check
the result by hand. It also stores flags, missing rounds, and a plain explanation.
Integrity tags and behavioral labels are stored as context and are never scored.

## Worked example (demo_hesitant, technical role)
Machine test is low reliability, so its weight 0.30 becomes 0.15. The weights of
the five rounds then add up to 0.85.
(70 x 0.10 + 66 x 0.15 + 78 x 0.15 + 61.2 x 0.30 + 58 x 0.15) / 0.85 = 65.5
Category: Moderate Fit, final.

## Limits
- Weights, thresholds and the floor are starting values, not tuned on real hiring outcomes.
- The demo uses simulated scores. HR and technical scores come from the earlier demos.
  ATS, screening and machine test scores are invented.
- The preliminary cap is a design choice. It stops one early score from looking final.
- Rank compares only candidates in the same job and role, and a small pool gives a weak ranking.
- A score is decision support. A human recruiter makes the final decision.