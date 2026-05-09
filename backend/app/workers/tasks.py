"""Generation pipeline executed asynchronously."""

from __future__ import annotations

import base64
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal
from app.domain.generation import GenerationOptions
from app.domain.requirements import ParsedRequirement
from app.exceptions import ClaudeConfigurationError, RequirementParseError
from app.models.generation_job import GenerationJob
from app.models.project import Project
from app.services.claude_client import ClaudeClient
from app.services.component_selector import ComponentSelector
from app.services.mermaid_generator import generate_architecture_mermaid
from app.services.prd_generator import generate_prd_docx
from app.services.requirement_parser import RequirementParser
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _load_options(blob: dict[str, Any]) -> GenerationOptions:
    raw = blob.get("options") or {}
    if isinstance(raw, dict):
        return GenerationOptions.model_validate(raw)
    return GenerationOptions()


@celery_app.task(name="generation.run_job", ignore_result=True)
def run_generation_job(job_id: str) -> None:
    jid = uuid.UUID(job_id)
    db = SessionLocal()
    try:
        _run_job_body(db, jid)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _run_job_body(db: Session, job_id: uuid.UUID) -> None:
    job = db.get(GenerationJob, job_id)
    if job is None:
        logger.error("GenerationJob %s not found", job_id)
        return

    project = db.get(Project, job.project_id) if job.project_id else None
    if project is None:
        _fail_job(db, job, "Project not linked to job")
        return

    settings = get_settings()
    try:
        client = ClaudeClient(settings.anthropic_api_key, model=settings.anthropic_model)
    except ClaudeConfigurationError as e:
        _fail_job(db, job, str(e))
        return

    job.status = "processing"
    job.progress = 5
    job.current_step = "parse_requirements"
    job.started_at = _utcnow()
    project.status = "generating"
    db.commit()

    blob = dict(project.requirements or {})
    user_input = blob.get("user_input")
    if not user_input or not isinstance(user_input, str):
        _fail_job(db, job, "Missing user_input on project requirements")
        return

    options = _load_options(blob)
    parser = RequirementParser(client)

    try:
        parsed = parser.parse(user_input, options)
    except RequirementParseError as e:
        _fail_job(db, job, str(e))
        return

    merged_req = {**blob, "parsed": parsed.model_dump(mode="json")}
    project.requirements = merged_req
    project.name = (parsed.system_name or project.name)[:200]

    job.progress = 30
    job.current_step = "select_components"
    db.commit()

    selector = ComponentSelector(db, client)
    try:
        selection = selector.select(parsed)
    except Exception as e:
        logger.exception("Component selection failed")
        _fail_job(db, job, f"Component selection failed: {e}")
        return

    project.component_selections = selection.model_dump(mode="json")

    job.progress = 60
    job.current_step = "generate_prd"
    db.commit()

    try:
        prd_bytes = generate_prd_docx(parsed, selection, project_title=parsed.system_name)
    except Exception as e:
        logger.exception("PRD generation failed")
        _fail_job(db, job, f"PRD generation failed: {e}")
        return

    job.progress = 80
    job.current_step = "generate_diagram"
    db.commit()

    mermaid = generate_architecture_mermaid(selection, title=parsed.system_name)

    prd_b64 = base64.standard_b64encode(prd_bytes).decode("ascii")
    project.generated_files = {
        "prd.docx": {"encoding": "base64", "data": prd_b64},
        "architecture.mmd": {"encoding": "text", "data": mermaid},
    }
    project.status = "completed"

    job.status = "completed"
    job.progress = 100
    job.current_step = "done"
    job.completed_at = _utcnow()
    job.error_message = None
    db.commit()


def _fail_job(db: Session, job: GenerationJob, message: str) -> None:
    logger.error("Job %s failed: %s", job.id, message)
    job.status = "failed"
    job.error_message = message
    job.completed_at = _utcnow()
    job.current_step = "failed"
    if job.project_id:
        proj = db.get(Project, job.project_id)
        if proj is not None:
            proj.status = "failed"
    db.commit()
