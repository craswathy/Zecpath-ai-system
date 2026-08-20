import re
from utils.logger import logger

# Fields considered non-essential to job-fit scoring -- should never
# influence a score, only used for contact/communication purposes.
NON_ESSENTIAL_ATTRIBUTES = [
    "name", "email", "phone", "location", "gender", "age", "photo",
    "marital_status", "nationality", "date_of_birth",
]


def mask_personal_attributes(candidate_profile):
    """
    Return a copy of the candidate profile with non-essential personal
    attributes removed/masked, so downstream scoring never sees them.
    Only skills, experience, education, and certifications remain visible.
    """
    masked = dict(candidate_profile)
    personal_info = masked.get("personal_info", {})

    masked_personal = {
        key: ("[MASKED]" if key in NON_ESSENTIAL_ATTRIBUTES else value)
        for key, value in personal_info.items()
    }
    masked["personal_info"] = masked_personal
    masked["_fairness_note"] = "Personal identifying attributes masked before scoring."

    logger.info("Masked non-essential personal attributes for scoring")
    return masked


def normalize_resume_text(text):
    """
    Standardize resume text formatting so stylistic differences (fonts,
    spacing, casing conventions) don't advantage or disadvantage a
    candidate purely on presentation.
    """
    if not text:
        return ""

    normalized = text
    normalized = re.sub(r"[ \t]+", " ", normalized)          # collapse whitespace
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)         # collapse blank lines
    normalized = re.sub(r"[^\w\s\-.,:@()/&%+]", "", normalized)  # strip decorative symbols
    normalized = normalized.strip()

    return normalized


def normalize_score_distribution(scores):
    """
    Min-max normalize a list of final ATS scores to a consistent 0-100 range,
    so score comparisons stay meaningful even if raw component scores were
    unusually compressed or spread out for a given job posting.
    """
    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)
    spread = max_score - min_score

    if spread == 0:
        return [50.0 for _ in scores]  # all identical -> neutral midpoint

    return [round((s - min_score) / spread * 100, 1) for s in scores]