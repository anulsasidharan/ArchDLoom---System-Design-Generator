"""Parse Mermaid-rendered SVG and inject per-node icon groups plus annotation hooks."""

from __future__ import annotations

import logging
import re
from io import BytesIO

from lxml import etree
from PIL import Image

from app.services.icon_layout import fit_icon_in_box, parse_svg_dimensions
from app.services.icon_storage import icon_to_data_uri

logger = logging.getLogger(__name__)

SVG_NS = "http://www.w3.org/2000/svg"
_XLINK_NS = "http://www.w3.org/1999/xlink"


def _local_tag(el: etree._Element) -> str:
    return etree.QName(el).localname


def _union_bbox(children: list[etree._Element]) -> tuple[float, float, float, float] | None:
    """Return ``x, y, width, height`` covering rect/polygon/ellipse children."""
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    found = False

    for el in children:
        tag = _local_tag(el)
        if tag == "rect":
            try:
                x = float(el.get("x", "0"))
                y = float(el.get("y", "0"))
                w = float(el.get("width", "0"))
                h = float(el.get("height", "0"))
            except ValueError:
                continue
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)
            found = True
        elif tag == "polygon" and el.get("points"):
            pts = re.findall(r"[-+]?\d*\.?\d+", el.get("points", ""))
            nums = [float(p) for p in pts]
            if len(nums) >= 2:
                xs = nums[0::2]
                ys = nums[1::2]
                min_x = min(min_x, min(xs))
                max_x = max(max_x, max(xs))
                min_y = min(min_y, min(ys))
                max_y = max(max_y, max(ys))
                found = True
        elif tag == "ellipse":
            try:
                cx = float(el.get("cx", "0"))
                cy = float(el.get("cy", "0"))
                rx = float(el.get("rx", "0"))
                ry = float(el.get("ry", "0"))
            except ValueError:
                continue
            min_x = min(min_x, cx - rx)
            max_x = max(max_x, cx + rx)
            min_y = min(min_y, cy - ry)
            max_y = max(max_y, cy + ry)
            found = True

    if not found:
        return None
    return min_x, min_y, max_x - min_x, max_y - min_y


def find_node_root(svg_root: etree._Element, node_id: str) -> etree._Element | None:
    """Locate the ``<g>`` representing a flowchart node by Mermaid id hint."""
    needle = node_id.strip()
    ranked: list[tuple[int, etree._Element]] = []
    for g in svg_root.iter():
        if _local_tag(g) != "g":
            continue
        gid = (g.get("id") or "").strip()
        cls = g.get("class") or ""
        score = 0
        if gid == needle:
            score = 100
        elif gid.endswith("-" + needle) or gid.endswith(needle):
            score = 80
        elif needle in gid:
            score = 40
        if score == 0:
            continue
        if "node" in cls:
            score += 5
        ranked.append((score, g))
    if not ranked:
        return None
    ranked.sort(key=lambda x: -x[0])
    return ranked[0][1]


def _suppress_mermaid_node_labels(node_g: etree._Element) -> None:
    """Hide Mermaid HTML labels so our icon + caption replace them instead of stacking."""
    for el in node_g.iterdescendants():
        if _local_tag(el) == "foreignObject":
            el.set("visibility", "hidden")
            el.set("pointer-events", "none")


def collect_outer_bbox(node_g: etree._Element) -> tuple[float, float, float, float] | None:
    shapes: list[etree._Element] = []
    for child in node_g:
        if _local_tag(child) in {"rect", "polygon", "ellipse", "path"}:
            shapes.append(child)
        elif _local_tag(child) == "g":
            shapes.extend([c for c in child if _local_tag(c) in {"rect", "polygon", "ellipse"}])
    if not shapes:
        for desc in node_g.iterdescendants():
            if _local_tag(desc) in {"rect", "polygon", "ellipse"}:
                shapes.append(desc)
    return _union_bbox(shapes)


def format_annotation_line(
    *,
    monthly_cost_usd: float | None,
    sla: str | None,
    vendor: str | None,
) -> str | None:
    parts: list[str] = []
    if monthly_cost_usd is not None:
        parts.append(f"${monthly_cost_usd:,.0f}/mo")
    if sla:
        parts.append(f"SLA: {sla}")
    elif vendor:
        parts.append(vendor)
    if not parts:
        return None
    return " · ".join(parts)


def _icon_intrinsic_size(icon_bytes: bytes) -> tuple[float, float]:
    if icon_bytes.startswith(b"\x89PNG") or icon_bytes.startswith(b"\xff\xd8\xff"):
        try:
            with Image.open(BytesIO(icon_bytes)) as im:
                w, h = im.size
                return float(max(w, 1)), float(max(h, 1))
        except OSError:
            return 64.0, 64.0
    try:
        icon_doc = etree.fromstring(icon_bytes, parser=etree.XMLParser(recover=True))
        return parse_svg_dimensions(icon_doc)
    except etree.XMLSyntaxError:
        return 64.0, 64.0


