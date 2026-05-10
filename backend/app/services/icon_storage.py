"""Resolve icon assets from local paths, HTTP(S), or S3 stubs."""

from __future__ import annotations

import base64
import logging
import urllib.request
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)

_PLACEHOLDER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="8" fill="#e5e7eb" stroke="#9ca3af"/>'
    '<text x="32" y="38" font-size="28" text-anchor="middle" fill="#374151">?</text>'
    "</svg>"
).encode("utf-8")


def placeholder_icon_bytes() -> bytes:
    return _PLACEHOLDER_SVG


class S3IconStorageStub:
    """Stub for future boto3 S3 reads; logs and returns None so callers use placeholders."""

    def __init__(self, bucket: str | None, region: str | None) -> None:
        self._bucket = bucket
        self._region = region

    def fetch_uri(self, uri: str) -> bytes | None:
        logger.info(
            "S3 icon stub: would fetch %s (bucket=%s region=%s)",
            uri,
            self._bucket,
            self._region,
        )
        return None


def _repo_icons_root() -> Path:
    settings = get_settings()
    if settings.icon_assets_root and str(settings.icon_assets_root).strip():
        return Path(settings.icon_assets_root).expanduser().resolve()
    # backend/app/services/icon_storage.py -> parents[2] == backend/
    backend_root = Path(__file__).resolve().parents[2]
    return (backend_root / "static" / "icons").resolve()


def resolve_icon_bytes(icon_url: str | None, *, category: str = "") -> bytes:
    """Return SVG or raster bytes; never raises — falls back to a neutral placeholder."""
    if not icon_url or not str(icon_url).strip():
        return _PLACEHOLDER_SVG

    raw = str(icon_url).strip()

    if raw.startswith("s3://"):
        stub = S3IconStorageStub(
            get_settings().s3_bucket_name,
            get_settings().s3_region,
        )
        got = stub.fetch_uri(raw)
        return got if got else _PLACEHOLDER_SVG

    if raw.startswith(("http://", "https://")):
        try:
            req = urllib.request.Request(raw, headers={"User-Agent": "ArchDLoom/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if data:
                    return data
        except Exception:
            logger.warning("HTTP icon fetch failed for %s", raw, exc_info=True)
        return _PLACEHOLDER_SVG

    # Strip leading /icons/ prefix (public URL convention) to get local path
    local_raw = raw
    if local_raw.startswith("/icons/"):
        local_raw = local_raw[len("/icons/"):]

    path = Path(local_raw)
    if not path.is_absolute():
        path = _repo_icons_root() / local_raw.lstrip("/\\")
    try:
        if path.is_file():
            return path.read_bytes()
    except OSError:
        logger.warning("Local icon read failed: %s", path)

    return _PLACEHOLDER_SVG


def svg_to_data_uri(svg_bytes: bytes) -> str:
    b64 = base64.standard_b64encode(svg_bytes).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def icon_to_data_uri(icon_bytes: bytes) -> str:
    """Build a data URI for SVG, PNG, or JPEG icon payloads."""
    if icon_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        b64 = base64.standard_b64encode(icon_bytes).decode("ascii")
        return f"data:image/png;base64,{b64}"
    if icon_bytes.startswith(b"\xff\xd8\xff"):
        b64 = base64.standard_b64encode(icon_bytes).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    return svg_to_data_uri(icon_bytes)
