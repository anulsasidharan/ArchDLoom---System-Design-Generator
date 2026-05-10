"""Generation job enqueue + status polling."""

from __future__ import annotations

import base64
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.generation import GenerationOptions
from app.models.generation_job import GenerationJob
from app.models.project import Project
from app.services.artifact_bundle import build_zip_bundle
from app.workers.tasks import run_generation_job

router = APIRouter(tags=["generation"])


class GenerateRequest(BaseModel):
    requirement: str = Field(..., min_length=1)
    options: GenerationOptions | None = None
    selected_documents: list[str] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    status: str
    progress: int
    current_step: str | None = None
    error_message: str | None = None


class JobPreviewResponse(BaseModel):
    """Artifacts for diagram viewer + component detail panel (completed jobs)."""

    status: str
    mermaid: str | None = None
    svg: str | None = None
    component_selections: dict[str, Any] = Field(default_factory=dict)


def _preview_title(text: str, max_len: int = 120) -> str:
    line = text.strip().split("\n")[0].strip()
    if not line:
        return "Untitled design"
    if len(line) > max_len:
        return line[: max_len - 1] + "…"
    return line


@router.post("/generate", status_code=202, response_model=GenerateResponse)
def enqueue_generation(body: GenerateRequest, db: Session = Depends(get_db)) -> GenerateResponse:
    opts = body.options or GenerationOptions()
    project = Project(
        name=_preview_title(body.requirement),
        requirements={
            "user_input": body.requirement.strip(),
            "options": opts.model_dump(),
            "selected_documents": body.selected_documents,
        },
        component_selections={},
        status="pending",
    )
    db.add(project)
    db.flush()
    job = GenerationJob(project_id=project.id, status="queued", progress=0)
    db.add(job)
    db.commit()
    db.refresh(job)
    run_generation_job.delay(str(job.id))
    return GenerateResponse(job_id=str(job.id))


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
def job_status(job_id: UUID, db: Session = Depends(get_db)) -> JobStatusResponse:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
        error_message=job.error_message,
    )


def _decode_generated_text(files: dict[str, Any], key: str) -> str | None:
    entry = files.get(key)
    if not isinstance(entry, dict):
        return None
    enc = entry.get("encoding")
    data = entry.get("data")
    if enc == "text" and isinstance(data, str):
        return data
    if enc == "base64" and isinstance(data, str):
        return base64.standard_b64decode(data).decode("utf-8")
    return None


@router.get("/jobs/{job_id}/preview", response_model=JobPreviewResponse)
def job_preview(job_id: UUID, db: Session = Depends(get_db)) -> JobPreviewResponse:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.project_id is None:
        raise HTTPException(status_code=404, detail="Project not linked to job")
    project = db.get(Project, job.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    files = dict(project.generated_files or {})
    mermaid = _decode_generated_text(files, "architecture.mmd")
    svg = _decode_generated_text(files, "architecture.svg")
    raw = project.component_selections if isinstance(project.component_selections, dict) else {}
    # stored as ComponentSelectionResult.model_dump() → unwrap inner "selections" dict
    selections = raw.get("selections", raw)
    return JobPreviewResponse(
        status=job.status,
        mermaid=mermaid,
        svg=svg,
        component_selections=selections,
    )


def _decode_generated_blob(entry: dict[str, Any]) -> bytes:
    enc = entry.get("encoding")
    data = entry.get("data")
    if enc == "base64" and isinstance(data, str):
        return base64.standard_b64decode(data)
    if enc == "text" and isinstance(data, str):
        return data.encode("utf-8")
    raise HTTPException(status_code=500, detail="Malformed generated artifact entry")


def _artifact_zip_bytes(files: dict[str, Any]) -> bytes:
    bundle = files.get("bundle.zip")
    if isinstance(bundle, dict) and bundle.get("encoding") == "base64":
        return _decode_generated_blob(bundle)

    keys = (
        "prd.docx",
        "hld.docx",
        "lld.docx",
        "architecture.md",
        "evolution.md",
        "architecture.mmd",
        "architecture-flow.mmd",
        "architecture.svg",
        "architecture.png",
        "network.mmd",
        "network.svg",
        "network.png",
    )
    raw: dict[str, bytes] = {}
    for key in keys:
        entry = files.get(key)
        if isinstance(entry, dict):
            raw[key] = _decode_generated_blob(entry)
    if not raw:
        raise HTTPException(status_code=404, detail="No downloadable artifacts on project")
    return build_zip_bundle(raw)


@router.get("/jobs/{job_id}/download")
def download_job_bundle(job_id: UUID, db: Session = Depends(get_db)) -> Response:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=409, detail="Job not completed yet")
    if job.project_id is None:
        raise HTTPException(status_code=404, detail="Project missing for job")

    project = db.get(Project, job.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    files = dict(project.generated_files or {})
    payload = _artifact_zip_bytes(files)
    filename = f"archdloom-{job_id}.zip"
    return Response(
        content=payload,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
