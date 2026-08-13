from rapidfuzz import fuzz
from parsers.skill_master_dictionary import ALL_SKILLS, SKILL_STACKS
from utils.logger import logger

FUZZY_THRESHOLD = 85  # minimum similarity score (0-100) to accept a fuzzy match


def extract_skills(text, fuzzy=True):
    """
    Extract skills from raw resume text.
    Returns a list of dicts: {skill, category, confidence, match_type}
    """
    text_lower = text.lower()
    found = {}

    # 1. Exact / synonym matching (highest confidence)
    for canonical, info in ALL_SKILLS.items():
        for syn in info["synonyms"]:
            if syn in text_lower:
                confidence = 1.0 if syn == canonical else 0.95
                _add_or_upgrade(found, canonical, info["category"], confidence, "exact")
                break

    # 2. Skill stack expansion (e.g. "MERN" -> mongodb, express.js, react, node.js)
    for stack_name, components in SKILL_STACKS.items():
        if stack_name in text_lower:
            for comp in components:
                comp_info = ALL_SKILLS.get(comp, {"category": "technical"})
                _add_or_upgrade(found, comp, comp_info["category"], 0.85, f"stack:{stack_name}")

    # 3. Fuzzy matching for spelling variations (lower confidence)
    if fuzzy:
        words = text_lower.replace(",", " ").replace("\n", " ").split()
        candidates = set(words) | set(_bigrams(words))
        for canonical, info in ALL_SKILLS.items():
            if canonical in found:
                continue
            for candidate in candidates:
                score = fuzz.ratio(candidate, canonical)
                if score >= FUZZY_THRESHOLD:
                    _add_or_upgrade(found, canonical, info["category"], round(score / 100, 2), "fuzzy")
                    break

    logger.info(f"Extracted {len(found)} unique skills")
    return sorted(found.values(), key=lambda x: -x["confidence"])


def _bigrams(words):
    return [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]


def _add_or_upgrade(found, skill, category, confidence, match_type):
    """Add a skill, or upgrade its confidence if a better match is found (dedup logic)."""
    if skill not in found or found[skill]["confidence"] < confidence:
        found[skill] = {
            "skill": skill,
            "category": category,
            "confidence": confidence,
            "match_type": match_type,
        }