def _truncate_caption(s: str, max_len: int = 44) -> str:
    s = s.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def inject_overlay_for_node(
    svg_root: etree._Element,
    node_id: str,
    icon_bytes: bytes,
    annotation: str | None,
    *,
    caption: str | None = None,
    overlay_class: str = "archdloom-icon-overlay",
) -> bool:
    """Insert icon, optional in-node caption, and optional annotation. Returns True if attached."""
    node_g = find_node_root(svg_root, node_id)
    if node_g is None:
        logger.debug("No SVG node group matched id hint %r", node_id)
        return False

    bbox = collect_outer_bbox(node_g)
    if bbox is None:
        logger.debug("Could not compute bbox for node %r", node_id)
        return False
    bx, by, bw, bh = bbox

    if caption:
        _suppress_mermaid_node_labels(node_g)

    iw, ih = _icon_intrinsic_size(icon_bytes)
    data_uri = icon_to_data_uri(icon_bytes)

    group = etree.Element(f"{{{SVG_NS}}}g")
    group.set("class", overlay_class)

    if caption:
        caption_reserve = min(max(15.0, bh * 0.22), bh * 0.36)
        icon_band_h = max(bh - caption_reserve, min(bw, bh) * 0.5)
        scale, tx, ty = fit_icon_in_box(
            bw,
            icon_band_h,
            iw,
            ih,
            padding=5.0,
            max_fill_ratio=0.94,
        )
        inner = etree.Element(f"{{{SVG_NS}}}g")
        inner.set(
            "transform",
            f"translate({bx + tx:.3f},{by + ty:.3f}) scale({scale:.6f})",
        )
        img = etree.Element(f"{{{SVG_NS}}}image")
        img.set("href", data_uri)
        img.set(f"{{{_XLINK_NS}}}href", data_uri)
        img.set("width", f"{iw:.3f}")
        img.set("height", f"{ih:.3f}")
        inner.append(img)
        group.append(inner)

        cap = _truncate_caption(caption)
        cap_y = by + icon_band_h + min(12.0, caption_reserve * 0.55)
        cap_el = etree.Element(f"{{{SVG_NS}}}text")
        cap_el.set("x", f"{bx + bw / 2:.3f}")
        cap_el.set("y", f"{cap_y:.3f}")
        cap_el.set("text-anchor", "middle")
        fs = min(12.0, max(9.0, bh * 0.14))
        cap_el.set("font-size", f"{fs:.1f}")
        cap_el.set("font-family", "system-ui, Segoe UI, Arial, Helvetica, sans-serif")
        cap_el.set("font-weight", "600")
        cap_el.set("fill", "#111827")
        cap_el.set("class", "archdloom-node-caption")
        cap_el.text = cap
        group.append(cap_el)
    else:
        scale, tx, ty = fit_icon_in_box(
            bw,
            bh,
            iw,
            ih,
            padding=6.0,
            max_fill_ratio=0.62,
        )
        inner = etree.Element(f"{{{SVG_NS}}}g")
        inner.set(
            "transform",
            f"translate({bx + tx:.3f},{by + ty:.3f}) scale({scale:.6f})",
        )
        img = etree.Element(f"{{{SVG_NS}}}image")
        img.set("href", data_uri)
        img.set(f"{{{_XLINK_NS}}}href", data_uri)
        img.set("width", f"{iw:.3f}")
        img.set("height", f"{ih:.3f}")
        inner.append(img)
        group.append(inner)

    if annotation:
        ty_rel = by + bh + 11
        tx_mid = bx + bw / 2
        text_el = etree.Element(f"{{{SVG_NS}}}text")
        text_el.set("x", f"{tx_mid:.3f}")
        text_el.set("y", f"{ty_rel:.3f}")
        text_el.set("text-anchor", "middle")
        text_el.set("font-size", "9.5")
        text_el.set("font-family", "system-ui, Segoe UI, Arial, Helvetica, sans-serif")
        text_el.set("fill", "#4b5563")
        text_el.set("class", "archdloom-node-annotation")
        text_el.text = annotation[:160]
        group.append(text_el)

    node_g.append(group)
    return True


def overlay_icons_on_mermaid_svg(
    svg_xml: str,
    overlays: list[tuple[str, bytes, str | None, str | None]]
    | list[tuple[str, bytes, str | None]],
) -> tuple[str, list[str]]:
    """Apply overlays: ``(node_id, icon, annotation, caption)``; ``caption`` may be omitted."""
    warnings: list[str] = []
    try:
        root = etree.fromstring(svg_xml.encode("utf-8"), parser=etree.XMLParser(huge_tree=True))
    except etree.XMLSyntaxError as e:
        return svg_xml, [f"parse_error:{e}"]

    if _local_tag(root) != "svg":
        return svg_xml, ["root_not_svg"]

    for row in overlays:
        node_id = row[0]
        icon_bytes = row[1]
        ann = row[2]
        cap: str | None = row[3] if len(row) > 3 else None
        ok = inject_overlay_for_node(root, node_id, icon_bytes, ann, caption=cap)
        if not ok:
            warnings.append(f"missing_node:{node_id}")

    out = etree.tostring(root, encoding="unicode", pretty_print=False)
    return out, warnings
