"""
Digest cache management.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

_DIGEST_CACHE_PATH = Path("data/last_digest.json")


def write_last_digest(
    text: str,
    hours: int,
    logger: logging.Logger,
) -> None:
    """Cache the latest generated digest."""
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hours": hours,
        "text": text,
    }

    try:
        _DIGEST_CACHE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp_path = _DIGEST_CACHE_PATH.with_suffix(".tmp")

        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )

        tmp_path.replace(_DIGEST_CACHE_PATH)

    except OSError:
        logger.exception("Caching digest failed")


def read_last_digest() -> dict | None:
    """Read cached digest."""
    try:
        data = json.loads(_DIGEST_CACHE_PATH.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None

    if isinstance(data, dict) and isinstance(data.get("text"), str):
        return data

    return None
