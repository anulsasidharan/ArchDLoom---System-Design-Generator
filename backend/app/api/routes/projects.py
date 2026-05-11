"""CRUD routes for saved projects."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    domain: str | None
    status: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


def _serialize(p: Project) -> dict[str, Any]:
    return {
        "id": str(p.id),
        "name": p.name,
        "description": p.description,
        "domain": p.domain,
        "status": p.status,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, Any]]:
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()
    return [_serialize(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return _serialize(p)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()
