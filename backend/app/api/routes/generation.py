"""Generation job enqueue + status polling."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.generation import GenerationOptions
from app.models.generation_job import GenerationJob
from app.models.project import Project
from app.workers.tasks import run_generation_job

router = APIRouter(tags=["generation"])


class GenerateRequest(BaseModel):
    requirement: str = Field(..., min_length=1)
    options: GenerationOptions | None = None


class GenerateResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    status: str
    progress: int
    current_step: str | None = None
    error_message: str | None = None


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
        requirements={"user_input": body.requirement.strip(), "options": opts.model_dump()},
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
