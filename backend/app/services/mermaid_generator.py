"""Mermaid architecture diagrams from component selections."""

from __future__ import annotations

import re

from app.domain.components import ArchitecturePattern, ComponentSelectionResult


def mermaid_category_to_node_ids(pattern: ArchitecturePattern) -> dict[str, str]:
    """Map ``category`` keys from ``ComponentSelectionResult.selections`` to Mermaid node ids."""
    if pattern == ArchitecturePattern.RAG_SYSTEM:
        return {
            "api_gateway": "GW",
            "compute": "APP",
            "vector_database": "V",
            "llm_provider": "L",
            "embedding_model": "E",
            "database": "DB",
            "cache": "C",
            "monitoring": "M",
            "message_queue": "Q",
        }
    if pattern == ArchitecturePattern.FINE_TUNING_PIPELINE:
        return {
            "api_gateway": "GW",
            "compute": "ORCH",
            "database": "META",
            "message_queue": "Q",
            "llm_provider": "BASE",
            "monitoring": "M",
            "cache": "C",
            "vector_database": "V",
            "embedding_model": "E",
        }
    if pattern == ArchitecturePattern.REALTIME_INFERENCE:
        return {
            "api_gateway": "GW",
            "compute": "INF",
            "cache": "C",
            "database": "DB",
            "llm_provider": "LLM",
            "monitoring": "M",
            "message_queue": "Q",
            "vector_database": "V",
        }
    if pattern == ArchitecturePattern.AGENTIC_AI_SYSTEM:
        return {
            "api_gateway": "GW",
            "compute": "ORCH",
            "llm_provider": "LLM",
            "database": "MEM",
            "cache": "C",
            "vector_database": "V",
            "monitoring": "M",
            "message_queue": "Q",
            "embedding_model": "E",
        }
    if pattern == ArchitecturePattern.EVENT_DRIVEN:
        return {
            "api_gateway": "GW",
            "compute": "APP",
            "message_queue": "Q",
            "database": "DB",
            "cache": "C",
            "monitoring": "M",
        }
    if pattern == ArchitecturePattern.MICROSERVICES:
        return {
            "api_gateway": "GW",
            "compute": "SVC",
            "database": "DB",
            "cache": "C",
            "monitoring": "M",
            "message_queue": "Q",
        }
    # THREE_TIER + GENERIC
    return {
        "api_gateway": "GW",
        "compute": "APP",
        "database": "DB",
        "cache": "C",
        "monitoring": "M",
        "message_queue": "Q",
        "vector_database": "V",
        "llm_provider": "L",
        "embedding_model": "E",
    }


def generate_architecture_mermaid(
    components: ComponentSelectionResult,
    *,
    title: str = "System",
) -> str:
    """Return Mermaid `graph TB` (or mixed) source for the high-level architecture."""
    pattern = components.architecture_pattern
    if pattern == ArchitecturePattern.RAG_SYSTEM:
        return _rag_diagram(components, title=title)
    if pattern == ArchitecturePattern.FINE_TUNING_PIPELINE:
        return _fine_tuning_diagram(components, title=title)
    if pattern == ArchitecturePattern.REALTIME_INFERENCE:
        return _realtime_inference_diagram(components, title=title)
    if pattern == ArchitecturePattern.AGENTIC_AI_SYSTEM:
        return _agentic_diagram(components, title=title)
    if pattern == ArchitecturePattern.EVENT_DRIVEN:
        return _event_driven_diagram(components, title=title)
    if pattern == ArchitecturePattern.MICROSERVICES:
        return _microservices_diagram(components, title=title)
    return _three_tier_diagram(components, title=title)


def generate_aiml_supplementary_mermaid(
    components: ComponentSelectionResult,
    *,
    title: str = "System",
) -> str:
    """Second diagram: control / data-flow emphasis for AI patterns (sequence-style)."""
    pattern = components.architecture_pattern
    if pattern == ArchitecturePattern.RAG_SYSTEM:
        return _rag_sequence(components, title=title)
    if pattern == ArchitecturePattern.FINE_TUNING_PIPELINE:
        return _finetune_sequence(components, title=title)
    if pattern == ArchitecturePattern.REALTIME_INFERENCE:
        return _inference_sequence(components, title=title)
    if pattern == ArchitecturePattern.AGENTIC_AI_SYSTEM:
        return _agentic_sequence(components, title=title)
    return ""


def _safe_label(key: str, components: ComponentSelectionResult, fallback: str) -> str:
    dec = components.selections.get(key)
    if dec:
        name = dec.selected.name.replace('"', "'")
        # Strip chars that break Mermaid node label syntax
        name = re.sub(r'[(){}\[\]<>|]', '', name).strip()
        return name or fallback
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
    cache = _safe_label("cache", cs, "Cache")
    q = _safe_label("message_queue", cs, "Ingestion queue")
    mon = _safe_label("monitoring", cs, "Observability")
    return f"""graph TB
    U[Users] --> GW[{gw}]
    GW --> APP[{app}]
    subgraph "{title} — RAG query path"
      APP --> RET[Retriever]
      RET --> V[{vdb}]
      RET --> RR[Reranker]
      RR --> L[{llm}]
      L --> APP
    end
    subgraph "Grounding store"
      APP --> DB[{db}]
      APP --> C[{cache}]
    end
    subgraph "Ingestion"
      SRC[Sources] --> Q[{q}]
      Q --> CHUNK[Chunk + enrich]
      CHUNK --> E[{emb}]
      E --> V
    end
    APP -. traces .-> M[{mon}]
"""


