"""Orchestrate Mermaid SVG rendering with icon overlays and annotations."""

from __future__ import annotations

import logging

from app.domain.components import ComponentSelectionResult
from app.services.diagram_bridge import render_mermaid_to_svg
from app.services.icon_storage import resolve_icon_bytes
from app.services.mermaid_generator import mermaid_category_to_node_ids
from app.services.svg_overlay import format_annotation_line, overlay_icons_on_mermaid_svg

logger = logging.getLogger(__name__)


def build_overlay_tuples(
    selection: ComponentSelectionResult,
) -> list[tuple[str, bytes, str | None, str | None]]:
    """Resolve icons, cost line, and display caption per mapped node id."""
    mapping = mermaid_category_to_node_ids(selection.architecture_pattern)
    overlays: list[tuple[str, bytes, str | None, str | None]] = []
    for cat, decision in selection.selections.items():
        node_id = mapping.get(cat)
        if not node_id:
            continue
        icon_bytes = resolve_icon_bytes(decision.selected.icon_url, category=cat)
        ann = format_annotation_line(
            monthly_cost_usd=decision.estimated_monthly_cost_usd,
            sla=decision.selected.sla,
            vendor=decision.selected.vendor,
        )
        cap = (decision.selected.name or "").strip() or None
        overlays.append((node_id, icon_bytes, ann, cap))
    if not overlays:
        logger.debug("No overlays resolved for diagram pattern %s", selection.architecture_pattern)
    return overlays


def render_architecture_diagram_svg(
    mermaid_source: str,
    selection: ComponentSelectionResult,
    *,
    diagram_title: str = "Architecture",
) -> tuple[str, list[str]]:
    """Return overlaid SVG markup plus overlay warnings (missing nodes, parse issues)."""
    base_svg = render_mermaid_to_svg(mermaid_source, title=diagram_title)
    tuples = build_overlay_tuples(selection)
    return overlay_icons_on_mermaid_svg(base_svg, tuples)
