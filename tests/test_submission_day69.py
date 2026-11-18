import os
import re
import sys
sys.path.append(".")

REQUIRED = ["README.md", "DOCUMENTATION_INDEX.md", "AI_ROADMAP.md",
            "INTERNSHIP_PORTFOLIO.md", "requirements.txt"]


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_required_submission_files_exist():
    assert [f for f in REQUIRED if not os.path.exists(f)] == []


def test_readme_has_setup_run_and_limits():
    text = read("README.md")
    for heading in ("## Setup", "## Run the pipeline", "## Run the tests",
                    "## Documentation", "## Known limitations"):
        assert heading in text, heading


def test_index_lists_only_existing_files():
    listed = re.findall(r"`([^`]+\.(?:md|txt|json))`", read("DOCUMENTATION_INDEX.md"))
    missing = sorted(f for f in set(listed) if not os.path.exists(f))
    assert missing == [], f"Index lists missing files: {missing}"


def test_roadmap_has_all_phases_and_risks():
    text = read("AI_ROADMAP.md")
    for phase in ("Phase 1", "Phase 2", "Phase 3", "Phase 4", "## 4. Risks"):
        assert phase in text, phase


def test_portfolio_is_fully_filled_in():
    assert "[ ]" not in read("INTERNSHIP_PORTFOLIO.md"), "Fill every [ ] before submitting"