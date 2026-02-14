"""
Simple file-based cache for LLM-generated prompts.
"""

import json
from pathlib import Path

CACHE_FILE = Path(__file__).parent / "prompt_cache.json"
MAX_CACHE_SIZE = 500  # Max cached prompts


def _load_cache() -> dict:
    """Load cache from file."""
    if not CACHE_FILE.exists():
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def _save_cache(cache: dict):
    """Save cache to file, trimming if too large."""
    # Trim if too large (keep most recent)
    if len(cache) > MAX_CACHE_SIZE:
        items = list(cache.items())
        cache = dict(items[-MAX_CACHE_SIZE:])

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_cached(key: str) -> str | None:
    """Get a cached value by key."""
    cache = _load_cache()
    return cache.get(key)


def set_cached(key: str, prompt: str):
    """Set a cached value."""
    cache = _load_cache()
    cache[key] = prompt
    _save_cache(cache)


def clear_cache():
    """Clear the entire cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
