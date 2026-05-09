"""Unit tests for the Phase 6 enterprise generators."""

from __future__ import annotations

from app.domain.components import (
    ArchitecturePattern,
    ComponentDecision,
    ComponentSelectionResult,
    ComponentSummary,
    TradeOffSet,
)
from app.domain.requirements import (
    ComplianceNeed,
    NonFunctionalRequirements,
    ParsedRequirement,
    ScaleMetrics,
)
from app.services.enterprise import (
    build_compliance_mapping,
    build_hadr_strategy,
    build_observability_plan,
    build_security_plan,
    estimate_costs,
    generate_network_diagram,
)


def _decision(category: str, name: str, *, cost: float = 100.0) -> ComponentDecision:
    return ComponentDecision(
        category=category,
        selected=ComponentSummary(id=None, name=name, category=category, vendor="AWS"),
        alternatives=[],
        rationale="test",
        trade_offs=TradeOffSet(pros=["a"], cons=["b"]),
        estimated_monthly_cost_usd=cost,
    )


def _selection(pattern: ArchitecturePattern, *, with_ai: bool = False) -> ComponentSelectionResult:
    sels: dict[str, ComponentDecision] = {
        "api_gateway": _decision("api_gateway", "API Gateway", cost=80.0),
        "compute": _decision("compute", "ECS Fargate", cost=300.0),
        "database": _decision("database", "Aurora PostgreSQL", cost=400.0),
        "cache": _decision("cache", "ElastiCache Redis", cost=120.0),
        "monitoring": _decision("monitoring", "CloudWatch", cost=150.0),
    }
    if with_ai:
        sels["llm_provider"] = _decision("llm_provider", "Claude Sonnet 4", cost=600.0)
        sels["vector_database"] = _decision("vector_database", "pgvector", cost=200.0)
        sels["embedding_model"] = _decision("embedding_model", "OpenAI text-embed", cost=120.0)
    total = sum(d.estimated_monthly_cost_usd or 0.0 for d in sels.values())
    return ComponentSelectionResult(
        selections=sels,
        total_monthly_cost_usd=total,
        architecture_pattern=pattern,
    )


def _req(
    *,
    domain: str = "saas",
    has_ai: bool = False,
    rto: str | None = None,
    rpo: str | None = None,
    availability: str | None = None,
    rps: float | None = 50.0,
    dau: int | None = 100_000,
    data_gb: float | None = 500.0,
    compliance: list[str] | None = None,
) -> ParsedRequirement:
    needs = [ComplianceNeed(name=c, description=f"{c} required") for c in (compliance or [])]
    return ParsedRequirement(
        system_name="TestSys",
        domain=domain,
        summary="Test system summary.",
        core_features=["onboarding", "billing"],
        scale_metrics=ScaleMetrics(
            daily_active_users=dau,
            peak_requests_per_second=rps,
            data_volume_gb=data_gb,
            mvp_users=5_000,
            growth_users=50_000,
        ),
        non_functional_requirements=NonFunctionalRequirements(
            availability_target=availability,
            rto=rto,
            rpo=rpo,
        ),
        compliance_needs=needs,
        has_ai_features=has_ai,
    )


# ---------- Cost estimator (P6-1) ----------


def test_cost_estimator_produces_phases_and_lines() -> None:
    sel = _selection(ArchitecturePattern.THREE_TIER)
    cost = estimate_costs(_req(), sel)
    assert cost.aggregate_monthly_usd > 0
    assert {p.name for p in cost.phases} == {"MVP", "Growth", "Enterprise"}
    assert all(li.estimated_monthly_cost_usd >= li.base_cost_usd for li in cost.line_items)
    assert any("scale" in a.lower() or "phase" in a.lower() for a in cost.assumptions)


def test_cost_estimator_scales_with_traffic() -> None:
    sel = _selection(ArchitecturePattern.THREE_TIER)
    low = estimate_costs(_req(rps=1.0, dau=1000, data_gb=1.0), sel)
    high = estimate_costs(_req(rps=10_000.0, dau=10_000_000, data_gb=100_000.0), sel)
    assert high.aggregate_monthly_usd > low.aggregate_monthly_usd


def test_cost_estimator_phase_ordering() -> None:
    sel = _selection(ArchitecturePattern.RAG_SYSTEM, with_ai=True)
    cost = estimate_costs(_req(has_ai=True), sel)
    phase_costs = {p.name: p.monthly_cost_usd for p in cost.phases}
    assert phase_costs["MVP"] <= phase_costs["Growth"] <= phase_costs["Enterprise"]


# ---------- Compliance mapper (P6-2) ----------


def test_compliance_inferred_from_healthcare_domain() -> None:
    mapping = build_compliance_mapping(_req(domain="healthcare"))
    codes = {f.code for f in mapping.frameworks}
    assert "HIPAA" in codes
    assert "SOC2" in codes


def test_compliance_explicit_gdpr_takes_priority() -> None:
    mapping = build_compliance_mapping(_req(domain="general", compliance=["GDPR"]))
    codes = {f.code for f in mapping.frameworks}
    assert "GDPR" in codes
    assert "GDPR" in mapping.explicit_codes


