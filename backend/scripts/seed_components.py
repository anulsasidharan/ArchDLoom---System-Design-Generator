#!/usr/bin/env python3
"""Seed the component library (idempotent by component name)."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy.exc import OperationalError, ProgrammingError

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.models.component import Component  # noqa: E402
from app.repositories.component_repository import ComponentRepository  # noqa: E402

# Local icon paths (served from frontend/public/icons/ at /icons/...)
# Backend resolves these from backend/static/icons/ via icon_storage.py
_AWS_RDS   = "/icons/AWS/amazon-rds.svg"
_AWS_DDB   = "/icons/AWS/amazon-dynamodb.svg"
_AWS_CACHE = "/icons/AWS/amazon-elasticache.svg"
_AWS_APIGW = "/icons/AWS/amazon-api-gateway.svg"
_AWS_FG    = "/icons/AWS/aws-fargate.svg"
_AWS_EKS   = "/icons/AWS/amazon-eks.svg"
_AWS_MSK   = "/icons/AWS/amazon-msk.svg"
_AWS_GF    = "/icons/AWS/amazon-grafana.svg"
_AWS_PROM  = "/icons/AWS/amazon-prometheus.svg"
_AWS_BDK   = "/icons/AWS/amazon-bedrock.svg"
_AWS_SQS   = "/icons/AWS/amazon-sqs.svg"

_GCP_VTXAI = "/icons/GCP/vertex-ai.svg"
_GCP_GKE   = "/icons/GCP/gke.svg"
_GCP_CSQL  = "/icons/GCP/cloud-sql.svg"
_GCP_RUN   = "/icons/GCP/cloud-run.svg"
_GCP_APIGEE= "/icons/GCP/apigee.svg"

_AZ_OAI    = "/icons/Azure/azure-openai.svg"
_AZ_PG     = "/icons/Azure/azure-postgresql.svg"
_AZ_REDIS  = "/icons/Azure/azure-redis.svg"
_AZ_APIM   = "/icons/Azure/azure-api-management.svg"
_AZ_GF     = "/icons/Azure/azure-grafana.svg"
_AZ_EH     = "/icons/Azure/azure-event-hubs.svg"

# Simple Icons CDN — verified working slugs (for non-cloud vendors)
_SI    = "https://cdn.simpleicons.org"
_PG    = f"{_SI}/postgresql/336791"
_MONGO = f"{_SI}/mongodb/47A248"
_REDIS = f"{_SI}/redis/DC382D"
_DD    = f"{_SI}/datadog/632CA6"
_GF    = f"{_SI}/grafana/F46800"
_KAFKA = f"{_SI}/apachekafka/231F20"
_KONG  = f"{_SI}/kong/003459"
_GGL   = f"{_SI}/google/4285F4"
_ANT   = f"{_SI}/anthropic/191919"
_K8S   = f"{_SI}/kubernetes/326CE5"
_RMQ   = f"{_SI}/rabbitmq/FF6600"

# Letter icons for vendors with no icon file or CDN coverage
def _letter_icon(letter: str, bg: str, fg: str = "white") -> str:
    return (
        f"data:image/svg+xml,"
        f"%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        f"%3Crect width='64' height='64' rx='10' fill='{bg}'/%3E"
        f"%3Ctext x='32' y='44' font-size='32' text-anchor='middle' "
        f"fill='{fg}' font-family='Arial,sans-serif' font-weight='bold'%3E{letter}%3C/text%3E"
        f"%3C/svg%3E"
    )

_OAI  = _letter_icon("O", "%23412991")   # OpenAI brand purple
_PIN  = _letter_icon("P", "%2300B894")   # Pinecone teal
_WEA  = _letter_icon("W", "%23548BF4")   # Weaviate blue
_MIL  = _letter_icon("M", "%230ACFCF")   # Milvus cyan
_QDR  = _letter_icon("Q", "%23DC244C")   # Qdrant red
_COH  = _letter_icon("C", "%23D18EE2")   # Cohere purple
_VOY  = _letter_icon("V", "%235C6BC0")   # Voyage indigo


def _rows() -> list[Component]:
    return [
        # ── Databases ─────────────────────────────────────────────────────────
        Component(
            name="Amazon RDS for PostgreSQL",
            category="database",
            vendor="AWS",
            icon_url=_AWS_RDS,
            selection_criteria={
                "ideal_scale": "small to large relational workloads",
                "use_cases": ["ACID", "complex queries", "relational data"],
                "managed_service": True,
            },
            features=["Multi-AZ", "automated backups", "JSONB"],
            trade_offs={
                "pros": ["Strong consistency", "rich SQL", "managed ops"],
                "cons": ["Higher cost vs self-managed", "vertical scaling limits"],
            },
            pricing_model="per_hour",
            base_cost_usd=350.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/rds/",
        ),
        Component(
            name="Amazon DynamoDB",
            category="database",
            vendor="AWS",
            icon_url=_AWS_DDB,
            selection_criteria={
                "ideal_scale": "high throughput key-value",
                "use_cases": ["single-digit ms latency", "horizontal scale"],
                "managed_service": True,
            },
            features=["Serverless option", "global tables", "streams"],
            trade_offs={
                "pros": ["Elastic scale", "predictable keys"],
                "cons": ["Modeling constraints", "cross-region complexity"],
            },
            pricing_model="per_request",
            base_cost_usd=200.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/dynamodb/",
        ),
        Component(
            name="MongoDB Atlas",
            category="database",
            vendor="MongoDB",
            icon_url=_MONGO,
            selection_criteria={
                "ideal_scale": "document workloads",
                "use_cases": ["flexible schema", "rapid iteration"],
                "managed_service": True,
            },
            features=["Sharding", "search", "change streams"],
            trade_offs={
                "pros": ["Flexible documents", "developer velocity"],
                "cons": ["Operational tuning at scale", "join complexity"],
            },
            pricing_model="per_hour",
            base_cost_usd=280.0,
            alternatives=[],
            config_examples={},
            docs_url="https://www.mongodb.com/atlas",
        ),
        # ── Cache ─────────────────────────────────────────────────────────────
        Component(
            name="Amazon ElastiCache for Redis",
            category="cache",
            vendor="AWS",
            icon_url=_AWS_CACHE,
            selection_criteria={
                "ideal_scale": "session and hot-path caching",
                "use_cases": ["cache", "rate limiting", "queues lite"],
                "managed_service": True,
            },
            features=["Cluster mode", "TLS", "multi-AZ"],
            trade_offs={
                "pros": ["Fast in-memory access", "managed patching"],
                "cons": ["Memory-bound", "hot key risk"],
            },
            pricing_model="per_hour",
            base_cost_usd=120.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/elasticache/",
        ),
        Component(
            name="Redis OSS (self-hosted)",
            category="cache",
            vendor="Redis Ltd.",
            icon_url=_REDIS,
            selection_criteria={
                "ideal_scale": "teams comfortable operating Redis",
                "use_cases": ["cache", "pub/sub"],
                "managed_service": False,
            },
            features=["Rich data structures", "Lua scripting"],
            trade_offs={
                "pros": ["Full control", "no vendor markup"],
                "cons": ["You operate HA/failover", "patch burden"],
            },
            pricing_model="per_hour",
            base_cost_usd=80.0,
            alternatives=[],
            config_examples={},
            docs_url="https://redis.io/docs/",
        ),
        # ── API Gateway ───────────────────────────────────────────────────────
        Component(
            name="Amazon API Gateway",
            category="api_gateway",
            vendor="AWS",
            icon_url=_AWS_APIGW,
            selection_criteria={
                "ideal_scale": "REST/WebSocket APIs",
                "use_cases": ["edge auth", "throttling", "routing"],
                "managed_service": True,
            },
            features=["Usage plans", "VPC links", "request validation"],
            trade_offs={
                "pros": ["Integrated IAM/Lambda", "managed scaling"],
                "cons": ["Latency overhead vs direct NLB", "cost at volume"],
            },
            pricing_model="per_request",
            base_cost_usd=90.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/apigateway/",
        ),
        Component(
            name="Kong Gateway",
            category="api_gateway",
            vendor="Kong",
            icon_url=_KONG,
            selection_criteria={
                "ideal_scale": "multi-cloud / Kubernetes ingress",
                "use_cases": ["plugins", "traffic policies"],
                "managed_service": False,
            },
            features=["Plugin ecosystem", "declarative config"],
            trade_offs={
                "pros": ["Portable", "flexible policies"],
                "cons": ["Self-managed HA unless vendor Konnect"],
            },
            pricing_model="license_or_saas",
            base_cost_usd=150.0,
            alternatives=[],
            config_examples={},
            docs_url="https://konghq.com/",
        ),
        # ── Compute ───────────────────────────────────────────────────────────
        Component(
            name="AWS Fargate on ECS",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_FG,
            selection_criteria={
                "ideal_scale": "container services without EC2 ops",
                "use_cases": ["microservices", "batch"],
                "managed_service": True,
            },
            features=["Task definitions", "service autoscaling"],
            trade_offs={
                "pros": ["No server patching", "easy rollout"],
                "cons": ["Cold starts", "cost vs EC2 at steady load"],
            },
            pricing_model="per_vcpu_hour",
            base_cost_usd=900.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/ecs/",
        ),
        Component(
            name="Amazon EKS",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_EKS,
            selection_criteria={
                "ideal_scale": "Kubernetes-first teams",
                "use_cases": ["microservices", "operators"],
                "managed_service": True,
            },
            features=["Managed control plane", "IRSA", "add-ons"],
            trade_offs={
                "pros": ["Ecosystem", "portability"],
                "cons": ["Complexity", "cluster ops still matter"],
            },
            pricing_model="per_cluster_hour",
            base_cost_usd=750.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/eks/",
        ),
        # ── Monitoring ────────────────────────────────────────────────────────
        Component(
            name="Datadog",
            category="monitoring",
            vendor="Datadog",
            icon_url=_DD,
            selection_criteria={
                "ideal_scale": "full-stack observability",
                "use_cases": ["metrics", "logs", "traces"],
                "managed_service": True,
            },
            features=["APM", "SLOs", "dashboards"],
            trade_offs={
                "pros": ["Fast integration", "broad coverage"],
                "cons": ["Cost scales with cardinality"],
            },
            pricing_model="per_host",
            base_cost_usd=400.0,
            alternatives=[],
            config_examples={},
            docs_url="https://www.datadoghq.com/",
        ),
        Component(
            name="Prometheus + Grafana",
            category="monitoring",
            vendor="CNCF",
            icon_url=_AWS_GF,
            selection_criteria={
                "ideal_scale": "metrics-first observability",
                "use_cases": ["Kubernetes", "SLO burn"],
                "managed_service": False,
            },
            features=["PromQL", "alerting", "dashboards"],
            trade_offs={
                "pros": ["OSS", "deep K8s metrics"],
                "cons": ["Long-term storage needs planning"],
            },
            pricing_model="self_hosted",
            base_cost_usd=120.0,
            alternatives=[],
            config_examples={},
            docs_url="https://prometheus.io/",
        ),
        # ── Message Queue ─────────────────────────────────────────────────────
        Component(
            name="Amazon MSK (Kafka)",
            category="message_queue",
            vendor="AWS",
            icon_url=_AWS_MSK,
            selection_criteria={
                "ideal_scale": "high-throughput streaming",
                "use_cases": ["event-driven", "audit logs"],
                "managed_service": True,
            },
            features=["Kafka compatibility", "multi-AZ"],
            trade_offs={
                "pros": ["Durable log", "replay"],
                "cons": ["Operational tuning", "cost"],
            },
            pricing_model="per_broker_hour",
            base_cost_usd=600.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/msk/",
        ),
        Component(
            name="Amazon SQS",
            category="message_queue",
            vendor="AWS",
            icon_url=_AWS_SQS,
            selection_criteria={
                "ideal_scale": "simple durable queues",
                "use_cases": ["async workers", "decoupling"],
                "managed_service": True,
            },
            features=["FIFO option", "DLQ"],
            trade_offs={
                "pros": ["Simple ops", "elastic"],
                "cons": ["Not a log like Kafka", "ordering caveats"],
            },
            pricing_model="per_request",
            base_cost_usd=40.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/sqs/",
        ),
        # ── LLM Providers ─────────────────────────────────────────────────────
        Component(
            name="OpenAI GPT API",
            category="llm_provider",
            vendor="OpenAI",
            icon_url=_OAI,
            selection_criteria={
                "ideal_scale": "hosted LLM inference",
                "use_cases": ["chat", "agents", "tools"],
                "managed_service": True,
            },
            features=["Tool calling", "large context windows"],
            trade_offs={
                "pros": ["Fast iteration", "strong general models"],
                "cons": ["Vendor dependency", "token costs"],
            },
            pricing_model="per_token",
            base_cost_usd=500.0,
            alternatives=[],
            config_examples={},
            docs_url="https://platform.openai.com/docs/",
        ),
        Component(
            name="Anthropic Claude API",
            category="llm_provider",
            vendor="Anthropic",
            icon_url=_ANT,
            selection_criteria={
                "ideal_scale": "hosted LLM inference",
                "use_cases": ["enterprise workloads", "long context"],
                "managed_service": True,
            },
            features=["Strong reasoning", "tool use"],
            trade_offs={
                "pros": ["Quality", "safety tooling"],
                "cons": ["Pricing vs OSS models"],
            },
            pricing_model="per_token",
            base_cost_usd=520.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.anthropic.com/",
        ),
        Component(
            name="AWS Bedrock (managed LLMs)",
            category="llm_provider",
            vendor="AWS",
            icon_url=_AWS_BDK,
            selection_criteria={
                "ideal_scale": "enterprise VPC inference",
                "use_cases": ["fine-tuned endpoints", "multi-model routing"],
                "managed_service": True,
            },
            features=["IAM", "VPC endpoints", "multiple foundation models"],
            trade_offs={
                "pros": ["Data residency controls", "unified AWS billing"],
                "cons": ["Model catalog varies by region"],
            },
            pricing_model="per_token",
            base_cost_usd=480.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/bedrock/",
        ),
        Component(
            name="Google Gemini API",
            category="llm_provider",
            vendor="Google",
            icon_url=_GCP_VTXAI,
            selection_criteria={
                "ideal_scale": "hosted multimodal inference",
                "use_cases": ["agents", "long-context tasks"],
                "managed_service": True,
            },
            features=["Multimodal inputs", "large context"],
            trade_offs={
                "pros": ["Strong general capability", "Google ecosystem"],
                "cons": ["Cross-cloud egress if not on GCP"],
            },
            pricing_model="per_token",
            base_cost_usd=490.0,
            alternatives=[],
            config_examples={},
            docs_url="https://ai.google.dev/",
        ),
        # ── Vector Databases ──────────────────────────────────────────────────
        Component(
            name="Pinecone",
            category="vector_database",
            vendor="Pinecone",
            icon_url=_PIN,
            selection_criteria={
                "ideal_scale": "managed vector search",
                "use_cases": ["RAG", "semantic search"],
                "managed_service": True,
            },
            features=["Namespaces", "metadata filters"],
            trade_offs={
                "pros": ["Low ops", "predictable latency"],
                "cons": ["Vendor lock-in", "cost at scale"],
            },
            pricing_model="per_pod_hour",
            base_cost_usd=300.0,
            alternatives=[],
            config_examples={},
            docs_url="https://www.pinecone.io/",
        ),
        Component(
            name="pgvector on RDS PostgreSQL",
            category="vector_database",
            vendor="PostgreSQL",
            icon_url=f"{_SI}/postgresql/336791",
            selection_criteria={
                "ideal_scale": "moderate vector workloads",
                "use_cases": ["RAG", "same DB as OLTP"],
                "managed_service": True,
            },
            features=["SQL joins", "transactional"],
            trade_offs={
                "pros": ["Reuse Postgres ops", "lower moving parts"],
                "cons": ["Less specialized than dedicated vector DB"],
            },
            pricing_model="per_hour",
            base_cost_usd=260.0,
            alternatives=[],
            config_examples={},
            docs_url="https://github.com/pgvector/pgvector",
        ),
        Component(
            name="Weaviate Cloud",
            category="vector_database",
            vendor="Weaviate",
            icon_url=_WEA,
            selection_criteria={
                "ideal_scale": "managed hybrid vector + keyword",
                "use_cases": ["RAG", "semantic search", "multi-tenant SaaS"],
                "managed_service": True,
            },
            features=["GraphQL API", "hybrid search", "multi-tenancy"],
            trade_offs={
                "pros": ["Flexible schema", "good DX"],
                "cons": ["Operational tuning for large shards"],
            },
            pricing_model="per_pod_hour",
            base_cost_usd=290.0,
            alternatives=[],
            config_examples={},
            docs_url="https://weaviate.io/",
        ),
        Component(
            name="Milvus",
            category="vector_database",
            vendor="Zilliz",
            icon_url=_MIL,
            selection_criteria={
                "ideal_scale": "high-throughput ANN at scale",
                "use_cases": ["RAG", "recommendations", "similarity"],
                "managed_service": False,
            },
            features=["GPU index options", "Kafka ingestion"],
            trade_offs={
                "pros": ["Very scalable ANN", "active OSS community"],
                "cons": ["Self-managed unless Zilliz Cloud"],
            },
            pricing_model="self_hosted",
            base_cost_usd=180.0,
            alternatives=[],
            config_examples={},
            docs_url="https://milvus.io/",
        ),
        Component(
            name="Qdrant Cloud",
            category="vector_database",
            vendor="Qdrant",
            icon_url=_QDR,
            selection_criteria={
                "ideal_scale": "developer-friendly vector search",
                "use_cases": ["RAG", "faceted filters"],
                "managed_service": True,
            },
            features=["Rich filtering", "snapshots"],
            trade_offs={
                "pros": ["Simple APIs", "good local dev story"],
                "cons": ["Compare ecosystem vs hyperscaler-native"],
            },
            pricing_model="per_gb_hour",
            base_cost_usd=240.0,
            alternatives=[],
            config_examples={},
            docs_url="https://qdrant.tech/",
        ),
        # ── Embedding Models ──────────────────────────────────────────────────
        Component(
            name="OpenAI text-embedding-3-large",
            category="embedding_model",
            vendor="OpenAI",
            icon_url=_OAI,
            selection_criteria={
                "ideal_scale": "hosted embeddings",
                "use_cases": ["RAG ingestion", "semantic search"],
                "managed_service": True,
            },
            features=["Strong retrieval quality"],
            trade_offs={
                "pros": ["Easy API", "good defaults"],
                "cons": ["Cost tied to tokens"],
            },
            pricing_model="per_token",
            base_cost_usd=120.0,
            alternatives=[],
            config_examples={},
            docs_url="https://platform.openai.com/docs/guides/embeddings",
        ),
        Component(
            name="Amazon Titan Embeddings",
            category="embedding_model",
            vendor="AWS",
            icon_url=_AWS_BDK,
            selection_criteria={
                "ideal_scale": "Bedrock embeddings",
                "use_cases": ["private VPC inference patterns"],
                "managed_service": True,
            },
            features=["Integrated IAM", "VPC endpoints"],
            trade_offs={
                "pros": ["AWS-native billing", "network controls"],
                "cons": ["Model choice narrower vs pure ML vendors"],
            },
            pricing_model="per_token",
            base_cost_usd=110.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/bedrock/",
        ),
        Component(
            name="Cohere Embed (v3)",
            category="embedding_model",
            vendor="Cohere",
            icon_url=_COH,
            selection_criteria={
                "ideal_scale": "hosted embeddings",
                "use_cases": ["RAG", "classification features"],
                "managed_service": True,
            },
            features=["Multilingual", "task-type variants"],
            trade_offs={
                "pros": ["Simple API", "strong retrieval embeddings"],
                "cons": ["Pricing vs OSS sentence-transformers"],
            },
            pricing_model="per_token",
            base_cost_usd=95.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.cohere.com/",
        ),
        Component(
            name="Voyage AI Embeddings",
            category="embedding_model",
            vendor="Voyage AI",
            icon_url=_VOY,
            selection_criteria={
                "ideal_scale": "retrieval-optimized embeddings",
                "use_cases": ["RAG", "domain packs"],
                "managed_service": True,
            },
            features=["Domain-specific embedding models"],
            trade_offs={
                "pros": ["Strong retrieval benchmarks on many tasks"],
                "cons": ["Additional vendor in stack"],
            },
            pricing_model="per_token",
            base_cost_usd=100.0,
            alternatives=[],
            config_examples={},
            docs_url="https://www.voyageai.com/",
        ),
        # ── Azure Components ──────────────────────────────────────────────────
        Component(
            name="Azure Database for PostgreSQL",
            category="database",
            vendor="Azure",
            icon_url=_AZ_PG,
            selection_criteria={
                "ideal_scale": "small to large relational workloads on Azure",
                "use_cases": ["ACID", "complex queries", "relational data"],
                "managed_service": True,
            },
            features=["Flexible server", "automated backups", "zone redundancy"],
            trade_offs={
                "pros": ["Azure-native IAM", "high availability zones", "managed ops"],
                "cons": ["Azure lock-in", "cost vs self-managed"],
            },
            pricing_model="per_hour",
            base_cost_usd=320.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/postgresql/",
        ),
        Component(
            name="Azure Cache for Redis",
            category="cache",
            vendor="Azure",
            icon_url=_AZ_REDIS,
            selection_criteria={
                "ideal_scale": "low-latency caching on Azure",
                "use_cases": ["session cache", "rate limiting", "pub/sub"],
                "managed_service": True,
            },
            features=["Geo-replication", "private endpoints", "zone redundancy"],
            trade_offs={
                "pros": ["Azure-native networking", "managed scaling"],
                "cons": ["Azure lock-in", "higher cost vs self-managed Redis"],
            },
            pricing_model="per_hour",
            base_cost_usd=190.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/",
        ),
        Component(
            name="Azure Event Hubs",
            category="message_queue",
            vendor="Azure",
            icon_url=_AZ_EH,
            selection_criteria={
                "ideal_scale": "high-throughput event streaming on Azure",
                "use_cases": ["event ingestion", "log streaming", "Kafka-compatible"],
                "managed_service": True,
            },
            features=["Kafka endpoint", "auto-inflate", "capture to storage"],
            trade_offs={
                "pros": ["Kafka-compatible API", "serverless tier", "Azure-native"],
                "cons": ["Pricing complexity", "less flexible routing than Kafka"],
            },
            pricing_model="per_throughput_unit",
            base_cost_usd=220.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/event-hubs/",
        ),
        Component(
            name="Azure API Management",
            category="api_gateway",
            vendor="Azure",
            icon_url=_AZ_APIM,
            selection_criteria={
                "ideal_scale": "enterprise API gateway on Azure",
                "use_cases": ["rate limiting", "auth", "routing", "developer portal"],
                "managed_service": True,
            },
            features=["Developer portal", "policy engine", "OAuth2/JWT", "analytics"],
            trade_offs={
                "pros": ["Rich policy engine", "built-in developer portal", "Azure-native"],
                "cons": ["Higher cost vs open-source alternatives", "cold start on consumption tier"],
            },
            pricing_model="per_hour",
            base_cost_usd=480.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/api-management/",
        ),
        Component(
            name="Azure OpenAI Service",
            category="llm_provider",
            vendor="Azure",
            icon_url=_AZ_OAI,
            selection_criteria={
                "ideal_scale": "enterprise OpenAI on private Azure endpoints",
                "use_cases": ["GPT-4o", "embeddings", "compliance-sensitive AI"],
                "managed_service": True,
            },
            features=["Private networking", "Azure AD auth", "content filtering", "PTU deployments"],
            trade_offs={
                "pros": ["Data residency", "Azure IAM integration", "SLA-backed"],
                "cons": ["Model lag vs OpenAI direct", "quota management overhead"],
            },
            pricing_model="per_token",
            base_cost_usd=550.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/ai-services/openai/",
        ),
        Component(
            name="Azure Monitor + Managed Grafana",
            category="monitoring",
            vendor="Azure",
            icon_url=_AZ_GF,
            selection_criteria={
                "ideal_scale": "observability for Azure workloads",
                "use_cases": ["metrics", "logs", "dashboards", "alerts"],
                "managed_service": True,
            },
            features=["Azure Metrics", "Log Analytics", "Managed Grafana", "Application Insights"],
            trade_offs={
                "pros": ["Native Azure integration", "no infra to manage"],
                "cons": ["Cost at high log volume", "steeper learning curve for non-Azure teams"],
            },
            pricing_model="per_GB",
            base_cost_usd=200.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/azure-monitor/",
        ),
    ]


def main() -> None:
    session = SessionLocal()
    repo = ComponentRepository(session)
    try:
        added = 0
        updated = 0
        for row in _rows():
            existing = repo.find_by_name(row.name)
            if existing:
                # Patch icon_url and trade_offs on existing records
                if existing.icon_url != row.icon_url:
                    existing.icon_url = row.icon_url
                    updated += 1
            else:
                session.add(row)
                added += 1
        session.commit()
        print(f"Seed complete ({added} inserted, {updated} updated).")
    except ProgrammingError as e:
        orig = getattr(e, "orig", e)
        detail = str(orig)
        if "does not exist" in detail or "UndefinedTable" in type(orig).__name__:
            print(
                'Database schema is missing (e.g. relation "components" does not exist).\n'
                "Apply Alembic migrations first, then run this script again.\n"
                "  From backend/ (same DATABASE_URL as this script):\n"
                "    alembic upgrade head\n"
                "  Or with Docker (repo root):\n"
                "    docker compose exec api alembic upgrade head",
                file=sys.stderr,
            )
            raise SystemExit(1) from e
        raise
    except OperationalError as e:
        print(
            "Cannot reach PostgreSQL.\n"
            "  Ensure DATABASE_URL matches a running server.",
            file=sys.stderr,
        )
        raise SystemExit(1) from e
    finally:
        session.close()


if __name__ == "__main__":
    main()
