"""architecture.md from Jinja templates + domain models."""

from __future__ import annotations

from app.domain.components import ArchitecturePattern, ComponentSelectionResult
from app.domain.requirements import ParsedRequirement
from app.services.jinja_env import render_template

_AIML_TEMPLATE_FILES: dict[ArchitecturePattern, str] = {
    ArchitecturePattern.RAG_SYSTEM: "shared/_aiml_rag.md.j2",
    ArchitecturePattern.FINE_TUNING_PIPELINE: "shared/_aiml_finetuning.md.j2",
    ArchitecturePattern.REALTIME_INFERENCE: "shared/_aiml_inference.md.j2",
    ArchitecturePattern.AGENTIC_AI_SYSTEM: "shared/_aiml_agentic.md.j2",
}


def _aiml_narrative_block(pattern: ArchitecturePattern, *, project_title: str) -> str | None:
    tpl = _AIML_TEMPLATE_FILES.get(pattern)
    if not tpl:
        return None
    return render_template(tpl, project_title=project_title)


def generate_architecture_markdown(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
    *,
    mermaid_source: str,
    project_title: str | None = None,
    supplementary_mermaid: str | None = None,
) -> str:
    title = project_title or requirements.system_name
    summary = requirements.summary or (
        f"{title} targets the {requirements.domain} domain with "
        f"{len(requirements.functional_requirements)} functional themes."
    )
    aiml_block = _aiml_narrative_block(
        components.architecture_pattern,
        project_title=title,
    )
    supp = (supplementary_mermaid or "").strip()
    return render_template(
        "documents/architecture.md.j2",
        project_title=title,
        summary_block=summary,
        domain=requirements.domain,
        pattern=components.architecture_pattern.value,
        scale=requirements.scale_metrics,
        nfr=requirements.non_functional_requirements,
        compliance=requirements.compliance_needs,
        component_rows=[(k, components.selections[k]) for k in sorted(components.selections)],
        mermaid_source=mermaid_source.strip(),
        aiml_template_block=aiml_block,
        supplementary_mermaid=supp,
        total_cost=components.total_monthly_cost_usd,
        needs_async=requirements.needs_async_processing,
        has_ai=requirements.has_ai_features,
    )
