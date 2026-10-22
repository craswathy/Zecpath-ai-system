# Scoring Model for Real-World Tasks (Day 50)

All numbers are starting values for design. Not tuned. Not implemented.

## 1. Metric weights by task type
| Task type | Correctness | Efficiency | Code quality | Approach |
|---|---|---|---|---|
| Coding | 0.50 | 0.20 | 0.15 | 0.15 |
| Debugging | 0.50 | 0.00 | 0.15 | 0.35 |
| File-based | 0.55 | 0.10 | 0.15 | 0.20 |
| Mini system design | 0.40 | 0.20 | 0.15 | 0.25 |

Each row adds up to 1.0. Metric definitions are in TASK_EVALUATION_LOGIC.md.
A metric that is null is left out and its weight is shared among the others in
proportion to their weights. Nothing is invented.

Base score = sum(metric x weight), on a 0 to 1 scale.

## 2. Time-based scoring
Rules:
1. Each task has an expected time and a time limit of 1.5 times the expected time.
2. Time is measured on the server, starting when the candidate opens the task. Outages
   and platform pauses are removed from the time used.
3. At the limit the last saved snapshot is submitted automatically. The candidate is told this first.
4. Correctness comes first. Time can lower the score by at most 10 percent.

Time factor:
- Time used is at or below the expected time: 1.0.
- Between expected time and the limit: falls in a straight line from 1.0 to 0.9.

Task score = base score x time factor

A faster finish earns no bonus. Finishing early is not a reason to score higher,
because speed can mean carelessness as much as skill.

Extra time for a candidate: expected time and limit are multiplied by the same
factor (for example 1.5). The reason is not stored.

## 3. Across difficulty levels
Combine task scores with the level weights used on Day 47.
| Level | Weight |
|---|---|
| L1 | 1.0 |
| L2 | 1.5 |
| L3 | 2.0 |

Overall machine test score = sum(task score x level weight) / sum(level weights) x 100

Skill breakdown by task type (coding, debugging, file-based, design) uses the same
weighted average inside each type.

## 4. Bands, floor and reliability
- 75 and above: Strong. 50 and above: Adequate. Below 50: Below-expectation.
- Floor: any task type scoring below 0.4 lowers the band by one level, so a strong
  coding score cannot hide a failed debugging task.
- Fewer than 3 scored tasks: low reliability.
- Candidates with null (evaluation unavailable) tasks are not scored on those tasks.

## 5. Worked examples
Example A: coding task, level L2
- Hidden tests: 5 basic (all pass), 3 edge (2 pass). Weights: 5 x 1.0 + 3 x 1.5 = 9.5 total. Passed: 5 + 2 x 1.5 = 8. Correctness = 0.84.
- Efficiency: ratio r = 3. Score = (10 − 3) / (10 − 2) = 0.875.
- Quality: 0.80. Approach: note 0.70, process 1.0, so 0.6 x 0.70 + 0.4 x 1.0 = 0.82.
- Base = 0.50 x 0.84 + 0.20 x 0.875 + 0.15 x 0.80 + 0.15 x 0.82 = 0.838.
- Time: expected 30 minutes, used 36, limit 45. Time factor = 1 − 0.1 x (36 − 30) / (45 − 30) = 0.96.
- Task score = 0.838 x 0.96 = about 0.80, so 80.4 of 100.

Example B: efficiency unavailable
Large-input output is wrong, so efficiency is null. Correctness 0.60, quality 0.80, approach 0.70.
Weights shared: 0.50, 0.15, 0.15 add up to 0.80, giving 0.625, 0.1875 and 0.1875.
Base = 0.60 x 0.625 + 0.80 x 0.1875 + 0.70 x 0.1875 = 0.656. The report says "efficiency not scored: large-input output incorrect".

Example C: overall machine test
Coding L2 80.4, debugging L1 90, file-based L2 70.
Overall = (80.4 x 1.5 + 90 x 1.0 + 70 x 1.5) / (1.5 + 1.0 + 1.5) = 315.6 / 4 = 78.9, Strong.
No task type is below 0.4, so no band change. Reliability: reliable (3 tasks).

## 6. Report format
1. Summary: score, band, reliability, one-line reason.
2. Task breakdown: for each task, type, level, the four metrics, time used versus expected, task score.
3. Evidence: tests passed (counts), runtime ratio, linter results, short timeline of runs and pass rates.
4. Candidate note shown beside the approach score.
5. Context flags: code similarity or paste events (not scored).
6. Notes on null metrics and why.
7. Statement: decision support, human review required.

## 7. Record format (Day 7 metadata)
```
{
  "candidate_id": "cand_00123",
  "metadata": {"model_version": "machine_test_v0.1", "timestamp": "...", "stage": "machine_test_scored", "status": "complete"},
  "tasks": [
    {"task_id": "code_l2_017", "type": "coding", "level": "L2",
     "metrics": {"correctness": 0.84, "efficiency": 0.875, "quality": 0.80, "approach": 0.82},
     "time": {"used_min": 36, "expected_min": 30, "limit_min": 45, "factor": 0.96},
     "score": 80.4}
  ],
  "machine_test_score": 78.9,
  "band": "Strong",
  "reliability": "reliable",
  "weight_in_hiring_fit": "to be decided",
  "explanation": "Level-weighted average of 3 tasks = 78.9"
}
```

## 8. Limits
1. Not built. Weights, time factor and thresholds are untuned.
2. Runtime ratios vary between machines, so the reference runs in the same sandbox and the median of 3 is used.
3. Code quality tools reward conventional style. Low weight is the mitigation.
4. Approach scoring can misread offline planners. A single clean run is not penalised.
5. Mini system design needs human review.
6. The score is decision support, not a hiring decision.