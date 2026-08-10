from parsers.jd_parser import extract_required_skills, extract_experience_years

def test_extract_skills_finds_python():
    text = "Must have experience with Python and SQL"
    skills = extract_required_skills(text)
    assert "python" in skills
    assert "sql" in skills

def test_extract_experience_years():
    text = "Experience : 0 - 4 Yrs"
    result = extract_experience_years(text)
    assert result["min_experience_years"] == 0
    assert result["max_experience_years"] == 4