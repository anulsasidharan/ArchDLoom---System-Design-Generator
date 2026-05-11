"""Read-only routes for the component library."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.component import Component

router = APIRouter(prefix="/components", tags=["components"])


def _serialize(c: Component) -> dict[str, Any]:
    return {
        "id": str(c.id),
        "name": c.name,
        "category": c.category,
        "vendor": c.vendor,
        "icon_url": c.icon_url,
        "features": c.features or [],
        "trade_offs": c.trade_offs or None,
        "pricing_model": c.pricing_model,
        "base_cost_usd": c.base_cost_usd,
        "selection_criteria": c.selection_criteria or None,
        "docs_url": c.docs_url,
    }


@router.get("")
def list_components(
    db: Annotated[Session, Depends(get_db)],
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    q = db.query(Component)
    if category:
        q = q.filter(Component.category == category)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            Component.name.ilike(pattern) | Component.vendor.ilike(pattern)
        )
    return [_serialize(c) for c in q.order_by(Component.category, Component.name).all()]


@router.get("/{component_id}")
def get_component(
    component_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    c = db.get(Component, component_id)
    if not c:
        raise HTTPException(status_code=404, detail="Component not found")
    return _serialize(c)
