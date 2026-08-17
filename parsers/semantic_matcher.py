from sentence_transformers import SentenceTransformer, util
from utils.logger import logger

# Small, fast model -- good enough for resume/JD matching, no GPU required
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model (first call only)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text):
    """Convert a text block into a semantic embedding vector."""
    if not text or not text.strip():
        return None
    model = get_model()
    return model.encode(text, convert_to_tensor=True)


def semantic_similarity(text_a, text_b):
    """
    Return a 0-1 similarity score between two text blocks based on
    meaning, not just shared keywords.
    """
    emb_a = embed_text(text_a)
    emb_b = embed_text(text_b)
    if emb_a is None or emb_b is None:
        return 0.0
    score = util.cos_sim(emb_a, emb_b).item()
    return round(max(0.0, min(1.0, score)), 3)


def compare_resume_to_jd(resume_sections, jd_profile):
    """
    Compare a candidate's resume sections (from Day 8 classifier output)
    against a parsed JD profile (from Day 6), across skills, experience,
    and projects.
    Returns a dict of per-category similarity scores + an overall score.
    """
    resume_skills_text = " ".join(resume_sections.get("SKILLS", []))
    resume_experience_text = " ".join(resume_sections.get("EXPERIENCE", []))
    resume_projects_text = " ".join(resume_sections.get("PROJECTS", []))

    jd_skills_text = ", ".join(s["name"] for s in jd_profile.get("required_skills", []))
    jd_title = jd_profile.get("title", "")

    skills_score = semantic_similarity(resume_skills_text, jd_skills_text)
    experience_score = semantic_similarity(resume_experience_text, jd_title)
    projects_score = semantic_similarity(resume_projects_text, jd_skills_text)

    weights = {"skills": 0.5, "experience": 0.3, "projects": 0.2}
    overall = round(
        skills_score * weights["skills"]
        + experience_score * weights["experience"]
        + projects_score * weights["projects"],
        3,
    )

    logger.info(f"Semantic match vs '{jd_title}': overall={overall}")
    return {
        "skills_similarity": skills_score,
        "experience_similarity": experience_score,
        "projects_similarity": projects_score,
        "overall_similarity": overall,
    }