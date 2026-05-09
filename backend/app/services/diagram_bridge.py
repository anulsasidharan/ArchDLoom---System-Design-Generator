"""PNG bridge for architecture diagrams (Mermaid CLI when available, Pillow fallback)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def render_mermaid_to_png(mermaid_source: str, *, title: str = "Architecture") -> bytes:
    """Render Mermaid text to PNG bytes for Word embedding.

    Tries `@mermaid-js/mermaid-cli` (`mmdc`) when present on PATH; otherwise builds a
    readable placeholder image referencing the bundled `.mmd` source.
    """
    mmdc = shutil.which("mmdc")
    if mmdc:
        try:
            return _mermaid_cli_png(mmdc, mermaid_source)
        except Exception:
            logger.warning("mmdc failed; using Pillow fallback", exc_info=True)
    return _fallback_png(mermaid_source, title=title)


def _mermaid_cli_png(mmdc: str, mermaid_source: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "diagram.mmd"
        out = Path(tmp) / "diagram.png"
        src.write_text(mermaid_source, encoding="utf-8")
        pup = os.environ.get("PUPPETEER_EXECUTABLE_PATH", "")
        env = {**os.environ, "PUPPETEER_EXECUTABLE_PATH": pup}
        proc = subprocess.run(
            [mmdc, "-i", str(src), "-o", str(out), "-b", "transparent"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if proc.returncode != 0 or not out.is_file():
            raise RuntimeError(proc.stderr or proc.stdout or "mmdc failed")
        return out.read_bytes()


def _fallback_png(mermaid_source: str, *, title: str) -> bytes:
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_body = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((40, 36), title[:120], fill=(17, 24, 39), font=font_title)
    msg = (
        "Rendered placeholder — install @mermaid-js/mermaid-cli and ensure `mmdc` is on PATH "
        "for pixel-perfect diagrams. The canonical Mermaid source ships as architecture.mmd."
    )
    _wrap_text(draw, msg, (40, 90), w - 80, font_body, fill=(55, 65, 81))

    snippet = mermaid_source.strip().replace("\r\n", "\n")
    if len(snippet) > 1800:
        snippet = snippet[:1797] + "..."
    _wrap_text(draw, snippet, (40, 160), w - 80, font_body, fill=(31, 41, 55))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    max_width: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    x, y = xy
    lines: list[str] = []
    for raw in text.split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        cur: list[str] = []
        for word in words:
            trial = (" ".join(cur + [word])).strip()
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width:
                cur.append(word)
            else:
                if cur:
                    lines.append(" ".join(cur))
                cur = [word]
        if cur:
            lines.append(" ".join(cur))

    line_height = int(draw.textbbox((0, 0), "Ay", font=font)[3] * 1.25) or 18
    for line in lines:
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height
