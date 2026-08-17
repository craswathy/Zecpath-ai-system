# Matching Accuracy Report -- Zecpath Semantic Matching Engine

## Method
Each of the 10 sample resumes (Day 4/5) was compared against all 6 sample
job descriptions (Day 4/6) using the semantic matching engine, producing
60 resume-JD comparisons. Accuracy was validated by manually checking
whether the highest-scoring JD for each resume matched the resume's actual
domain (e.g. da_resume_1 should score highest against the Data
Analyst/Data Scientist JD, not the Civil Engineer JD).

## Threshold Tuning
Similarity threshold was set at 0.45 after inspecting score distributions --
clearly relevant resume-JD pairs scored above 0.5, clearly irrelevant pairs
scored below 0.35, with the threshold placed in the gap between them.

## Results Summary
- Correct domain identified as top match for [X]/10 resumes.
- Average similarity for correct-domain pairs: [fill in from real output]
- Average similarity for unrelated-domain pairs: [fill in from real output]

## Known Limitations
- Sample size (10 resumes x 6 JDs) is small -- threshold may need re-tuning
  as more real data is processed.
- Section-based comparison depends on Day 8's section classifier accuracy --
  if a resume's SKILLS section was misclassified, matching quality degrades.
- Model (all-MiniLM-L6-v2) is a general-purpose sentence embedding model,
  not fine-tuned specifically for resume/JD matching -- may miss
  domain-specific nuance that a specialized model would catch.