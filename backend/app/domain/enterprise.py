"""Pydantic models for Phase 6 enterprise concerns: cost, compliance, HA/DR, security, observability."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CostLineItem(BaseModel):
    """One row of an estimated component-level monthly cost."""

    category: str
    component: str
    pricing_model: str | None = None
    base_cost_usd: float = 0.0
    scale_multiplier: float = 1.0
    estimated_monthly_cost_usd: float = 0.0
    notes: str = ""


class CostPhaseProjection(BaseModel):
    """Aggregate cost projection per evolution phase."""

    name: str
    monthly_cost_usd: float
    notes: str = ""


class CostEstimate(BaseModel):
    """Complete cost picture used by HLD/architecture/evolution artifacts."""

    pattern: str
    line_items: list[CostLineItem] = Field(default_factory=list)
    aggregate_monthly_usd: float = 0.0
    phases: list[CostPhaseProjection] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ComplianceControl(BaseModel):
    """A single recommended control linked to one or more frameworks."""

    id: str
    name: str
    description: str
    frameworks: list[str] = Field(default_factory=list)


class ComplianceFramework(BaseModel):
    """Top-level regulatory or attestation framework block."""

    code: str
    name: str
    drivers: list[str] = Field(default_factory=list)
    controls: list[ComplianceControl] = Field(default_factory=list)


class ComplianceMapping(BaseModel):
    """Aggregated compliance posture for the system."""

    frameworks: list[ComplianceFramework] = Field(default_factory=list)
    inferred_codes: list[str] = Field(default_factory=list)
    explicit_codes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class HADRStrategy(BaseModel):
    """High-availability and disaster-recovery posture and recommendations."""

    availability_target: str
    rto: str
    rpo: str
    posture: str
    posture_rationale: str = ""
    recommendations: list[str] = Field(default_factory=list)
    backup_strategy: list[str] = Field(default_factory=list)
    drills: list[str] = Field(default_factory=list)
    failover_runbook: list[str] = Field(default_factory=list)


class ObservabilityPillar(BaseModel):
    """Metrics / logs / traces (or peers) with concrete instrumentation hints."""

    name: str
    purpose: str
    instruments: list[str] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)


class ObservabilityPlan(BaseModel):
    """Observability blueprint: pillars, SLOs, paging, dashboards."""

    pillars: list[ObservabilityPillar] = Field(default_factory=list)
    slo_targets: list[str] = Field(default_factory=list)
    paging: list[str] = Field(default_factory=list)
    dashboards: list[str] = Field(default_factory=list)
    log_retention: str = ""
    trace_sampling: str = ""


class SecurityPlan(BaseModel):
    """Security architecture narrative split by control families."""

    authentication: list[str] = Field(default_factory=list)
    authorization: list[str] = Field(default_factory=list)
    encryption_at_rest: list[str] = Field(default_factory=list)
    encryption_in_transit: list[str] = Field(default_factory=list)
    network_security: list[str] = Field(default_factory=list)
    secrets_management: list[str] = Field(default_factory=list)
    audit_logging: list[str] = Field(default_factory=list)
    application_security: list[str] = Field(default_factory=list)
    data_protection: list[str] = Field(default_factory=list)
    iam_principles: list[str] = Field(default_factory=list)
    threat_model_notes: list[str] = Field(default_factory=list)
