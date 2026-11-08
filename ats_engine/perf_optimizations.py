from concurrent.futures import ProcessPoolExecutor
from parsers.resume_reader import extract_resume
from parsers.semantic_matcher import get_model
from utils.logger import logger

_embedding_cache = {}


def clear_cache():
    _embedding_cache.clear()


def cache_size():
    return len(_embedding_cache)


def embed_texts_cached(texts, batch_size=32):
    """
    Return one embedding per input text. Texts already seen come from the
    cache; the rest are encoded together in one batch, each unique text once.
    """
    model = get_model()
    missing = list({t for t in texts if t not in _embedding_cache})
    if missing:
        vectors = model.encode(missing, batch_size=batch_size,
                               convert_to_tensor=True, show_progress_bar=False)
        for text, vector in zip(missing, vectors):
            _embedding_cache[text] = vector
        logger.info(f"Encoded {len(missing)} new texts, cache size {len(_embedding_cache)}")
    return [_embedding_cache[t] for t in texts]


def similarity_matrix(resume_texts, jd_texts):
    """
    All resume-vs-JD cosine similarities in one call.
    Returns a list of rows: result[i][j] = similarity(resume i, JD j).
    """
    import torch
    from sentence_transformers import util
    resume_vectors = torch.stack(embed_texts_cached(resume_texts))
    jd_vectors = torch.stack(embed_texts_cached(jd_texts))
    return util.cos_sim(resume_vectors, jd_vectors).tolist()


def extract_many(paths, workers=None):
    """
    Extract text from many resumes. workers=1 runs sequentially;
    otherwise a process pool is used (PDF parsing is CPU-bound).
    Must be called under an `if __name__ == "__main__":` guard on Windows.
    """
    if workers == 1:
        return [extract_resume(p) for p in paths]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(extract_resume, paths))