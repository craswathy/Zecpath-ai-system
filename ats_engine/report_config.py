# Day 53: thresholds and wording for the hiring intelligence report. Starting values.

MODEL_VERSION = "report_v1.0"

ROUND_NAMES = ["ats", "screening", "hr_interview", "technical_interview", "machine_test"]
ROUND_LABELS = {
    "ats": "ATS", "screening": "Screening", "hr_interview": "HR interview",
    "technical_interview": "Technical interview", "machine_test": "Machine test",
}

STRENGTH_ROUND_SCORE = 75     # a round at or above this is listed as a strength
WEAKNESS_ROUND_SCORE = 55     # a round below this is listed as a weakness
ROUND_FLOOR = 40              # same floor as the aggregation engine
HR_COMPONENT_STRONG = 0.8
HR_COMPONENT_WEAK = 0.5
SKILL_STRONG = 0.75
SKILL_WEAK = 0.5
SHALLOW_FLAG = 2              # this many shallow technical answers is listed as a weakness
MAX_ITEMS = 6                 # maximum items per list, so the summary stays one page

LIMITATIONS = [
    "This report is decision support. A human recruiter makes the final decision.",
    "Scores come from rule-based scoring with starting thresholds that are not tuned on real hiring outcomes.",
    "Behavioral and integrity information is context only. Integrity tags are reasons to look, not proof of misconduct.",
    "Confidence shows how far to trust the evidence. It is not the chance that the candidate is a good hire.",
]