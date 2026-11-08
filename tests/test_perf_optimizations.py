import sys
sys.path.append(".")
from ats_engine.perf_optimizations import (
    embed_texts_cached, similarity_matrix, clear_cache, cache_size,
)
from parsers.semantic_matcher import semantic_similarity


def test_cache_encodes_each_unique_text_once():
    clear_cache()
    embed_texts_cached(["python sql", "python sql", "civil engineering"])
    assert cache_size() == 2


def test_repeat_call_adds_nothing_to_cache():
    clear_cache()
    embed_texts_cached(["data analyst"])
    embed_texts_cached(["data analyst"])
    assert cache_size() == 1


def test_batched_matrix_matches_pairwise_scores():
    resumes = ["Python SQL machine learning", "AutoCAD site design"]
    jds = ["Data analyst needing Python", "Civil engineer"]
    matrix = similarity_matrix(resumes, jds)
    for i, r in enumerate(resumes):
        for j, jd in enumerate(jds):
            assert abs(matrix[i][j] - semantic_similarity(r, jd)) < 0.02