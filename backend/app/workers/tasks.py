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
from app.exceptions import ClaudeConfigurationError, RequirementParseError
from app.models.generation_job import GenerationJob
from app.models.project import Project
from app.services.architecture_markdown import generate_architecture_markdown
from app.services.artifact_bundle import build_zip_bundle
from app.services.claude_client import ClaudeClient
from app.services.component_selector import ComponentSelector
from app.services.diagram_bridge import render_mermaid_to_png, render_mermaid_to_svg
from app.services.diagram_renderer import render_architecture_diagram_svg
from app.services.enterprise import (
    build_compliance_mapping,
    build_hadr_strategy,
    build_observability_plan,
    build_security_plan,
    estimate_costs,
    generate_network_diagram,
)
from app.services.evolution_generator import generate_evolution_markdown
from app.services.hld_generator import generate_hld_docx
from app.services.lld_generator import generate_lld_docx
from app.services.mermaid_generator import (
    generate_aiml_supplementary_mermaid,
    generate_architecture_mermaid,
)
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

    selected_docs: list[str] = blob.get("selected_documents") or []
    # Empty list = generate everything (backwards-compat)
    def _want(key: str) -> bool:
        return not selected_docs or key in selected_docs

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

    job.progress = 25
    job.current_step = "select_components"
    db.commit()

    selector = ComponentSelector(db, client)
    try:
        selection = selector.select(parsed, options)
    except Exception as e:
        logger.exception("Component selection failed")
        _fail_job(db, job, f"Component selection failed: {e}")
        return

    project.component_selections = selection.model_dump(mode="json")

    job.progress = 45
    job.current_step = "enterprise_analysis"
    db.commit()

    try:
        cost_estimate = estimate_costs(parsed, selection)
        compliance_mapping = build_compliance_mapping(parsed)
        security_plan = build_security_plan(parsed, selection, compliance_mapping)
        hadr_strategy = build_hadr_strategy(parsed, selection)
        observability_plan = build_observability_plan(parsed, selection)
    except Exception as e:
        logger.exception("Enterprise analysis failed")
        _fail_job(db, job, f"Enterprise analysis failed: {e}")
        return

    job.progress = 55
    job.current_step = "generate_diagram"
    db.commit()

    mermaid = generate_architecture_mermaid(selection, title=parsed.system_name)
    flow_mermaid = generate_aiml_supplementary_mermaid(
        selection,
        title=parsed.system_name or "Architecture",
    )
    network_mermaid = generate_network_diagram(
        selection,
        title=parsed.system_name or "Architecture",
    )

    job.progress = 62
    job.current_step = "render_architecture_markdown"
    db.commit()

    architecture_md: str | None = None
    evolution_md: str | None = None
    try:
        if _want("architecture"):
            architecture_md = generate_architecture_markdown(
                parsed,
                selection,
                mermaid_source=mermaid,
                project_title=parsed.system_name,
                supplementary_mermaid=flow_mermaid or None,
                network_mermaid=network_mermaid or None,
                cost=cost_estimate,
                compliance_mapping=compliance_mapping,
                security=security_plan,
                hadr=hadr_strategy,
                observability=observability_plan,
            )
        if _want("evolution"):
            evolution_md = generate_evolution_markdown(
                parsed,
                selection,
                project_title=parsed.system_name,
            )
    except Exception as e:
        logger.exception("Markdown artifact generation failed")
        _fail_job(db, job, f"Markdown artifact generation failed: {e}")
        return

    job.progress = 68
    job.current_step = "render_diagram_png"
    db.commit()

    try:
        diagram_png = render_mermaid_to_png(mermaid, title=parsed.system_name)
    except Exception as e:
        logger.exception("Diagram PNG rendering failed")
        _fail_job(db, job, f"Diagram rendering failed: {e}")
        return

    network_png: bytes | None = None
    network_svg: str | None = None
    try:
        network_png = render_mermaid_to_png(network_mermaid, title=parsed.system_name or "Network")
    except Exception:
        logger.warning("Network PNG rendering failed; storing Mermaid source only", exc_info=True)
    try:
        network_svg = render_mermaid_to_svg(
            network_mermaid,
            title=parsed.system_name or "Network",
        )
    except Exception:
        logger.warning("Network SVG rendering failed; storing Mermaid source only", exc_info=True)

    try:
        enhanced_svg, svg_warnings = render_architecture_diagram_svg(
            mermaid,
            selection,
            diagram_title=parsed.system_name or "Architecture",
        )
        if svg_warnings:
            logger.info("Diagram SVG overlay notes: %s", "; ".join(svg_warnings[:12]))
    except Exception:
        logger.warning("Enhanced SVG overlay failed; storing base Mermaid SVG", exc_info=True)
        enhanced_svg = render_mermaid_to_svg(mermaid, title=parsed.system_name or "Architecture")

    job.progress = 74
    job.current_step = "generate_documents"
    db.commit()

    prd_bytes: bytes | None = None
    hld_bytes: bytes | None = None
    lld_bytes: bytes | None = None
    try:
        if _want("prd"):
            prd_bytes = generate_prd_docx(
                parsed,
                selection,
                project_title=parsed.system_name,
                diagram_png=diagram_png,
            )
        if _want("hld"):
            hld_bytes = generate_hld_docx(
                parsed,
                selection,
                project_title=parsed.system_name,
                diagram_png=diagram_png,
                network_png=network_png,
                cost=cost_estimate,
                compliance_mapping=compliance_mapping,
                security=security_plan,
                hadr=hadr_strategy,
                observability=observability_plan,
            )
        if _want("lld"):
            lld_bytes = generate_lld_docx(
                parsed,
                selection,
                project_title=parsed.system_name,
                diagram_png=diagram_png,
            )
    except Exception as e:
        logger.exception("Word artifact generation failed")
        _fail_job(db, job, f"Word artifact generation failed: {e}")
        return

    job.progress = 88
    job.current_step = "zip_bundle"
    db.commit()

    bundle_files: dict[str, bytes] = {}
    if prd_bytes:
        bundle_files["prd.docx"] = prd_bytes
    if hld_bytes:
        bundle_files["hld.docx"] = hld_bytes
    if lld_bytes:
        bundle_files["lld.docx"] = lld_bytes
    if evolution_md:
        bundle_files["evolution.md"] = evolution_md.encode("utf-8")
    if architecture_md:
        bundle_files["architecture.md"] = architecture_md.encode("utf-8")
        bundle_files["architecture.mmd"] = mermaid.encode("utf-8")
        bundle_files["architecture.svg"] = enhanced_svg.encode("utf-8")
        bundle_files["architecture.png"] = diagram_png
        bundle_files["network.mmd"] = network_mermaid.encode("utf-8")
        if flow_mermaid.strip():
            bundle_files["architecture-flow.mmd"] = flow_mermaid.encode("utf-8")
        if network_svg:
            bundle_files["network.svg"] = network_svg.encode("utf-8")
        if network_png:
            bundle_files["network.png"] = network_png

    try:
        bundle_zip = build_zip_bundle(bundle_files)
    except Exception as e:
        logger.exception("ZIP bundling failed")
        _fail_job(db, job, f"ZIP bundling failed: {e}")
        return

    png_b64 = base64.standard_b64encode(diagram_png).decode("ascii")
    zip_b64 = base64.standard_b64encode(bundle_zip).decode("ascii")
    svg_b64 = base64.standard_b64encode(enhanced_svg.encode("utf-8")).decode("ascii")

    # Always store diagram artifacts for the frontend viewer
    gen_files: dict[str, dict[str, str]] = {
        "architecture.mmd": {"encoding": "text", "data": mermaid},
        "architecture.svg": {"encoding": "base64", "data": svg_b64},
        "architecture.png": {"encoding": "base64", "data": png_b64},
        "network.mmd": {"encoding": "text", "data": network_mermaid},
        "bundle.zip": {"encoding": "base64", "data": zip_b64},
    }
    if prd_bytes:
        gen_files["prd.docx"] = {"encoding": "base64", "data": base64.standard_b64encode(prd_bytes).decode("ascii")}
    if hld_bytes:
        gen_files["hld.docx"] = {"encoding": "base64", "data": base64.standard_b64encode(hld_bytes).decode("ascii")}
    if lld_bytes:
        gen_files["lld.docx"] = {"encoding": "base64", "data": base64.standard_b64encode(lld_bytes).decode("ascii")}
    if architecture_md:
        gen_files["architecture.md"] = {"encoding": "text", "data": architecture_md}
    if evolution_md:
        gen_files["evolution.md"] = {"encoding": "text", "data": evolution_md}
    if flow_mermaid.strip():
        gen_files["architecture-flow.mmd"] = {"encoding": "text", "data": flow_mermaid}
    if network_svg:
        gen_files["network.svg"] = {
            "encoding": "base64",
            "data": base64.standard_b64encode(network_svg.encode("utf-8")).decode("ascii"),
        }
    if network_png:
        gen_files["network.png"] = {
            "encoding": "base64",
            "data": base64.standard_b64encode(network_png).decode("ascii"),
        }

    enterprise_blob: dict[str, Any] = {
        "cost": cost_estimate.model_dump(mode="json"),
        "compliance": compliance_mapping.model_dump(mode="json"),
        "security": security_plan.model_dump(mode="json"),
        "hadr": hadr_strategy.model_dump(mode="json"),
        "observability": observability_plan.model_dump(mode="json"),
    }
    project.generated_files = {**gen_files, "enterprise": enterprise_blob}
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
