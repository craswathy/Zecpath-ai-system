import json
import os
import sys
sys.path.append(".")

DIR = "demo_dataset_day63"


def test_dataset_files_exist():
    assert len(os.listdir(os.path.join(DIR, "resumes"))) == 8
    assert len(os.listdir(os.path.join(DIR, "job_descriptions"))) == 2


def test_every_profile_has_a_resume_and_a_job():
    with open(os.path.join(DIR, "test_candidate_profiles.json"), encoding="utf-8") as f:
        profiles = json.load(f)
    assert len(profiles) == 8
    for p in profiles:
        assert os.path.exists(os.path.join(DIR, "resumes", p["candidate_id"] + ".txt"))
        assert os.path.exists(os.path.join(DIR, "job_descriptions", p["job_id"] + ".txt"))
        assert len(p["responses"]) >= 2


def test_dataset_covers_varied_quality():
    with open(os.path.join(DIR, "test_candidate_profiles.json"), encoding="utf-8") as f:
        qualities = " ".join(p["quality"] for p in json.load(f))
    for word in ("strong", "fresher", "keyword", "gap", "overqualified", "wrong domain"):
        assert word in qualities


def test_simulation_runs_for_all_candidates():
    from ats_engine.run_demo_simulation import run
    run()
    with open(os.path.join(DIR, "simulation_results.json"), encoding="utf-8") as f:
        results = json.load(f)
    assert len(results) == 8
    for r in results:
        assert 0 <= r["hiring_fit_percentage"] <= 100
        assert r["category"] in ("Strong Fit", "Moderate Fit", "Weak Fit")
        assert "ats" in r and "hr" in r