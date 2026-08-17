import sys
sys.path.append(".")
from parsers.semantic_matcher import semantic_similarity

def test_similar_text_scores_high():
    score = semantic_similarity("Python, SQL, machine learning", "Python and SQL experience required")
    assert score > 0.5

def test_unrelated_text_scores_low():
    score = semantic_similarity("Civil engineering, AutoCAD, site design", "React, Node.js, JavaScript developer")
    assert score < 0.4