def _fine_tuning_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API / CI gateway")
    orch = _safe_label("compute", cs, "Training orchestrator")
    meta = _safe_label("database", cs, "Metadata & lineage DB")
    q = _safe_label("message_queue", cs, "Job queue")
    base = _safe_label("llm_provider", cs, "Base model API")
    mon = _safe_label("monitoring", cs, "Experiment tracking")
    cache = _safe_label("cache", cs, "Artifact cache")
    return f"""graph TB
    subgraph "{title} — Fine-tuning pipeline"
      RAW[Raw datasets] --> CURATE[Curate / label]
      CURATE --> DS[(Versioned datasets)]
      DS --> Q[{q}]
      Q --> TRAIN[Training workers / GPUs]
      TRAIN --> REG[(Model registry)]
      REG --> EVAL[Offline evaluation]
      EVAL --> PROMOTE[Promotion gates]
    end
    GW[{gw}] --> ORCH[{orch}]
    ORCH --> TRAIN
    ORCH --> META[{meta}]
    BASE[{base}] -. base weights .-> TRAIN
    TRAIN --> C[{cache}]
    TRAIN -. metrics .-> M[{mon}]
    PROMOTE -. approved routes .-> GW
"""


def _realtime_inference_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API Gateway")
    inf = _safe_label("compute", cs, "Inference service")
    llm = _safe_label("llm_provider", cs, "Hosted LLM / runtime")
    cache = _safe_label("cache", cs, "Prefix cache / KV")
    db = _safe_label("database", cs, "Policies & features DB")
    mon = _safe_label("monitoring", cs, "SLO & latency monitors")
    q = _safe_label("message_queue", cs, "Async overflow")
    return f"""graph LR
    U[Clients] --> GW[{gw}]
    GW --> LB[Router / autoscaler]
    LB --> INF[{inf}]
    subgraph "{title} — Real-time inference"
      INF --> LLM[{llm}]
      INF --> C[{cache}]
      INF --> DBN[{db}]
    end
    INF -. overload .-> Q[{q}]
    INF -. p95/p99 .-> M[{mon}]
"""


def _agentic_diagram(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "API Gateway")
    orch = _safe_label("compute", cs, "Agent orchestrator")
    llm = _safe_label("llm_provider", cs, "Planner LLM")
    mem = _safe_label("database", cs, "Session / tool state DB")
    vdb = _safe_label("vector_database", cs, "Long-term memory")
    cache = _safe_label("cache", cs, "Working set cache")
    q = _safe_label("message_queue", cs, "Tool fan-out queue")
    mon = _safe_label("monitoring", cs, "Traces & eval hooks")
    return f"""graph TB
    U[Users] --> GW[{gw}]
    GW --> ORCH[{orch}]
    subgraph "{title} — Agentic control loop"
      ORCH --> PL[Planner / policy]
      PL --> LLM[{llm}]
      LLM --> ORCH
      ORCH --> TOOLS[Tool executors]
      TOOLS --> EXT[External APIs & data]
      ORCH --> MEM[{mem}]
      ORCH --> V[{vdb}]
      ORCH --> C[{cache}]
      TOOLS --> Q[{q}]
    end
    ORCH -. spans .-> M[{mon}]
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


def _rag_sequence(cs: ComponentSelectionResult, *, title: str) -> str:
    app = _safe_label("compute", cs, "Orchestrator")
    vdb = _safe_label("vector_database", cs, "Vector DB")
    llm = _safe_label("llm_provider", cs, "LLM")
    return f"""sequenceDiagram
    autonumber
    participant U as User
    participant G as Gateway
    participant A as {app}
    participant V as {vdb}
    participant L as {llm}
    U->>G: Prompt
    G->>A: Authenticated request
    A->>V: Similarity search
    V-->>A: Chunks + scores
    A->>L: Grounded completion
    L-->>A: Answer + citations
    A-->>G: Response
    G-->>U: Result
    Note over A,L: RAG query path (high level)
"""


def _finetune_sequence(cs: ComponentSelectionResult, *, title: str) -> str:
    orch = _safe_label("compute", cs, "Orchestrator")
    q = _safe_label("message_queue", cs, "Job queue")
    return f"""sequenceDiagram
    autonumber
    participant D as Data owners
    participant O as {orch}
    participant Q as {q}
    participant T as Training cluster
    participant R as Model registry
    D->>O: Register dataset version
    O->>Q: Enqueue training job
    Q->>T: Schedule GPUs
    T->>R: Push checkpoint
    R->>O: Evaluation hooks
    Note over O,R: Training lifecycle
"""


def _inference_sequence(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _safe_label("api_gateway", cs, "Gateway")
    inf = _safe_label("compute", cs, "Inference")
    llm = _safe_label("llm_provider", cs, "Model runtime")
    return f"""sequenceDiagram
    autonumber
    participant C as Client
    participant G as {gw}
    participant I as {inf}
    participant M as {llm}
    C->>G: Inference request
    G->>I: Route + throttle
    I->>M: Forward tokens / batch
    M-->>I: Streams / logits
    I-->>G: Normalized response
    G-->>C: Low-latency reply
    Note over C,M: Latency path
"""


def _agentic_sequence(cs: ComponentSelectionResult, *, title: str) -> str:
    orch = _safe_label("compute", cs, "Orchestrator")
    llm = _safe_label("llm_provider", cs, "LLM")
    return f"""sequenceDiagram
    autonumber
    participant U as User
    participant A as {orch}
    participant L as {llm}
    participant T as Tools
    U->>A: Task
    loop Reason + act
      A->>L: Plan next step
      L-->>A: Tool calls / answer
      A->>T: Execute capabilities
      T-->>A: Observations
    end
    A-->>U: Final response
    Note over U,T: Agent loop
"""
