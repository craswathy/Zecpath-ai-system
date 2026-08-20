# Bias Reduction & Fairness Documentation -- Zecpath

## Overview
This document explains the fairness safeguards built into the ATS scoring
pipeline, addressing three risk areas: personal-attribute bias, keyword
overdependence, and score-distribution inconsistency.

## 1. Personal Attribute Masking
Before scoring, non-essential personal attributes -- name, email, phone,
location, gender, age, photo, marital status, nationality, date of birth --
are masked from the data the scoring engine sees. Only job-relevant
attributes (skills, experience, education, certifications) reach the ATS
scoring engine (Day 13). This prevents the model from ever having access
to attributes that could introduce demographic bias, even unintentionally.

## 2. Resume Format Normalization
Resume text is normalized (whitespace, casing conventions, decorative
symbols stripped) before scoring, so candidates are not advantaged or
disadvantaged based on formatting choices, font styling, or document
design skill -- factors unrelated to job qualification.

## 3. Keyword Overdependence Check
A candidate whose score is driven almost entirely by skill/keyword match,
with very low experience/education/semantic contribution, is flagged for
manual review rather than auto-ranked highly. This catches keyword-stuffed
resumes that would otherwise game a keyword-only matching system --
mirroring exactly the problem the semantic matching engine (Day 12) was
built to address.

## 4. Score Distribution Normalization
Final scores are min-max normalized across a candidate pool so that score
comparisons remain meaningful even when the raw score spread for a
particular job posting happens to be unusually compressed or wide.

## 5. Score Distribution Bias Check (group-level)
Where a demographic or non-essential grouping attribute is available
(e.g. institution tier, location) but was NOT used in scoring, average
scores can be compared across groups. A gap larger than 15 points between
group averages is flagged for human review -- this does not change any
individual score, it surfaces a pattern for a person to investigate.

## What This Does Not Do
- These checks reduce risk, they do not guarantee a bias-free system --
  the underlying skill/education dictionaries (Days 9, 11) reflect the
  data used to build them, and should be periodically reviewed for
  coverage gaps across genuinely diverse resume styles.
- Bias flags are surfaced for human review, not auto-resolved -- final
  hiring decisions should always retain human oversight (matches PRD
  Phase 20 recommendation: "Selected / Hold / Rejected" as recruiter-
  reviewed outcomes, not fully automated ones).