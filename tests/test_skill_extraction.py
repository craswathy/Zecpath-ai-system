from parsers.skill_extractor import extract_skills

def test_extract_exact_match():
    text = "Skilled in Python and SQL"
    skills = extract_skills(text)
    names = [s["skill"] for s in skills]
    assert "python" in names
    assert "sql" in names

def test_extract_skill_stack():
    text = "Experience with MERN stack development"
    skills = extract_skills(text)
    names = [s["skill"] for s in skills]
    assert "react" in names
    assert "mongodb" in names

def test_extract_fuzzy_spelling():
    text = "Worked extensively with Pyhton for automation"
    skills = extract_skills(text)
    names = [s["skill"] for s in skills]
    assert "python" in names