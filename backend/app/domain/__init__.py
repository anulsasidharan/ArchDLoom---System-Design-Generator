"""Shared Pydantic domain models (API boundaries and generation pipeline)."""

from app.domain.components import (
    ArchitecturePattern,
    ComponentAlternative,
    ComponentDecision,
    ComponentSelectionResult,
    ComponentSummary,
    TradeOffSet,
)
from app.domain.enterprise import (
    ComplianceControl,
    ComplianceFramework,
    ComplianceMapping,
    CostEstimate,
    CostLineItem,
    CostPhaseProjection,
    HADRStrategy,
    ObservabilityPillar,
    ObservabilityPlan,
    SecurityPlan,
)
from app.domain.generation import GenerationJobStatus, GenerationOptions
from app.domain.requirements import (
    ComplianceNeed,
    FunctionalRequirement,
    NonFunctionalRequirements,
    ParsedRequirement,
    ScaleMetrics,
    SuccessMetric,
    UserStory,
)

__all__ = [
    "ArchitecturePattern",
    "ComplianceControl",
    "ComplianceFramework",
    "ComplianceMapping",
    "ComplianceNeed",
    "ComponentAlternative",
    "ComponentDecision",
    "ComponentSelectionResult",
    "ComponentSummary",
    "CostEstimate",
    "CostLineItem",
    "CostPhaseProjection",
    "FunctionalRequirement",
    "GenerationJobStatus",
    "GenerationOptions",
    "HADRStrategy",
    "NonFunctionalRequirements",
    "ObservabilityPillar",
    "ObservabilityPlan",
    "ParsedRequirement",
    "ScaleMetrics",
    "SecurityPlan",
    "SuccessMetric",
    "TradeOffSet",
    "UserStory",
]
