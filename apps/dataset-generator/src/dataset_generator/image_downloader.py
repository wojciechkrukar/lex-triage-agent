"""
Image downloader — fetches public-domain / open-licensed images from URLs,
computes sha256, and returns base64-encoded thumbnail-sized content.

Policy:
- Only downloads images from approved public-domain / CC0 / CC-BY / CC-BY-SA sources.
- Uses Wikimedia 640px thumbnails to keep file size manageable (~50–150 KB each).
- Returns None silently on any network failure — the caller skips missing images.
"""

from __future__ import annotations

import base64
import hashlib
import time
from typing import NamedTuple

import requests

_HEADERS = {
    "User-Agent": (
        "lex-triage-agent/1.0 (legal-email-triage dataset generator; "
        "educational synthetic data; non-commercial)"
    ),
    "Accept": "image/jpeg,image/png,image/*",
}


class DownloadResult(NamedTuple):
    data: bytes
    content_type: str
    final_url: str


def download_image(url: str, timeout: int = 20, retries: int = 3) -> DownloadResult | None:
    """
    Download an image from *url* (follows redirects, e.g. Wikimedia Special:FilePath).
    Retries up to *retries* times on HTTP 429 (rate-limit) with exponential back-off.
    Returns a DownloadResult or None on any failure.
    """
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True)
            if resp.status_code == 429:
                wait = 2 ** attempt * 5  # 5s, 10s, 20s
                time.sleep(wait)
                continue
            if resp.status_code != 200 or not resp.content:
                return None
            ct = resp.headers.get("Content-Type", "image/jpeg")
            # Sanity: must look like an image (>2 KB) to exclude HTML error pages.
            if len(resp.content) < 2048:
                return None
            if "text/html" in ct:
                return None
            return DownloadResult(
                data=resp.content,
                content_type=ct.split(";")[0].strip(),
                final_url=str(resp.url),
            )
        except Exception:
            return None
    return None


def to_b64(data: bytes) -> str:
    """Return base64-encoded string of *data*."""
    return base64.b64encode(data).decode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Return hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def wikimedia_thumb_url(path_hash: str, filename: str, width: int = 640) -> str:
    """
    Build a Wikimedia Commons thumbnail URL from the known path hash.

    Example:
        wikimedia_thumb_url("d/d9", "Car_Accident_in_Sofia.jpg")
        -> "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Car_Accident_in_Sofia.jpg/640px-Car_Accident_in_Sofia.jpg"
    """
    base = "https://upload.wikimedia.org/wikipedia/commons/thumb"
    return f"{base}/{path_hash}/{filename}/{width}px-{filename}"
