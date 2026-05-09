"""architecture.md from Jinja templates + domain models."""

from __future__ import annotations

from app.domain.components import ComponentSelectionResult
from app.domain.requirements import ParsedRequirement
from app.services.jinja_env import render_template


def generate_architecture_markdown(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
    *,
    mermaid_source: str,
    project_title: str | None = None,
) -> str:
    title = project_title or requirements.system_name
    summary = requirements.summary or (
        f"{title} targets the {requirements.domain} domain with "
        f"{len(requirements.functional_requirements)} functional themes."
    )
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
        total_cost=components.total_monthly_cost_usd,
        needs_async=requirements.needs_async_processing,
        has_ai=requirements.has_ai_features,
    )
