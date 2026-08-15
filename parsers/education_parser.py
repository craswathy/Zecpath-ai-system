import re
from parsers.education_dictionary import DEGREE_PATTERNS, FIELD_OF_STUDY, CERTIFICATION_CATEGORIES
from utils.logger import logger

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")


def normalize_degree(text):
    """Match text against known degree patterns, return canonical degree name."""
    text_lower = text.lower()
    for canonical, variants in DEGREE_PATTERNS.items():
        for v in variants:
            if v in text_lower:
                return canonical
    return None


def normalize_field_of_study(text):
    """Match text against known field-of-study keywords."""
    text_lower = text.lower()
    for canonical, variants in FIELD_OF_STUDY.items():
        for v in variants:
            if v in text_lower:
                return canonical
    return None


def extract_graduation_year(text):
    """Pull the most recent 4-digit year mentioned in the line/block."""
    years = YEAR_PATTERN.findall(text)
    all_years = YEAR_PATTERN.findall(text)  # re-run to get full matches
    matches = re.findall(r"\b(19|20)\d{2}\b", text)
    full_years = re.findall(r"\b((?:19|20)\d{2})\b", text)
    if full_years:
        return max(int(y) for y in full_years)
    return None


def extract_education_entries(education_block_text):
    """
    Parse the EDUCATION section text (from Day 8's section classifier)
    into structured entries: degree, field_of_study, institution, year.
    """
    entries = []
    lines = [l.strip() for l in education_block_text.split("\n") if l.strip()]

    for line in lines:
        degree = normalize_degree(line)
        if not degree:
            continue

        field = normalize_field_of_study(line)
        year = extract_graduation_year(line)

        # institution = whatever text remains after removing degree/field keywords (rough heuristic)
        institution = line
        institution = re.sub(YEAR_PATTERN, "", institution).strip(" -,")

        entries.append({
            "degree": degree,
            "field_of_study": field,
            "institution": institution if institution else None,
            "graduation_year": year,
        })

    logger.info(f"Extracted {len(entries)} education entries")
    return entries


def extract_certifications(cert_block_text):
    """
    Parse the CERTIFICATIONS section text into structured entries,
    tagged with a relevance category (cloud, analytics, project management, etc.).
    """
    certs = []
    lines = [l.strip() for l in cert_block_text.split("\n") if l.strip()]

    for line in lines:
        line_lower = line.lower()
        category = "general"
        for keyword, cat in CERTIFICATION_CATEGORIES.items():
            if keyword in line_lower:
                category = cat
                break

        year = extract_graduation_year(line)

        certs.append({
            "name": line,
            "category": category,
            "year": year,
        })

    logger.info(f"Extracted {len(certs)} certifications")
    return certs