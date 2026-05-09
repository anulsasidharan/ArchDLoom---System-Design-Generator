from __future__ import annotations

from pydantic import BaseModel, Field


class ScaleMetrics(BaseModel):
    """Inferred or stated scale signals."""

    daily_active_users: int | None = None
    peak_requests_per_second: float | None = None
    data_volume_gb: float | None = None
    mvp_users: int | None = Field(default=None, description="MVP phase user ceiling")
    growth_users: int | None = Field(default=None, description="Growth phase user ceiling")


class UserStory(BaseModel):
    role: str
    action: str
    benefit: str


class FunctionalRequirement(BaseModel):
    name: str
    description: str
    user_stories: list[UserStory] = Field(default_factory=list)


class SuccessMetric(BaseModel):
    name: str
    target: str
    measurement: str


class ComplianceNeed(BaseModel):
    name: str
    description: str = ""


class NonFunctionalRequirements(BaseModel):
    latency_target: str | None = None
    availability_target: str | None = None
    throughput_target: str | None = None
    concurrent_users: str | None = None
    rto: str | None = None
    rpo: str | None = None


class ParsedRequirement(BaseModel):
    """Structured output from natural-language system design input."""

    system_name: str
    domain: str
    summary: str = ""
    core_features: list[str] = Field(default_factory=list)
    scale_metrics: ScaleMetrics = Field(default_factory=ScaleMetrics)
    functional_requirements: list[FunctionalRequirement] = Field(default_factory=list)
    non_functional_requirements: NonFunctionalRequirements = Field(
        default_factory=NonFunctionalRequirements
    )
    compliance_needs: list[ComplianceNeed] = Field(default_factory=list)
    tech_preferences: dict[str, str] = Field(default_factory=dict)
    budget_constraints: dict[str, str] = Field(default_factory=dict)
    business_goals: list[str] = Field(default_factory=list)
    success_metrics: list[SuccessMetric] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    needs_async_processing: bool = False
    has_ai_features: bool = False
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Only when critical information is missing.",
    )
