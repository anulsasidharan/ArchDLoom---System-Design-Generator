"""Basic Mermaid architecture diagrams from component selections."""

from __future__ import annotations

from app.domain.components import ArchitecturePattern, ComponentSelectionResult


def generate_architecture_mermaid(
    components: ComponentSelectionResult,
    *,
    title: str = "System",
) -> str:
    """Return Mermaid `graph TB` source for the high-level architecture."""
    pattern = components.architecture_pattern
    if pattern == ArchitecturePattern.RAG_SYSTEM:
        return _rag_diagram(components, title=title)
    if pattern == ArchitecturePattern.EVENT_DRIVEN:
        return _event_driven_diagram(components, title=title)
    if pattern == ArchitecturePattern.MICROSERVICES:
        return _microservices_diagram(components, title=title)
    return _three_tier_diagram(components, title=title)


def _safe_label(key: str, components: ComponentSelectionResult, fallback: str) -> str:
    dec = components.selections.get(key)
    if dec:
        return dec.selected.name.replace('"', "'")
    return fallback


def _three_tier_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API Gateway")
    app = _safe_label("compute", cs, "Application")
    db = _safe_label("database", cs, "Database")
    cache = _safe_label("cache", cs, "Cache")
    mon = _safe_label("monitoring", cs, "Monitoring")
    return f"""graph TB
    U[Users] --> GW[{gw}]
    GW --> APP[{app}]
    APP --> DB[{db}]
    APP --> C[{cache}]
    APP -. metrics .-> M[{mon}]
    subgraph "{title} — Three-tier"
      GW
      APP
    end
"""


def _rag_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API Gateway")
    app = _safe_label("compute", cs, "Orchestrator")
    vdb = _safe_label("vector_database", cs, "Vector DB")
    llm = _safe_label("llm_provider", cs, "LLM")
    emb = _safe_label("embedding_model", cs, "Embeddings")
    db = _safe_label("database", cs, "Primary DB")
    return f"""graph TB
    U[Users] --> GW[{gw}]
    GW --> APP[{app}]
    APP --> V[{vdb}]
    APP --> L[{llm}]
    INGEST[Ingestion] --> E[{emb}] --> V
    APP --> DB[{db}]
    subgraph "{title} — RAG"
      APP
      V
      L
    end
"""


def _event_driven_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API Gateway")
    app = _safe_label("compute", cs, "Services")
    q = _safe_label("message_queue", cs, "Queue")
    db = _safe_label("database", cs, "Database")
    return f"""graph LR
    U[Users] --> GW[{gw}]
    GW --> APP[{app}]
    APP --> Q[{q}]
    Q --> APP
    APP --> DB[{db}]
    subgraph "{title} — Event-driven"
      APP
      Q
    end
"""


def _microservices_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API Gateway")
    app = _safe_label("compute", cs, "Services")
    db = _safe_label("database", cs, "Database")
    cache = _safe_label("cache", cs, "Cache")
    return f"""graph TB
    U[Users] --> GW[{gw}]
    GW --> SVC[{app}]
    SVC --> DB[{db}]
    SVC --> C[{cache}]
    subgraph "{title} — Microservices"
      SVC
    end
"""
