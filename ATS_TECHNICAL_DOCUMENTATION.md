# ATS Technical Documentation -- Zecpath

## Purpose
This is the master reference for the ATS pipeline built across Days 5-18.
It maps each pipeline stage to its module, input/output, and related
documentation, so a new developer can understand the whole system without
reading every day's individual notes.

## Pipeline Stages

### 1. Text Extraction (Day 5)
- **Module**: `parsers/resume_reader.py`, `parsers/text_cleaner.py`
- **Input**: Raw PDF/DOCX file from `data/`
- **Output**: Cleaned text file in `data/extracted/`
- **Key logic**: File-type dispatch (PDF via pdfplumber, DOCX via python-docx),
  then regex-based noise removal and heading normalization.
- **Known limitation**: Multi-column layouts and scanned/image PDFs are not
  reliably handled (see TROUBLESHOOTING_NOTES.md).

### 2. Job Description Parsing (Day 6)
- **Module**: `parsers/jd_parser.py`, `parsers/skill_dictionary.py`
- **Input**: Raw JD text file
- **Output**: Structured JD JSON in `data/jd_parsed/`
- **Key logic**: Dictionary-based skill/education matching, regex-based
  experience-year extraction.
- **See also**: JD_PARSING_DOCUMENTATION.md

### 3. Data Pipeline & Storage Design (Day 7)
- **Documentation only** (no runnable module)
- **See**: STORAGE_STRUCTURE.md, METADATA_STANDARDS.md

### 4. Section Classification (Day 8)
- **Module**: `parsers/section_classifier.py`
- **Input**: Cleaned resume text (Day 5 output)
- **Output**: Labeled sections JSON in `data/labeled_sections/`
- **Key logic**: Heading-based detection with a rule-based content fallback.
- **Known limitation**: Fails when headings are embedded mid-line (column
  layout bug) -- see TROUBLESHOOTING_NOTES.md.

### 5. Skill Extraction (Day 9)
- **Module**: `parsers/skill_extractor.py`, `parsers/skill_master_dictionary.py`
- **Input**: Cleaned resume text
- **Output**: Skill list with confidence scores in `data/skills_extracted/`
- **Key logic**: Three-layer matching (exact, stack expansion, fuzzy via rapidfuzz).
- **See also**: SKILL_CONFIDENCE_SCORING.md

### 6. Experience Parsing (Day 10)
- **Module**: `parsers/experience_parser.py`, `parsers/experience_relevance.py`
- **Input**: Cleaned resume text
- **Output**: Structured experience object in `data/experience_parsed/`
- **Key logic**: Regex date-range detection, interval merging for total
  experience, gap/overlap detection, fuzzy title-relevance scoring.

### 7. Education & Certification Parsing (Day 11)
- **Module**: `parsers/education_parser.py`, `parsers/education_relevance.py`
- **Input**: Labeled EDUCATION/CERTIFICATIONS sections (Day 8 output)
- **Output**: Academic profile JSON in `data/education_parsed/`
- **Key logic**: Degree-hierarchy ranking, dictionary-based field matching.

### 8. Semantic Matching (Day 12)
- **Module**: `parsers/semantic_matcher.py`
- **Input**: Resume sections + JD profile
- **Output**: Similarity scores in `data/semantic_matches/`
- **Key logic**: sentence-transformers embeddings, cosine similarity.
- **See also**: MATCHING_ACCURACY_REPORT.md

### 9. ATS Scoring (Day 13)
- **Module**: `ats_engine/ats_scorer.py`, `ats_engine/scoring_config.py`
- **Input**: Outputs from stages 5-8 (skills, experience, education, semantic)
- **Output**: Final explainable score in `data/ats_scores/`
- **Key logic**: Weighted combination with missing-data redistribution.

### 10. Ranking & Shortlisting (Day 14)
- **Module**: `ats_engine/candidate_ranker.py`, `ats_engine/recruiter_report.py`
- **Input**: ATS scores (Day 13 output)
- **Output**: Ranked list + recruiter report in `data/rankings/`
- **Key logic**: Sort by score, threshold-based zone classification.

### 11. Fairness & Bias Reduction (Day 15)
- **Module**: `ats_engine/fairness_normalizer.py`, `ats_engine/bias_checker.py`
- **Output**: Fairness review in `data/fairness_review/`
- **See also**: BIAS_REDUCTION_DOCUMENTATION.md

### 12. API Layer (Day 16)
- **Module**: `ats_engine/api_server.py`, `ats_engine/api_schemas.py`
- **See also**: ATS_API_SPECIFICATION.md, INTEGRATION_FLOW_DOCUMENT.md

### 13. Testing (Day 17)
- **See**: ATS_TESTING_REPORT.md, IMPROVEMENT_BACKLOG.md

### 14. Performance & Stability (Day 18)
- **Module**: `ats_engine/performance_benchmark.py`, `ats_engine/memory_utils.py`
- **See also**: PERFORMANCE_REPORT.md, STABILITY_IMPROVEMENTS.md

## Full Pipeline Execution Order
```
python -m parsers.run_extraction
python -m parsers.run_jd_parsing
python -m parsers.run_section_classification
python -m parsers.run_skill_extraction
python -m parsers.run_experience_parsing
python -m parsers.run_education_parsing
python -m parsers.run_semantic_matching
python -m ats_engine.run_ats_scoring
python -m ats_engine.run_ranking
python -m ats_engine.run_fairness_check
```