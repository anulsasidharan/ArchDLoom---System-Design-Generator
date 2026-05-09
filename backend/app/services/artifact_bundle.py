"""ZIP packaging for generated artifacts."""

from __future__ import annotations

import zipfile
from io import BytesIO


def build_zip_bundle(files: dict[str, bytes]) -> bytes:
    """Return a ZIP archive containing filename -> payload mappings."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, payload in sorted(files.items()):
            zf.writestr(name, payload)
    return buf.getvalue()
