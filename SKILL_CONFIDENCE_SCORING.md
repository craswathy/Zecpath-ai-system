\# Skill Confidence Scoring Logic -- Zecpath



\## Match Types and Confidence Levels



| Match Type | Confidence | Description |

|---|---|---|

| Exact canonical match | 1.0 | The skill's canonical name appears verbatim in the text |

| Synonym match | 0.95 | A known synonym/variation appears (e.g. "ML" for "machine learning") |

| Stack expansion | 0.85 | Skill inferred from a stack mention (e.g. "MERN" implies React, Node.js, MongoDB, Express.js) |

| Fuzzy match | 0.85-0.99 (variable) | Spelling variation caught via similarity scoring (e.g. "Pyhton" -> "python"), confidence = similarity score / 100 |



\## Deduplication Rule



If the same skill is matched by more than one method (e.g. both exact and fuzzy), the highest confidence score wins -- the skill is only listed once in the final output, tagged with whichever match type produced the highest confidence.



\## Why this matters



Downstream ATS scoring can filter or weight skills by confidence -- a skill detected via exact match should count more heavily than one inferred from a fuzzy spelling match, reducing false positives while still catching real variations.

