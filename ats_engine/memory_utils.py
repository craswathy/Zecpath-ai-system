import gc
from utils.logger import logger


def release_memory():
    """
    Force garbage collection after processing a large batch.
    Useful after semantic matching (Day 12), which holds tensor objects
    that don't always get released immediately by Python's normal GC timing.
    """
    collected = gc.collect()
    logger.info(f"Garbage collection freed {collected} objects")
    return collected


def process_in_chunks(items, chunk_size=5):
    """
    Yield items in small chunks instead of loading everything into memory
    at once -- useful when processing many resumes/JDs in run_* scripts.
    """
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]