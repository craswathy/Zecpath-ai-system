# Task Evaluation Logic (Day 50)

All numbers are starting values for design. Not tuned. Not implemented.

## 1. Evaluation steps for one task
```
Take the final submission (and the run history)
   v
Run hidden tests in the sandbox
   v
Correctness
   v
Efficiency (only if the large-input test passes)
   v
Code quality (static analysis)
   v
Problem-solving approach (snapshots + candidate note)
   v
Metric scores (0 to 1) -> scoring model
```
If the platform fails during a run, retry up to 2 times. If it still fails the metric
is null and the report says "evaluation unavailable". It is never scored as 0.

## 2. Correctness
Correctness = sum(weight of passed tests) / sum(weight of all tests)

| Test group | Weight per test | Purpose |
|---|---|---|
| Basic | 1.0 | Normal cases |
| Edge | 1.5 | Empty input, one item, duplicates, limits, bad data |

Partial credit comes from the test weights. Each test runs with its own time limit.
A test that times out counts as failed.

## 3. Efficiency
Used for coding and file-based tasks. Measured on the large-input hidden test.
1. Run the candidate and the reference solution in the same sandbox.
2. Take the median of 3 runs for each. Ratio r = candidate runtime / reference runtime.
3. Time score: 1.0 if r is 2 or less, 0 if r is 10 or more or the run timed out, and a straight line in between.
4. Memory score uses the same rule on the memory ratio.
5. Efficiency = the lower of the time score and the memory score.

If the large-input output is wrong, efficiency is null (a fast wrong answer earns nothing).

## 4. Code quality
Language tools run: a linter, a complexity check and a duplicate-code check.

Quality = max(0, 1 − 0.04 x lint issues per 100 lines − 0.15 x functions with complexity above 10 − 0.10 x repeated blocks of 6 or more lines)

- Only measured when the code ran.
- Low weight in the scoring model, because style tools judge style narrowly.
- Naming and comments are not penalised beyond what the linter reports.

## 5. Problem-solving approach
Approach = 0.6 x note score + 0.4 x process score

Note score: the candidate's short note is scored on rubric points for that task, for
example "states a plan", "considers edge cases", "names a trade-off". It uses the
same key-point and reasoning method as the Day 47 engine. A human can override it.

Process score = 0.5 x ran before submitting + 0.5 x improvement
- Ran before submitting: 1 if the candidate ran the code at least once, else 0.
- Improvement: visible-test pass rate at the best later run minus the first run, limited to 0 to 1.
  If the first run already passed everything, improvement is 1.

If there is no note, approach = process score only, and the report says so.
A candidate who writes correct code in one clean run is not penalised.

## 6. Rules for each task type
### Coding problem
Correctness, efficiency, quality and approach as above.

### Debugging task
- Correctness: hidden tests pass after the fix.
- No efficiency metric.
- Quality: size of the change. Changed lines at most 3 times the reference fix = 1.0; beyond that it drops in a straight line to 0 at 10 times.
- Approach: the note must name the root cause and say why the fix works. Process score as above.

### File-based task
- Inputs are provided in the working folder. Expected outputs are kept outside the sandbox.
- Comparison tolerates order where order does not matter, extra whitespace, and small number differences.
- Partial credit by share of rows and fields that are right.
- Messy data is part of the task. Handling bad rows is covered by edge tests.
- Efficiency measured on a larger input file.

### Mini system design
- Not executed. Scored with the Day 47 method on four parameters: required components covered, depth, reasoning about trade-offs, and real-world fit.
- Efficiency here means scalability and performance reasoning.
- Mandatory human review before the result is final.

## 7. Failure and missing-data rules
| Situation | Result |
|---|---|
| No submission or empty file | Task score 0 |
| Code does not compile or run | Correctness from the tests it passes (usually 0). Other metrics null |
| Platform error after retries | Metric null, report notes "evaluation unavailable" |
| Efficiency null | Its weight is shared among the other metrics |
| Note missing | Approach from process only |
| Task started but not opened by the candidate (system error) | Excluded from scoring, offered again |

## 8. Optional recruiter context (never scored)
- Code similarity with other candidates or with common solutions. Simple problems have few solution shapes, so a match is a reason to look, not proof.
- Large paste events in snapshots (shared with the Day 49 context).