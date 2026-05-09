"""Smoke tests for Mermaid generation helpers."""

from app.domain.components import (
    ArchitecturePattern,
    ComponentAlternative,
    ComponentDecision,
    ComponentSelectionResult,
    ComponentSummary,
    TradeOffSet,
)
from app.services.mermaid_generator import generate_architecture_mermaid


def _minimal_selection(pattern: ArchitecturePattern) -> ComponentSelectionResult:
    db = ComponentSummary(id=None, name="PostgreSQL", category="database")
    decision = ComponentDecision(
        category="database",
        selected=db,
        alternatives=[
            ComponentAlternative(name="Other", rejection_reason="Lower fit score."),
        ],
        rationale="Test",
        trade_offs=TradeOffSet(pros=["a"], cons=["b"]),
        estimated_monthly_cost_usd=100.0,
    )
    return ComponentSelectionResult(
        selections={"database": decision},
        total_monthly_cost_usd=100.0,
        architecture_pattern=pattern,
    )


def test_three_tier_contains_graph() -> None:
    src = generate_architecture_mermaid(_minimal_selection(ArchitecturePattern.THREE_TIER))
    assert "graph TB" in src


def test_rag_contains_subgraph() -> None:
    src = generate_architecture_mermaid(_minimal_selection(ArchitecturePattern.RAG_SYSTEM))
    assert "RAG" in src