def test_compliance_pci_inference_from_keywords() -> None:
    req = _req(domain="general")
    req.summary = "Process credit card payments via tokenized vault."
    mapping = build_compliance_mapping(req)
    codes = {f.code for f in mapping.frameworks}
    assert "PCI-DSS" in codes


def test_compliance_default_soc2_when_silent() -> None:
    req = _req(domain="unrecognized-domain")
    mapping = build_compliance_mapping(req)
    assert any(f.code == "SOC2" for f in mapping.frameworks)


# ---------- Network diagrams (P6-3) ----------


def test_network_diagram_three_tier_has_subnets() -> None:
    src = generate_network_diagram(_selection(ArchitecturePattern.THREE_TIER), title="Sys")
    assert "Public subnets" in src
    assert "Private subnets" in src
    assert "Data subnets" in src
    assert "graph TB" in src


def test_network_diagram_rag_includes_vector_and_llm() -> None:
    src = generate_network_diagram(
        _selection(ArchitecturePattern.RAG_SYSTEM, with_ai=True),
        title="Sys",
    )
    assert "Vector" in src or "pgvector" in src
    assert "LLM" in src or "llm" in src.lower()


def test_network_diagram_realtime_inference_multiregion() -> None:
    src = generate_network_diagram(
        _selection(ArchitecturePattern.REALTIME_INFERENCE, with_ai=True),
        title="Sys",
    )
    assert "Region A" in src and "Region B" in src


# ---------- Security plan (P6-4) ----------


def test_security_plan_contains_required_families() -> None:
    sel = _selection(ArchitecturePattern.THREE_TIER)
    mapping = build_compliance_mapping(_req())
    plan = build_security_plan(_req(), sel, mapping)
    assert plan.encryption_at_rest
    assert plan.encryption_in_transit
    assert plan.network_security
    assert plan.iam_principles


def test_security_plan_extends_for_pci() -> None:
    sel = _selection(ArchitecturePattern.MICROSERVICES)
    req = _req(domain="payments")
    mapping = build_compliance_mapping(req)
    plan = build_security_plan(req, sel, mapping)
    assert any("token" in item.lower() or "pan" in item.lower() for item in plan.data_protection)


def test_security_plan_extends_for_ai_pattern() -> None:
    sel = _selection(ArchitecturePattern.AGENTIC_AI_SYSTEM, with_ai=True)
    req = _req(has_ai=True)
    mapping = build_compliance_mapping(req)
    plan = build_security_plan(req, sel, mapping)
    assert any("tool" in item.lower() for item in plan.threat_model_notes + plan.authorization)


# ---------- HA/DR strategy (P6-5) ----------


def test_hadr_strategy_defaults_to_multi_az() -> None:
    plan = build_hadr_strategy(_req(), _selection(ArchitecturePattern.THREE_TIER))
    assert plan.posture == "multi-az"
    assert plan.recommendations
    assert plan.failover_runbook
    assert plan.backup_strategy
    assert plan.drills


def test_hadr_strategy_upgrades_for_strict_targets() -> None:
    plan = build_hadr_strategy(
        _req(availability="99.999%", rto="2 minutes", rpo="30 seconds"),
        _selection(ArchitecturePattern.REALTIME_INFERENCE, with_ai=True),
    )
    assert plan.posture == "multi-region-active-active"


def test_hadr_strategy_active_passive_for_moderate_targets() -> None:
    plan = build_hadr_strategy(
        _req(availability="99.99%", rto="30 minutes", rpo="15 minutes"),
        _selection(ArchitecturePattern.MICROSERVICES),
    )
    assert plan.posture in {"multi-region-active-passive", "multi-region-active-active"}


# ---------- Observability (P6-6) ----------


def test_observability_plan_basic_pillars() -> None:
    plan = build_observability_plan(_req(), _selection(ArchitecturePattern.THREE_TIER))
    pillar_names = {p.name for p in plan.pillars}
    assert "Metrics (RED + USE)" in pillar_names
    assert "Logs" in pillar_names
    assert "Traces" in pillar_names
    assert plan.slo_targets
    assert plan.paging
    assert plan.dashboards
    assert plan.log_retention
    assert plan.trace_sampling


def test_observability_plan_adds_ai_pillar_for_rag() -> None:
    plan = build_observability_plan(
        _req(has_ai=True),
        _selection(ArchitecturePattern.RAG_SYSTEM, with_ai=True),
    )
    pillar_names = {p.name for p in plan.pillars}
    assert "AI/ML telemetry" in pillar_names


def test_observability_plan_inference_alerts() -> None:
    plan = build_observability_plan(
        _req(has_ai=True, availability="99.95%"),
        _selection(ArchitecturePattern.REALTIME_INFERENCE, with_ai=True),
    )
    ai_pillar = next(p for p in plan.pillars if p.name == "AI/ML telemetry")
    assert any("latency" in a.lower() for a in ai_pillar.alerts)
