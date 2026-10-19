import sys
sys.path.append(".")
from ats_engine.technical_scoring_config import PARAMETER_WEIGHTS
from ats_engine.technical_scoring_engine import (
    score_answer, score_technical_interview, build_text_report,
)

CONCEPT_Q = {
    "id": "t_con_l2", "type": "conceptual", "level": "L2",
    "key_points": ["runs side effects after render", "dependency array controls re-run", "cleanup function"],
}
EXP_Q = {"id": "t_exp_l1", "type": "experience", "level": "L1", "key_points": ["a", "b", "c"]}

DEEP = ("useEffect runs side effects after render. The dependency array controls when it runs again, "
        "so an empty array runs it once. A cleanup function runs before the next run, for example to stop a timer.")
SHALLOW = "Runs side effects, dependency array, cleanup function."


def test_weights_add_up_to_one():
    for weights in PARAMETER_WEIGHTS.values():
        assert round(sum(weights.values()), 5) == 1.0


def test_deep_answer_beats_shallow_answer():
    deep = score_answer(CONCEPT_Q, DEEP, "react")
    shallow = score_answer(CONCEPT_Q, SHALLOW, "react")
    assert deep["score"] > shallow["score"]
    assert deep["depth_label"] == "deep"
    assert shallow["depth_label"] == "shallow"


def test_keyword_listing_is_flagged():
    shallow = score_answer(CONCEPT_Q, SHALLOW, "react")
    assert shallow["keyword_listing"] is True
    assert "little explanation" in shallow["explanation"]


def test_empty_answer_scores_zero():
    result = score_answer(CONCEPT_Q, "   ", "react")
    assert result["score"] == 0.0
    assert result["depth_label"] == "no answer"


def test_experience_answer_uses_evidence_checks():
    good = score_answer(EXP_Q, "I built a login form in my college project. The hardest part was showing errors.", "react")
    weak = score_answer(EXP_Q, "I made a form.", "react")
    assert good["parameters"]["accuracy"] > weak["parameters"]["accuracy"]


def test_harder_level_counts_more():
    easy = {"topic": "a", "level": "L1", "score": 1.0, "depth_label": "deep", "keyword_listing": False,
            "parameters": {"accuracy": 1, "depth": 1, "reasoning": 1, "applicability": 1}}
    hard = {"topic": "a", "level": "L3", "score": 0.0, "depth_label": "deep", "keyword_listing": False,
            "parameters": {"accuracy": 0, "depth": 0, "reasoning": 0, "applicability": 0}}
    result = score_technical_interview([easy, hard])
    assert result["technical_score"] < 50  # L3 weight 2.0 vs L1 weight 1.0


def test_weak_skill_lowers_band():
    def ans(topic, level, score):
        return {"topic": topic, "level": level, "score": score, "depth_label": "deep", "keyword_listing": False,
                "parameters": {"accuracy": score, "depth": score, "reasoning": score, "applicability": score}}
    answers = [ans("react", "L1", 0.9)] * 5 + [ans("node", "L1", 0.2)]
    result = score_technical_interview(answers)
    assert result["weak_skills"] == ["node"]
    assert result["band_adjusted_from"] is not None


def test_few_answers_are_low_reliability():
    one = score_answer(CONCEPT_Q, DEEP, "react")
    assert score_technical_interview([one])["reliability"] == "low_reliability"


def test_report_has_all_sections():
    one = score_answer(CONCEPT_Q, DEEP, "react")
    result = score_technical_interview([one])
    text = build_text_report("c1", "mern", [one], result)
    for heading in ("1. SUMMARY", "2. SKILL-WISE BREAKDOWN", "3. PARAMETER AVERAGES", "4. ANSWER DETAIL"):
        assert heading in text