"""Compute uniform scale and translation to fit an icon inside a node bounding box."""

from __future__ import annotations

from typing import Any


def fit_icon_in_box(
    box_w: float,
    box_h: float,
    icon_w: float,
    icon_h: float,
    *,
    padding: float = 6.0,
    max_fill_ratio: float = 0.42,
) -> tuple[float, float, float]:
    """Return ``(scale, translate_x, translate_y)`` in the box's coordinate space.

    The icon is scaled uniformly, centered in the box, and capped by ``max_fill_ratio`` of the
    smaller box dimension so labels remain readable on Mermaid diagrams.
    """
    if box_w <= 0 or box_h <= 0 or icon_w <= 0 or icon_h <= 0:
        return 1.0, 0.0, 0.0

    inner_w = max(box_w - 2 * padding, 1.0)
    inner_h = max(box_h - 2 * padding, 1.0)
    cap = min(inner_w, inner_h) * max_fill_ratio
    scale_w = cap / icon_w
    scale_h = cap / icon_h
    scale = min(scale_w, scale_h, 1.0)

    drawn_w = icon_w * scale
    drawn_h = icon_h * scale
    tx = (box_w - drawn_w) / 2
    ty = (box_h - drawn_h) / 2
    return scale, tx, ty


def parse_svg_dimensions(svg_root: Any) -> tuple[float, float]:
    """Best-effort width/height from root ``svg`` element (lxml Element)."""
    from lxml import etree

    if etree.QName(svg_root).localname != "svg":
        return 64.0, 64.0
    w = svg_root.get("width")
    h = svg_root.get("height")
    vb = svg_root.get("viewBox")
    fw, fh = 64.0, 64.0
    if vb:
        parts = vb.replace(",", " ").split()
        if len(parts) == 4:
            try:
                fw = float(parts[2])
                fh = float(parts[3])
            except ValueError:
                pass
    if w and h:
        try:
            ws = str(w).strip().rstrip("px")
            hs = str(h).strip().rstrip("px")
            fw = float(ws)
            fh = float(hs)
        except ValueError:
            pass
    return max(fw, 1.0), max(fh, 1.0)
