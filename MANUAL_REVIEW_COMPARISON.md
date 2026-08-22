# Manual Review vs AI Score Comparison -- Zecpath

## Method
For each resume, the AI-generated final_score (from data/ats_scores/) was
compared against a manual judgment call: would a human recruiter reasonably
shortlist, review, or reject this candidate for the job it was scored against?

## Comparison Table

| Resume | Job Scored Against | AI Score | AI Decision | Manual Judgment | Match? |
|---|---|---|---|---|---|
| da_resume_1 | (check ats_scores file) | | | Shortlist/Review/Reject | Yes/No |
| ... | | | | | |

## How to fill this in
1. Open each file: type data\ats_scores\<resume>_ats_score.json
2. Note the final_score and decision_zone (from rankings)
3. Read the resume yourself, read the JD it was scored against
4. Ask: "Would I, as a recruiter, agree with this decision?"
5. Mark Match = Yes if your judgment agrees with the AI, No if it disagrees

