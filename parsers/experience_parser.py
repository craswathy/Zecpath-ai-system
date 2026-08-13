import re
from datetime import datetime
from dateutil import parser as dateparser
from utils.logger import logger

DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>(\d{1,2}/\d{4})|([A-Za-z]{3,9}\.?\s\d{4})|(\d{4}))"
    r"\s*[-\u2013\u2014]\s*"
    r"(?P<end>present|current|(\d{1,2}/\d{4})|([A-Za-z]{3,9}\.?\s\d{4})|(\d{4}))",
    re.IGNORECASE,
)


def parse_date(raw):
    """Convert a raw date string ('06/2020', 'Jan 2021', 'present') into a datetime."""
    if not raw:
        return None
    raw = raw.strip()
    if raw.lower() in ("present", "current"):
        return datetime.now()
    try:
        return dateparser.parse(raw, default=datetime(1900, 1, 1))
    except (ValueError, OverflowError):
        return None


def extract_experience_entries(text):
    """
    Scan cleaned resume text line by line, find date ranges, and pull the
    surrounding text as company/title.
    Returns a list of raw entries (unparsed dates as strings).
    """
    entries = []
    lines = text.split("\n")

    for line in lines:
        match = DATE_RANGE_PATTERN.search(line)
        if not match:
            continue

        before = line[: match.start()].strip(" -\u2013\u2014")
        after = line[match.end() :].strip(" -\u2013\u2014")

        company = before if before else None
        designation = None

        if "//" in after:
            _, designation = after.split("//", 1)
            designation = designation.strip()
        elif after:
            designation = after.strip()

        entries.append({
            "company": company,
            "designation": designation,
            "start_date_raw": match.group("start"),
            "end_date_raw": match.group("end"),
        })

    logger.info(f"Extracted {len(entries)} experience entries")
    return entries


def compute_experience_summary(entries):
    """
    Parse raw date strings, merge overlapping periods, compute total
    experience years, and detect gaps/overlaps.
    """
    intervals = []
    for e in entries:
        start = parse_date(e["start_date_raw"])
        end = parse_date(e["end_date_raw"])
        if start and end and end > start:
            intervals.append((start, end, e))

    intervals.sort(key=lambda x: x[0])

    merged = []
    gaps = []
    overlaps = []

    for start, end, source in intervals:
        if not merged:
            merged.append([start, end])
        else:
            last = merged[-1]
            if start <= last[1]:
                if start < last[1]:
                    overlaps.append({
                        "overlap_start": start.strftime("%Y-%m"),
                        "overlap_end": last[1].strftime("%Y-%m"),
                    })
                last[1] = max(last[1], end)
            else:
                gap_days = (start - last[1]).days
                if gap_days > 30:
                    gaps.append({
                        "gap_from": last[1].strftime("%Y-%m"),
                        "gap_to": start.strftime("%Y-%m"),
                        "gap_days": gap_days,
                    })
                merged.append([start, end])

    total_days = sum((end - start).days for start, end in merged)
    total_years = round(total_days / 365.25, 2)

    return {
        "total_experience_years": total_years,
        "gaps": gaps,
        "overlaps": overlaps,
    }