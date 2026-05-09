"""Evolution roadmap markdown via shared Jinja templates."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.components import ComponentSelectionResult
from app.domain.requirements import ParsedRequirement
from app.services.jinja_env import render_template
from app.services.mermaid_generator import generate_architecture_mermaid


@dataclass(frozen=True)
class _Phase:
    name: str
    focus: str
    mermaid: str
    strengths: list[str]
    limitations: list[str]
    triggers: list[str]
    migrations: list[str]


def generate_evolution_markdown(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
    *,
    project_title: str | None = None,
) -> str:
    title = project_title or requirements.system_name
    sm = requirements.scale_metrics
    mvp_u = sm.mvp_users or 5_000
    growth_u = sm.growth_users or max(mvp_u * 10, 50_000)

    phases = [
        _Phase(
            name="MVP",
            focus=(
                f"Ship core journeys quickly with minimal ops overhead "
                f"(~≤{mvp_u:,} active users)."
            ),
            mermaid=generate_architecture_mermaid(components, title=f"{title} — MVP"),
            strengths=[
                "Fast iteration and narrow blast radius",
                "Managed services reduce undifferentiated ops",
                "Clear ownership for a small team",
            ],
            limitations=[
                "Single-region posture may violate future residency needs",
                "Manual release gates don't scale past a handful of services",
                "Backup and DR drills often deferred early",
            ],
            triggers=[
                "Sustained latency regression vs product SLO",
                "Deployment frequency blocked by manual steps",
                "Database CPU/storage trending toward limits",
            ],
            migrations=[
                "Introduce automated CI/CD with staged rollouts",
                "Split read/write paths and add caching where hot spots emerge",
                "Promote observability baselines (RED metrics + tracing)",
            ],
        ),
        _Phase(
            name="Growth",
            focus=f"Scale throughput and reliability for roughly {mvp_u:,}–{growth_u:,} users.",
            mermaid=generate_architecture_mermaid(components, title=f"{title} — Growth"),
            strengths=[
                "Horizontal scaling for stateless tiers",
                "Queue-backed async where bursts appear",
                "Stronger observability and error budgets",
            ],
            limitations=[
                "Cross-service coordination complexity rises",
                "Data model migrations require careful sequencing",
                "Cost visibility must improve to avoid surprise spend",
            ],
            triggers=[
                "Cross-region latency or failover requirements",
                "Compliance scope expands (PII residency, audit trails)",
                "Team topology shifts to parallel squads",
            ],
            migrations=[
                "Formalize multi-AZ / DR drills against stated RTO/RPO",
                "Introduce feature flags and progressive delivery",
                "Shard/partition hot relational datasets or offload reads",
            ],
        ),
        _Phase(
            name="Enterprise",
            focus=f"Operate as a mature platform beyond ~{growth_u:,} users with governance.",
            mermaid=generate_architecture_mermaid(components, title=f"{title} — Enterprise"),
            strengths=[
                "Policy-driven guardrails for security and compliance",
                "Well-defined SLOs with paging aligned to business impact",
                "Capacity planning tied to finance and roadmap",
            ],
            limitations=[
                "Higher baseline cost for redundancy and tooling",
                "Change management overhead increases",
                "Requires robust platform engineering focus",
            ],
            triggers=[],
            migrations=[],
        ),
    ]

    intro = (
        f"{title} evolves from a deliberately small MVP footprint toward the selected "
        f"`{components.architecture_pattern.value}` reference architecture. "
        "Triggers are heuristic — validate against real telemetry and risk appetite."
    )

    total = components.total_monthly_cost_usd
    base_note = (
        f"Baseline library estimate ${total:,.0f}/mo"
        if total is not None
        else "Baseline cost not computed"
    )

    cost_rows = [
        {
            "name": "MVP",
            "cost": "~20–40% of target footprint",
            "notes": "Prefer managed services; defer multi-region duplication.",
        },
        {
            "name": "Growth",
            "cost": "~60–80% of target footprint",
            "notes": "Add redundancy, async paths, and observability depth.",
        },
        {
            "name": "Enterprise",
            "cost": f"Align with `{base_note}`",
            "notes": "Governance, DR, security controls, and FinOps discipline.",
        },
    ]

    return render_template(
        "documents/evolution.md.j2",
        project_title=title,
        phases=phases,
        evolution_intro=intro,
        scale=requirements.scale_metrics,
        cost_rows=cost_rows,
    )
