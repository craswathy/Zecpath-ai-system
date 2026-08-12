import re
from utils.logger import logger

# Canonical section name -> heading variations that map to it
SECTION_HEADINGS = {
    "SKILLS": ["skills", "technical skills", "core skills", "key skills"],
    "EXPERIENCE": ["experience", "work experience", "professional experience", "employment history"],
    "EDUCATION": ["education", "academic background", "qualifications"],
    "CERTIFICATIONS": ["certifications", "certificates", "licenses"],
    "PROJECTS": ["projects", "academic projects", "key projects"],
    "SUMMARY": ["summary", "objective", "profile"],
    "CONTACT": ["contact", "contact information"],
}

# Rule-based signals used when no heading is present (fallback)
DATE_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
DEGREE_PATTERN = re.compile(r"\b(b\.?tech|bachelor|master|msc|bsc|phd|degree)\b", re.IGNORECASE)
SKILL_SEPARATOR_PATTERN = re.compile(r",\s*\w+,\s*\w+")  # comma-separated word lists


def match_heading(line):
    """Check if a line is a known section heading; return canonical name or None."""
    line_clean = line.strip().lower().rstrip(":")
    for canonical, variants in SECTION_HEADINGS.items():
        if line_clean in variants:
            return canonical
    return None


def guess_section_by_content(block_text):
    """Fallback rule-based guess when no heading was detected for a block."""
    if DEGREE_PATTERN.search(block_text):
        return "EDUCATION"
    if DATE_PATTERN.search(block_text) and len(block_text.split()) > 15:
        return "EXPERIENCE"
    if SKILL_SEPARATOR_PATTERN.search(block_text) and len(block_text.split()) < 25:
        return "SKILLS"
    return "UNCLASSIFIED"


def classify_sections(cleaned_text):
    """
    Split cleaned resume text into sections.
    Returns a dict: {section_name: [text blocks]}
    """
    lines = cleaned_text.split("\n")
    sections = {}
    current_section = "HEADER"
    buffer = []

    for line in lines:
        heading = match_heading(line)
        if heading:
            # flush previous buffer into current_section
            if buffer:
                sections.setdefault(current_section, []).append("\n".join(buffer).strip())
                buffer = []
            current_section = heading
        else:
            if line.strip():
                buffer.append(line)

    if buffer:
        sections.setdefault(current_section, []).append("\n".join(buffer).strip())

    # fallback: reclassify anything still stuck under HEADER/UNCLASSIFIED
    if "HEADER" in sections:
        reclassified = []
        for block in sections["HEADER"]:
            guess = guess_section_by_content(block)
            if guess != "UNCLASSIFIED":
                sections.setdefault(guess, []).append(block)
            else:
                reclassified.append(block)
        sections["HEADER"] = reclassified

    logger.info(f"Classified into sections: {list(sections.keys())}")
    return sections