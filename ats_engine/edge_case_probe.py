import math

from parsers.text_cleaner import clean_text
from parsers.section_classifier import classify_sections
from parsers.skill_extractor import extract_skills
from parsers.experience_parser import extract_experience_entries
from parsers.education_parser import extract_education_entries
from parsers.jd_parser import parse_jd
from ats_engine.polished_decision_service import safe_decide

TEXT_INPUTS = {
    "empty": "",
    "whitespace_only": "   \n\t  \n",
    "single_word": "Python",
    "numbers_only": "2019 2020 2021 12345",
    "unicode_mixed": "Résumé 简历 — Python • SQL",
    "very_long": "Python SQL Excel. " * 5000,
    "symbols_only": "!@#$%^&*()_+{}|:<>?",
    "single_date_line": "EXPERIENCE\n06/2022 - present",
    "reversed_dates": "EXPERIENCE\nAcme 06/2024 - 01/2020 // Analyst\n",
}

TEXT_STAGES = {
    "clean_text": clean_text,
    "classify_sections": classify_sections,
    "extract_skills": extract_skills,
    "extract_experience_entries": extract_experience_entries,
    "extract_education_entries": extract_education_entries,
    "parse_jd": lambda t: parse_jd(t, job_id="probe"),
}

PAYLOADS = {
    "none": None,
    "list": [1, 2],
    "empty_dict": {},
    "scores_not_dict": {"round_scores": 5},
    "nan_score": {"round_scores": {"ats": float("nan")}},
    "inf_score": {"round_scores": {"ats": math.inf}},
    "negative_score": {"round_scores": {"ats": -5}},
    "bool_score": {"round_scores": {"ats": True}},
    "string_score": {"round_scores": {"ats": "high"}},
}


def find_crashes():
    crashes = []
    for stage, fn in TEXT_STAGES.items():
        for label, text in TEXT_INPUTS.items():
            try:
                fn(text)
            except Exception as exc:
                crashes.append((stage, label, f"{type(exc).__name__}: {str(exc)[:60]}"))
    for label, payload in PAYLOADS.items():
        try:
            result = safe_decide(payload)
            if "error" not in result and label != "empty_dict":
                crashes.append(("safe_decide", label, "bad input was accepted"))
        except Exception as exc:
            crashes.append(("safe_decide", label, f"{type(exc).__name__}: {str(exc)[:60]}"))
    return crashes


def run():
    crashes = find_crashes()
    total = len(TEXT_STAGES) * len(TEXT_INPUTS) + len(PAYLOADS)
    print(f"Checked {total} stage/input combinations.")
    if not crashes:
        print("No crashes.")
    for stage, label, detail in crashes:
        print(f"CRASH  {stage:<28}{label:<18}{detail}")
    print(f"\nFAILURES: {len(crashes)}")
    return crashes


if __name__ == "__main__":
    run()