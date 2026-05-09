"""Shared Pydantic domain models (API boundaries and generation pipeline)."""

from app.domain.components import (
    ArchitecturePattern,
    ComponentAlternative,
    ComponentDecision,
    ComponentSelectionResult,
    ComponentSummary,
    TradeOffSet,
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
    "ComplianceNeed",
    "ComponentAlternative",
    "ComponentDecision",
    "ComponentSelectionResult",
    "ComponentSummary",
    "FunctionalRequirement",
    "GenerationJobStatus",
    "GenerationOptions",
    "NonFunctionalRequirements",
    "ParsedRequirement",
    "ScaleMetrics",
    "SuccessMetric",
    "TradeOffSet",
    "UserStory",
]
