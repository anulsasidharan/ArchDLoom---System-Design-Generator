"""Smoke tests for Mermaid generation helpers."""

from app.domain.components import (
    ArchitecturePattern,
    ComponentAlternative,
    ComponentDecision,
    ComponentSelectionResult,
    ComponentSummary,
    TradeOffSet,
)
from app.services.mermaid_generator import (
    generate_aiml_supplementary_mermaid,
    generate_architecture_mermaid,
    mermaid_category_to_node_ids,
)


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


def test_node_id_map_three_tier() -> None:
    m = mermaid_category_to_node_ids(ArchitecturePattern.THREE_TIER)
    assert m["database"] == "DB"
    assert m["api_gateway"] == "GW"


def test_node_id_map_microservices() -> None:
    m = mermaid_category_to_node_ids(ArchitecturePattern.MICROSERVICES)
    assert m["compute"] == "SVC"


def test_fine_tuning_diagram_contains_pipeline() -> None:
    src = generate_architecture_mermaid(
        _minimal_selection(ArchitecturePattern.FINE_TUNING_PIPELINE)
    )
    assert "Fine-tuning" in src or "fine-tuning" in src


def test_realtime_inference_contains_inference() -> None:
    src = generate_architecture_mermaid(
        _minimal_selection(ArchitecturePattern.REALTIME_INFERENCE)
    )
    assert "Real-time inference" in src or "inference" in src.lower()


def test_agentic_diagram_contains_agentic() -> None:
    src = generate_architecture_mermaid(
        _minimal_selection(ArchitecturePattern.AGENTIC_AI_SYSTEM)
    )
    assert "Agentic" in src


def test_supplementary_sequence_for_rag() -> None:
    seq = generate_aiml_supplementary_mermaid(
        _minimal_selection(ArchitecturePattern.RAG_SYSTEM),
        title="T",
    )
    assert "sequenceDiagram" in seq


def test_supplementary_empty_for_three_tier() -> None:
    assert (
        generate_aiml_supplementary_mermaid(
            _minimal_selection(ArchitecturePattern.THREE_TIER)
        )
        == ""
    )


def test_node_id_map_finetune() -> None:
    m = mermaid_category_to_node_ids(ArchitecturePattern.FINE_TUNING_PIPELINE)
    assert m.get("compute") == "ORCH"
    assert m.get("llm_provider") == "BASE"
