from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ArchitecturePattern(str, Enum):
    THREE_TIER = "three_tier_web_app"
    MICROSERVICES = "microservices"
    RAG_SYSTEM = "rag_system"
    EVENT_DRIVEN = "event_driven"
    GENERIC = "generic"


class TradeOffSet(BaseModel):
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


class ComponentSummary(BaseModel):
    """Lightweight component snapshot for documents and API."""

    id: str | None = None
    name: str
    category: str
    vendor: str | None = None
    features: list[Any] = Field(default_factory=list)
    icon_url: str | None = None
    instance_type: str | None = None
    storage_config: str | None = None
    encryption_method: str | None = None
    sla: str | None = None


class ComponentAlternative(BaseModel):
    name: str
    rejection_reason: str


class ComponentDecision(BaseModel):
    category: str
    selected: ComponentSummary
    alternatives: list[ComponentAlternative] = Field(default_factory=list)
    rationale: str = ""
    trade_offs: TradeOffSet = Field(default_factory=TradeOffSet)
    estimated_monthly_cost_usd: float | None = None


class ComponentSelectionResult(BaseModel):
    selections: dict[str, ComponentDecision]
    total_monthly_cost_usd: float | None = None
    architecture_pattern: ArchitecturePattern = ArchitecturePattern.GENERIC
