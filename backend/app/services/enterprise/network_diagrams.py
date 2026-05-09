"""Network architecture Mermaid diagram generator.

Renders a VPC-style topology with public / private / data subnets, NAT egress,
WAF + LB ingress, and pattern-aware overlays (RAG ingestion network, fine-tuning
training tier, agent tool egress, etc.).
"""

from __future__ import annotations

from app.domain.components import ArchitecturePattern, ComponentSelectionResult


def _label(cs: ComponentSelectionResult, key: str, fallback: str) -> str:
    dec = cs.selections.get(key)
    if dec:
        return dec.selected.name.replace('"', "'")
    return fallback


def _multi_az(has_ai: bool) -> bool:
    """Show two AZs when patterns are AI/data-heavy or always (default true)."""
    return True


def _common_header(title: str) -> str:
    return f"""%% Network architecture for {title}
%% (logical view — translate to VPC/CIDR allocations during cloud setup)
graph TB
    classDef pub fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e;
    classDef priv fill:#ecfccb,stroke:#65a30d,color:#365314;
    classDef data fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef edge fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d;
    classDef ext fill:#f3e8ff,stroke:#7e22ce,color:#581c87;
"""


def _three_tier_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "API Gateway")
    app = _label(cs, "compute", "App tier")
    db = _label(cs, "database", "Primary DB")
    cache = _label(cs, "cache", "Cache")
    mon = _label(cs, "monitoring", "Observability")
    return _common_header(title) + f"""
    subgraph EDGE["Internet edge"]
      USR[Public users]:::ext
      DDOS[DDoS / WAF]:::edge
      CDN[CDN]:::edge
    end
    subgraph VPC["VPC / Virtual Network"]
      subgraph PUB["Public subnets (AZ-a, AZ-b)"]
        ALB[Load balancer<br/>{gw}]:::pub
        NAT[NAT gateway]:::pub
      end
      subgraph PRIV["Private subnets (AZ-a, AZ-b)"]
        APP[{app}<br/>auto-scaling group]:::priv
        CACHE[{cache}]:::priv
      end
      subgraph DATA["Data subnets (AZ-a, AZ-b)"]
        DB[{db}<br/>multi-AZ]:::data
      end
      MON[{mon}<br/>endpoint]:::priv
    end
    USR --> DDOS --> CDN --> ALB
    ALB --> APP
    APP --> CACHE
    APP --> DB
    APP -. egress via NAT .-> NAT
    APP -. metrics .-> MON
"""


def _rag_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "API Gateway")
    app = _label(cs, "compute", "RAG orchestrator")
    db = _label(cs, "database", "Primary DB")
    vdb = _label(cs, "vector_database", "Vector DB")
    llm = _label(cs, "llm_provider", "LLM provider")
    emb = _label(cs, "embedding_model", "Embedding service")
    cache = _label(cs, "cache", "Cache")
    q = _label(cs, "message_queue", "Ingestion queue")
    return _common_header(title) + f"""
    subgraph EDGE["Internet edge"]
      USR[Users]:::ext
      WAF[WAF / Bot mgmt]:::edge
    end
    subgraph VPC["VPC"]
      subgraph PUB["Public subnets"]
        ALB[ALB<br/>{gw}]:::pub
        NAT[NAT gateway]:::pub
      end
      subgraph PRIV["Private (orchestration)"]
        APP[{app}]:::priv
        EMB[{emb}]:::priv
        CACHE[{cache}]:::priv
        Q[{q}]:::priv
      end
      subgraph DATA["Data tier"]
        DB[{db}]:::data
        VDB[{vdb}]:::data
      end
    end
    subgraph EXT["External / managed services"]
      LLM[{llm}<br/>private link if available]:::ext
      OBJ[Object storage<br/>raw documents]:::ext
    end
    USR --> WAF --> ALB --> APP
    APP --> CACHE
    APP --> DB
    APP --> VDB
    APP -. completion .-> LLM
    OBJ --> Q --> EMB --> VDB
    APP -. egress .-> NAT
"""


def _fine_tuning_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "Control-plane gateway")
    orch = _label(cs, "compute", "Training orchestrator")
    meta = _label(cs, "database", "Metadata DB")
    q = _label(cs, "message_queue", "Job queue")
    base = _label(cs, "llm_provider", "Base model API")
    cache = _label(cs, "cache", "Artifact cache")
    return _common_header(title) + f"""
    subgraph EDGE["Operator access"]
      OPS[Engineers / CI]:::ext
      VPN[Private SSO / VPN]:::edge
    end
    subgraph VPC["VPC"]
      subgraph PUB["Public subnets"]
        GW[{gw}]:::pub
        NAT[NAT gateway]:::pub
      end
      subgraph CTRL["Private control plane"]
        ORCH[{orch}]:::priv
        META[{meta}]:::data
        Q[{q}]:::priv
        CACHE[{cache}]:::priv
      end
      subgraph TRAIN["Training subnets (GPU)"]
        T[GPU training fleet<br/>isolated NSG]:::priv
        REG[Model registry<br/>S3 bucket policy]:::data
      end
    end
    subgraph EXT["External"]
      BASE[{base}]:::ext
      DS[Dataset object storage]:::ext
    end
    OPS --> VPN --> GW --> ORCH
    ORCH --> META
    ORCH --> Q --> T
    DS --> T
    T --> REG
    BASE -. base weights .-> T
    T -. egress .-> NAT
    T --> CACHE
"""


