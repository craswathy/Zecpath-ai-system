import sys
sys.path.append(".")
from parsers.text_cleaner import clean_text

def test_clean_text_removes_bullets():
    raw = "• Python\n• SQL"
    result = clean_text(raw)
    assert "- Python" in result
    assert "- SQL" in result

def test_clean_text_handles_empty():
    assert clean_text("") == ""

def test_clean_text_normalizes_section_heading():
    raw = "experience\nWorked at ABC Corp"
    result = clean_text(raw)
    assert "EXPERIENCE" in result