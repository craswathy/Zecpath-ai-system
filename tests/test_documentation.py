import os
import re

HANDBOOK = "ZECPATH_AI_TECHNICAL_HANDBOOK.md"
CORE = [
    "README.md", "CODING_STANDARDS.md", "DEVELOPER_GUIDE.md",
    "TROUBLESHOOTING_NOTES.md", "ATS_TECHNICAL_DOCUMENTATION.md",
    "SCREENING_TECHNICAL_DOCUMENTATION.md", "ARCHITECTURE_OVERVIEW.md",
    "AI_INTEGRATION_DOCUMENT.md", "SCALABILITY_STRATEGY.md",
    "AI_OBSERVABILITY_PLAN.md", "LOGGING_STRUCTURE.md",
    "UNIFIED_SCORING_DOCUMENTATION.md", "ATS_API_SPECIFICATION.md",
    "SYSTEM_ARCHITECTURE_DOCUMENTATION.md", "DEVELOPER_ONBOARDING_GUIDE.md",
    "MODULE_INDEX.md", HANDBOOK,
]


def test_core_documents_exist():
    missing = [d for d in CORE if not os.path.exists(d)]
    assert missing == [], f"Missing documents: {missing}"


def test_handbook_references_only_existing_files():
    with open(HANDBOOK, "r", encoding="utf-8") as f:
        mentioned = set(re.findall(r"[A-Z][A-Z0-9_]+\.md", f.read()))
    missing = sorted(m for m in mentioned if not os.path.exists(m))
    assert missing == [], f"Handbook mentions missing files: {missing}"