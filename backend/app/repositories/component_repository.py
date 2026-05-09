from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.component import Component


class ComponentRepository:
    """CRUD-style access to the component library."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, component_id: uuid.UUID) -> Component | None:
        return self._session.get(Component, component_id)

    def find_by_name(self, name: str) -> Component | None:
        stmt = select(Component).where(Component.name == name).limit(1)
        return self._session.scalars(stmt).first()

    def list_by_category(self, category: str) -> list[Component]:
        stmt = select(Component).where(Component.category == category).order_by(Component.name)
        return list(self._session.scalars(stmt).all())

    def list_all(self) -> list[Component]:
        stmt = select(Component).order_by(Component.category, Component.name)
        return list(self._session.scalars(stmt).all())