def _realtime_inference_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "Inference gateway")
    inf = _label(cs, "compute", "Inference fleet")
    cache = _label(cs, "cache", "KV / prefix cache")
    db = _label(cs, "database", "Feature/policy DB")
    llm = _label(cs, "llm_provider", "Hosted LLM")
    return _common_header(title) + f"""
    subgraph EDGE["Edge"]
      C[Clients]:::ext
      WAF[WAF + rate limit]:::edge
      ANY[Anycast load balancer]:::edge
    end
    subgraph REGIONA["Region A — VPC"]
      subgraph PUBA["Public"]
        GWA[{gw}]:::pub
      end
      subgraph PRIVA["Private inference"]
        INFA[{inf}<br/>autoscaling]:::priv
        CACHEA[{cache}]:::priv
      end
      subgraph DATAA["Data"]
        DBA[{db}]:::data
      end
    end
    subgraph REGIONB["Region B — VPC (failover)"]
      GWB[{gw} replica]:::pub
      INFB[{inf} warm pool]:::priv
      DBB[{db} read replica]:::data
    end
    subgraph EXT["External"]
      LLM[{llm}<br/>private endpoint]:::ext
    end
    C --> WAF --> ANY
    ANY --> GWA --> INFA
    ANY -. failover .-> GWB --> INFB
    INFA --> CACHEA --> DBA
    INFA -. tokens .-> LLM
    DBA -. async repl .-> DBB
"""


def _agentic_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "Agent gateway")
    orch = _label(cs, "compute", "Agent orchestrator")
    llm = _label(cs, "llm_provider", "Planner LLM")
    mem = _label(cs, "database", "Session DB")
    vdb = _label(cs, "vector_database", "Long-term memory")
    q = _label(cs, "message_queue", "Tool fan-out queue")
    return _common_header(title) + f"""
    subgraph EDGE["Edge"]
      USR[Users / clients]:::ext
      WAF[WAF + auth proxy]:::edge
    end
    subgraph VPC["VPC"]
      subgraph PUB["Public subnets"]
        GW[{gw}]:::pub
        NAT[Egress proxy<br/>allow-listed]:::pub
      end
      subgraph PRIV["Private control plane"]
        ORCH[{orch}]:::priv
        Q[{q}]:::priv
        TOOL[Tool executors<br/>per-tool NSG]:::priv
      end
      subgraph DATA["Data"]
        MEM[{mem}]:::data
        VDB[{vdb}]:::data
      end
    end
    subgraph EXT["External (allow-listed)"]
      LLM[{llm}]:::ext
      API1[Tool API #1]:::ext
      API2[Tool API #2]:::ext
    end
    USR --> WAF --> GW --> ORCH
    ORCH --> MEM
    ORCH --> VDB
    ORCH --> Q --> TOOL
    TOOL --> NAT
    NAT --> API1
    NAT --> API2
    ORCH -. completions .-> LLM
"""


def _event_driven_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "API Gateway")
    app = _label(cs, "compute", "Producers / consumers")
    q = _label(cs, "message_queue", "Bus / queue")
    db = _label(cs, "database", "DB")
    return _common_header(title) + f"""
    subgraph EDGE["Edge"]
      USR[Producers]:::ext
      WAF[WAF]:::edge
    end
    subgraph VPC["VPC"]
      subgraph PUB["Public"]
        GW[{gw}]:::pub
        NAT[NAT gateway]:::pub
      end
      subgraph PRIV["Private"]
        APP[{app}]:::priv
      end
      subgraph DATA["Data"]
        Q[{q}]:::data
        DB[{db}]:::data
      end
    end
    USR --> WAF --> GW --> APP
    APP --> Q --> APP
    APP --> DB
    APP -. egress .-> NAT
"""


def _microservices_network(cs: ComponentSelectionResult, *, title: str) -> str:
    gw = _label(cs, "api_gateway", "Edge gateway")
    svc = _label(cs, "compute", "Service mesh")
    db = _label(cs, "database", "Per-service DBs")
    cache = _label(cs, "cache", "Cache")
    return _common_header(title) + f"""
    subgraph EDGE["Edge"]
      USR[Users]:::ext
      WAF[WAF + DDoS]:::edge
    end
    subgraph VPC["VPC"]
      subgraph PUB["Public"]
        ALB[{gw}]:::pub
        NAT[NAT gateway]:::pub
      end
      subgraph MESH["Private — service mesh"]
        SVC[{svc}<br/>mTLS east-west]:::priv
        CACHE[{cache}]:::priv
      end
      subgraph DATA["Data subnets per service"]
        DB[{db}]:::data
      end
    end
    USR --> WAF --> ALB --> SVC
    SVC --> CACHE
    SVC --> DB
    SVC -. egress .-> NAT
"""


def generate_network_diagram(
    components: ComponentSelectionResult,
    *,
    title: str = "System",
) -> str:
    """Return Mermaid source for a logical network/VPC topology view."""
    pattern = components.architecture_pattern
    if pattern == ArchitecturePattern.RAG_SYSTEM:
        return _rag_network(components, title=title)
    if pattern == ArchitecturePattern.FINE_TUNING_PIPELINE:
        return _fine_tuning_network(components, title=title)
    if pattern == ArchitecturePattern.REALTIME_INFERENCE:
        return _realtime_inference_network(components, title=title)
    if pattern == ArchitecturePattern.AGENTIC_AI_SYSTEM:
        return _agentic_network(components, title=title)
    if pattern == ArchitecturePattern.EVENT_DRIVEN:
        return _event_driven_network(components, title=title)
    if pattern == ArchitecturePattern.MICROSERVICES:
        return _microservices_network(components, title=title)
    return _three_tier_network(components, title=title)
