"""Diagram overlay and layout helpers."""

from app.services.icon_layout import fit_icon_in_box
from app.services.svg_overlay import overlay_icons_on_mermaid_svg


def test_fit_icon_in_box_scales_down() -> None:
    scale, tx, ty = fit_icon_in_box(100, 80, 64, 64, padding=4)
    assert scale < 1.0 or scale == 1.0
    assert tx >= 0 and ty >= 0


def test_overlay_injects_foreign_markup() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="120">
      <g id="GW" class="node default">
        <rect x="10" y="10" width="120" height="56" fill="#fff" stroke="#333"/>
      </g>
    </svg>"""
    icon = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="blue"/></svg>'
    out, warns = overlay_icons_on_mermaid_svg(svg, [("GW", icon, "$100/mo")])
    assert "archdloom-icon-overlay" in out
    assert not any(w.startswith("missing_node") for w in warns)
