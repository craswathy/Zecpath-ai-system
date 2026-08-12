from parsers.section_classifier import classify_sections

def test_classify_detects_skills_heading():
    text = "SKILLS\nPython, SQL, Excel\nEXPERIENCE\nWorked at ABC Corp 2020-2023"
    result = classify_sections(text)
    assert "SKILLS" in result
    assert "EXPERIENCE" in result

def test_classify_handles_missing_heading_fallback():
    text = "Python, SQL, Excel, Power BI"
    result = classify_sections(text)
    assert "SKILLS" in result or "UNCLASSIFIED" in result