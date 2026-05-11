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

# AWS Architecture icons (Arch_* paths have no spaces)
_AWS_AURORA = "/icons/AWS/Arch_Amazon-Aurora_64.svg"
_AWS_OS = "/icons/AWS/Arch_Amazon-OpenSearch-Service_64.svg"
_AWS_RS = "/icons/AWS/Arch_Amazon-Redshift_64.svg"
_AWS_DOCDB = "/icons/AWS/Arch_Amazon-DocumentDB_64.svg"
_AWS_NEPTUNE = "/icons/AWS/Arch_Amazon-Neptune_64.svg"
_AWS_TS = "/icons/AWS/Arch_Amazon-Timestream_64.svg"
_AWS_KEYSPACES = "/icons/AWS/Arch_Amazon-Keyspaces_64.svg"
_AWS_MEMDB = "/icons/AWS/Arch_Amazon-MemoryDB_64.svg"
_AWS_ECACHE_ARCH = "/icons/AWS/Arch_Amazon-ElastiCache_64.svg"
_AWS_LBD = "/icons/AWS/Arch_AWS-Lambda_64.svg"
_AWS_EC2 = "/icons/AWS/Arch_Amazon-EC2_64.svg"
_AWS_ECS = "/icons/AWS/Arch_Amazon-Elastic-Container-Service_64.svg"
_AWS_APP_RUNNER = "/icons/AWS/Arch_AWS-App-Runner_64.svg"
_AWS_BEANSTALK = "/icons/AWS/Arch_AWS-Elastic-Beanstalk_64.svg"
_AWS_BATCH = "/icons/AWS/Arch_AWS-Batch_64.svg"
_AWS_SNS = "/icons/AWS/Arch_Amazon-Simple-Notification-Service_64.svg"
_AWS_EVT = "/icons/AWS/Arch_Amazon-EventBridge_64.svg"
_AWS_SFN = "/icons/AWS/Arch_AWS-Step-Functions_64.svg"
_AWS_KDS = "/icons/AWS/Arch_Amazon-Kinesis-Data-Streams_64.svg"
_AWS_SM = "/icons/AWS/Arch_Amazon-SageMaker-AI_64.svg"
_AWS_ATHENA = "/icons/AWS/Arch_Amazon-Athena_64.svg"
_AWS_CW = "/icons/AWS/Arch_Amazon-CloudWatch_64.svg"
_AWS_XRAY = "/icons/AWS/Arch_AWS-X-Ray_64.svg"
_AWS_KENDRA = "/icons/AWS/Arch_Amazon-Kendra_64.svg"

# GCP product icons (percent-encode spaces in URL paths)
_GCP_BQ = "/icons/GCP/BigQuery/BigQuery-512-color.svg"
_GCP_SPANNER = "/icons/GCP/Cloud%20Spanner/CloudSpanner-512-color.svg"
_GCP_ALLOY = "/icons/GCP/AlloyDB/AlloyDB-512-color.svg"
_GCP_CE = "/icons/GCP/Compute%20Engine/ComputeEngine-512-color-rgb.svg"
_GCP_VERTEX_DIR = "/icons/GCP/Vertex%20AI/VertexAI-512-color.svg"

# Azure paths / brand fallbacks
_AZ_ML = "/icons/Azure/ai + machine learning/10166-icon-service-Machine-Learning.svg"
_AZ_SEARCH = "/icons/Azure/general/10834-icon-service-Search.svg"
_AZ_QUEUE = "/icons/Azure/general/10840-icon-service-Storage-Queue.svg"
_AZ_LOG = "/icons/Azure/monitor/00007-icon-service-Activity-Log.svg"
_AZ_DB_BRICKS = "/icons/Azure/analytics/10787-icon-service-Azure-Databricks.svg"

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
_SI_GCP = f"{_SI}/googlecloud/4285F4"
#
# Note: some Microsoft/Azure brand icons are not available via cdn.simpleicons.org
# (requests return 404). For those, use a local data-uri placeholder instead.
# (We assign these after `_letter_icon` is defined below to avoid NameError.)
_SI_AZURE = ""
_SI_AZ_FN = ""

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

# Azure placeholders (avoid SimpleIcons 404)
_SI_AZURE = _letter_icon("AZ", "%230078D4")   # Azure
_SI_AZ_FN = _letter_icon("Fn", "%230063AF")  # Azure Functions

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
        # ── Expanded AWS catalog ───────────────────────────────────────────────
        Component(
            name="Amazon Aurora",
            category="database",
            vendor="AWS",
            icon_url=_AWS_AURORA,
            selection_criteria={
                "ideal_scale": "relational OLTP with higher throughput than vanilla RDS",
                "use_cases": ["MySQL/Postgres compatibility", "global clusters", "auto-scaling storage"],
                "managed_service": True,
            },
            features=["Storage autoscaling", "read replicas", "backtrack (MySQL)"],
            trade_offs={
                "pros": ["High durability", "faster failover options", "AWS-native HA"],
                "cons": ["Premium vs standard RDS", "some engine limits vs vanilla Postgres"],
            },
            pricing_model="per_hour",
            base_cost_usd=420.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/",
        ),
        Component(
            name="Amazon RDS for MySQL",
            category="database",
            vendor="AWS",
            icon_url=_AWS_RDS,
            selection_criteria={
                "ideal_scale": "managed MySQL relational workloads",
                "use_cases": ["ACID", "LAMP stacks", "read replicas"],
                "managed_service": True,
            },
            features=["Multi-AZ", "automated backups", "Performance Insights"],
            trade_offs={
                "pros": ["Familiar MySQL", "managed patching/upgrades"],
                "cons": ["Vertical scaling ceilings", "engine tuning still required at scale"],
            },
            pricing_model="per_hour",
            base_cost_usd=330.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_MySQL.html",
        ),
        Component(
            name="Amazon OpenSearch Service",
            category="database",
            vendor="AWS",
            icon_url=_AWS_OS,
            selection_criteria={
                "ideal_scale": "search, logs, and analytics at large scale",
                "use_cases": ["full-text search", "log analytics", "security analytics"],
                "managed_service": True,
            },
            features=["OpenSearch dashboards", "fine-grained access control", "UltraWarm/Cold tiers"],
            trade_offs={
                "pros": ["ElasticSearch-compatible APIs", "managed operations"],
                "cons": ["Cluster sizing complexity", "cost at high retention"],
            },
            pricing_model="per_instance_hour",
            base_cost_usd=480.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/opensearch-service/",
        ),
        Component(
            name="Amazon Redshift",
            category="database",
            vendor="AWS",
            icon_url=_AWS_RS,
            selection_criteria={
                "ideal_scale": "cloud data warehouse and large analytical queries",
                "use_cases": ["BI", "ETL targets", "lake house patterns with Redshift Spectrum"],
                "managed_service": True,
            },
            features=["RA3 nodes", "data sharing", "ML in SQL (Redshift ML)"],
            trade_offs={
                "pros": ["Strong price/performance for analytics", "deep AWS integration"],
                "cons": ["Not OLTP", "workload tuning and distribution keys matter"],
            },
            pricing_model="per_node_hour",
            base_cost_usd=950.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/redshift/",
        ),
        Component(
            name="Amazon DocumentDB (with MongoDB compatibility)",
            category="database",
            vendor="AWS",
            icon_url=_AWS_DOCDB,
            selection_criteria={
                "ideal_scale": "MongoDB-compatible document workloads on AWS",
                "use_cases": ["document model", "JSON workloads", "managed Mongo API"],
                "managed_service": True,
            },
            features=["Replica sets", "TLS", "automated backups"],
            trade_offs={
                "pros": ["Operational simplicity vs self-managed MongoDB"],
                "cons": ["Compatibility gaps vs MongoDB Atlas for some features"],
            },
            pricing_model="per_instance_hour",
            base_cost_usd=410.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/documentdb/",
        ),
        Component(
            name="Amazon Neptune",
            category="database",
            vendor="AWS",
            icon_url=_AWS_NEPTUNE,
            selection_criteria={
                "ideal_scale": "graph and highly connected datasets",
                "use_cases": ["knowledge graphs", "fraud graphs", "Gremlin/SPARQL"],
                "managed_service": True,
            },
            features=["Gremlin", "SPARQL", "Neptune ML"],
            trade_offs={
                "pros": ["Purpose-built graph engine", "HA options"],
                "cons": ["Specialized skillset", "different query model than SQL"],
            },
            pricing_model="per_instance_hour",
            base_cost_usd=520.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/neptune/",
        ),
        Component(
            name="Amazon Timestream",
            category="database",
            vendor="AWS",
            icon_url=_AWS_TS,
            selection_criteria={
                "ideal_scale": "time-series telemetry and IoT-scale ingest",
                "use_cases": ["metrics", "IoT telemetry", "operational analytics"],
                "managed_service": True,
            },
            features=["Serverless option", "SQL interface", "tiered storage"],
            trade_offs={
                "pros": ["Time-series optimized", "low ops"],
                "cons": ["Not a general-purpose SQL database"],
            },
            pricing_model="per_gb_ingest",
            base_cost_usd=260.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/timestream/",
        ),
        Component(
            name="Amazon Keyspaces (for Apache Cassandra)",
            category="database",
            vendor="AWS",
            icon_url=_AWS_KEYSPACES,
            selection_criteria={
                "ideal_scale": "Cassandra-compatible wide-column workloads",
                "use_cases": ["high write throughput", "multi-AZ resilience", "Cassandra API"],
                "managed_service": True,
            },
            features=["Cassandra drivers", "on-demand capacity", "PITR"],
            trade_offs={
                "pros": ["No Cassandra cluster ops", "elastic throughput"],
                "cons": ["Cassandra data modeling required", "cost at sustained high throughput"],
            },
            pricing_model="per_request",
            base_cost_usd=310.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/keyspaces/",
        ),
        Component(
            name="Amazon Athena",
            category="database",
            vendor="AWS",
            icon_url=_AWS_ATHENA,
            selection_criteria={
                "ideal_scale": "ad hoc SQL over data lakes in S3",
                "use_cases": ["lake queries", "on-demand analytics", "partitioned tables"],
                "managed_service": True,
            },
            features=["Presto/Trino engine", "federated queries", "Iceberg/Hudi support"],
            trade_offs={
                "pros": ["No servers to manage", "pay per scanned data"],
                "cons": ["Scan costs without strict partitioning", "not OLTP"],
            },
            pricing_model="per_tb_scanned",
            base_cost_usd=140.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/athena/",
        ),
        Component(
            name="Amazon ElastiCache for Memcached",
            category="cache",
            vendor="AWS",
            icon_url=_AWS_ECACHE_ARCH,
            selection_criteria={
                "ideal_scale": "simple object caching with horizontal scale-out",
                "use_cases": ["object cache", "session offload", "simple key/value"],
                "managed_service": True,
            },
            features=["Multi-AZ", "TLS", "horizontal scaling"],
            trade_offs={
                "pros": ["Simple protocol", "predictable performance"],
                "cons": ["Fewer data structures vs Redis", "cluster-aware client needed at scale"],
            },
            pricing_model="per_hour",
            base_cost_usd=95.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/",
        ),
        Component(
            name="Amazon MemoryDB for Redis",
            category="cache",
            vendor="AWS",
            icon_url=_AWS_MEMDB,
            selection_criteria={
                "ideal_scale": "Redis-compatible workloads needing durable primary",
                "use_cases": ["primary datastore patterns", "low-latency leaderboards"],
                "managed_service": True,
            },
            features=["Durability", "Multi-AZ", "Redis data structures"],
            trade_offs={
                "pros": ["Strong durability story vs pure cache"],
                "cons": ["Higher cost than ElastiCache for pure cache use cases"],
            },
            pricing_model="per_hour",
            base_cost_usd=210.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/memorydb/",
        ),
        Component(
            name="AWS Lambda",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_LBD,
            selection_criteria={
                "ideal_scale": "event-driven bursts and microservices glue",
                "use_cases": ["webhooks", "stream processing", "API backends with low steady traffic"],
                "managed_service": True,
            },
            features=["Per-ms billing", "VPC support", "concurrency controls"],
            trade_offs={
                "pros": ["No servers", "elastic scale"],
                "cons": ["Cold starts", "runtime/size limits", "long-running jobs are a poor fit"],
            },
            pricing_model="per_request",
            base_cost_usd=180.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/lambda/",
        ),
        Component(
            name="Amazon EC2",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_EC2,
            selection_criteria={
                "ideal_scale": "full control over OS and instance types",
                "use_cases": ["lift-and-shift", "custom AMIs", "GPU workloads"],
                "managed_service": False,
            },
            features=["Broad instance families", "placement groups", "EBS optimization"],
            trade_offs={
                "pros": ["Maximum flexibility", "predictable performance tuning"],
                "cons": ["You manage patching/HA unless layered with ASG/EKS"],
            },
            pricing_model="per_hour",
            base_cost_usd=500.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/ec2/",
        ),
        Component(
            name="Amazon ECS (EC2 launch type)",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_ECS,
            selection_criteria={
                "ideal_scale": "containers where you want to manage EC2 capacity",
                "use_cases": ["cost-optimized steady workloads", "GPU nodes", "custom AMIs"],
                "managed_service": True,
            },
            features=["Deep AWS integration", "task definitions", "service discovery"],
            trade_offs={
                "pros": ["More cost control vs Fargate for steady loads"],
                "cons": ["More ops than Fargate", "capacity planning required"],
            },
            pricing_model="per_hour",
            base_cost_usd=620.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/ecs/",
        ),
        Component(
            name="AWS App Runner",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_APP_RUNNER,
            selection_criteria={
                "ideal_scale": "containerized web services and APIs with minimal ops",
                "use_cases": ["internal tools", "simple HTTP services", "from image/repo deploys"],
                "managed_service": True,
            },
            features=["Auto scaling", "TLS", "VPC connector"],
            trade_offs={
                "pros": ["Very simple deploy path", "good for small teams"],
                "cons": ["Less control than ECS/EKS", "feature surface smaller than K8s"],
            },
            pricing_model="per_vcpu_hour",
            base_cost_usd=240.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/apprunner/",
        ),
        Component(
            name="AWS Elastic Beanstalk",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_BEANSTALK,
            selection_criteria={
                "ideal_scale": "classic web apps with managed platform updates",
                "use_cases": ["Tomcat/.NET/Node platforms", "gradual modernization"],
                "managed_service": True,
            },
            features=["Rolling deployments", "health reporting", "integrated load balancer"],
            trade_offs={
                "pros": ["Faster path than raw EC2 for many web stacks"],
                "cons": ["Less “cloud native” than containers for large orgs"],
            },
            pricing_model="per_hour",
            base_cost_usd=380.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/elasticbeanstalk/",
        ),
        Component(
            name="AWS Batch",
            category="compute",
            vendor="AWS",
            icon_url=_AWS_BATCH,
            selection_criteria={
                "ideal_scale": "batch and HPC-style jobs on AWS",
                "use_cases": ["ETL jobs", "rendering", "ML training jobs"],
                "managed_service": True,
            },
            features=["Job queues", "Spot integration", "array jobs"],
            trade_offs={
                "pros": ["Scales out workers automatically", "good Spot economics"],
                "cons": ["Not for interactive low-latency serving"],
            },
            pricing_model="per_vcpu_hour",
            base_cost_usd=320.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/batch/",
        ),
        Component(
            name="Amazon SNS",
            category="message_queue",
            vendor="AWS",
            icon_url=_AWS_SNS,
            selection_criteria={
                "ideal_scale": "pub/sub fan-out and mobile push patterns",
                "use_cases": ["fan-out", "SQS integration", "application events"],
                "managed_service": True,
            },
            features=["Topics", "FIFO topics", "message filtering"],
            trade_offs={
                "pros": ["Simple pub/sub", "high fan-out"],
                "cons": ["Different semantics than Kafka logs", "delivery guarantees vary by subscriber"],
            },
            pricing_model="per_million_requests",
            base_cost_usd=35.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/sns/",
        ),
        Component(
            name="Amazon EventBridge",
            category="message_queue",
            vendor="AWS",
            icon_url=_AWS_EVT,
            selection_criteria={
                "ideal_scale": "event buses and SaaS integration on AWS",
                "use_cases": ["event routing", "scheduled rules", "partner integrations"],
                "managed_service": True,
            },
            features=["Schema registry", "content filtering", "archive/replay"],
            trade_offs={
                "pros": ["Great AWS-native integration", "low ops"],
                "cons": ["Not a durable log like Kafka for all patterns"],
            },
            pricing_model="per_million_events",
            base_cost_usd=45.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/eventbridge/",
        ),
        Component(
            name="AWS Step Functions",
            category="message_queue",
            vendor="AWS",
            icon_url=_AWS_SFN,
            selection_criteria={
                "ideal_scale": "orchestrated workflows across AWS services",
                "use_cases": ["Saga patterns", "human approvals", "ML pipelines glue"],
                "managed_service": True,
            },
            features=["Express workflows", "SDK integrations", "map state parallelism"],
            trade_offs={
                "pros": ["Durable orchestration", "visual workflows"],
                "cons": ["State transition costs at huge scale", "AWS-centric"],
            },
            pricing_model="per_transition",
            base_cost_usd=70.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/step-functions/",
        ),
        Component(
            name="Amazon Kinesis Data Streams",
            category="message_queue",
            vendor="AWS",
            icon_url=_AWS_KDS,
            selection_criteria={
                "ideal_scale": "real-time streaming ingestion and consumers",
                "use_cases": ["clickstreams", "metrics pipelines", "fan-out consumers"],
                "managed_service": True,
            },
            features=["On-demand mode", "enhanced fan-out", "KCL consumers"],
            trade_offs={
                "pros": ["Low-latency streaming", "AWS-native integrations"],
                "cons": ["Throughput planning/shards", "different model than SQS"],
            },
            pricing_model="per_shard_hour",
            base_cost_usd=280.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/streams/latest/dev/",
        ),
        Component(
            name="Amazon SageMaker",
            category="llm_provider",
            vendor="AWS",
            icon_url=_AWS_SM,
            selection_criteria={
                "ideal_scale": "end-to-end ML lifecycle on AWS",
                "use_cases": ["training", "hosted endpoints", "MLOps pipelines"],
                "managed_service": True,
            },
            features=["Notebooks", "Feature Store", "Model Registry", "Pipelines"],
            trade_offs={
                "pros": ["Deep AWS integration", "broad ML surface area"],
                "cons": ["Complexity", "cost without governance"],
            },
            pricing_model="per_hour",
            base_cost_usd=650.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/sagemaker/",
        ),
        Component(
            name="Amazon Kendra",
            category="llm_provider",
            vendor="AWS",
            icon_url=_AWS_KENDRA,
            selection_criteria={
                "ideal_scale": "enterprise search with retrieval quality focus",
                "use_cases": ["RAG connectors", "internal knowledge search", "FAQ bots"],
                "managed_service": True,
            },
            features=["Connectors", "FAQ", "relevance tuning"],
            trade_offs={
                "pros": ["Fast enterprise search outcomes", "AWS IAM integration"],
                "cons": ["Less flexible than bespoke vector stacks for some RAG patterns"],
            },
            pricing_model="per_query_unit",
            base_cost_usd=420.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/kendra/",
        ),
        Component(
            name="Amazon OpenSearch (k-NN vectors)",
            category="vector_database",
            vendor="AWS",
            icon_url=_AWS_OS,
            selection_criteria={
                "ideal_scale": "vector + keyword hybrid search on AWS",
                "use_cases": ["RAG", "semantic search", "hybrid retrieval"],
                "managed_service": True,
            },
            features=["k-NN indexes", "filters", "aggregations"],
            trade_offs={
                "pros": ["Single platform for logs + vectors", "familiar OpenSearch APIs"],
                "cons": ["Tuning shards/replicas for latency", "cost at large embeddings"],
            },
            pricing_model="per_instance_hour",
            base_cost_usd=440.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html",
        ),
        Component(
            name="Amazon CloudWatch",
            category="monitoring",
            vendor="AWS",
            icon_url=_AWS_CW,
            selection_criteria={
                "ideal_scale": "AWS-native metrics/logs/alarms",
                "use_cases": ["infra metrics", "application logs", "SLO alerting"],
                "managed_service": True,
            },
            features=["Logs Insights", "alarms", "dashboards", "X-Ray integration"],
            trade_offs={
                "pros": ["First-class AWS integration", "fast time-to-value"],
                "cons": ["Log ingestion costs at volume", "cross-cloud limited"],
            },
            pricing_model="per_GB",
            base_cost_usd=160.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/cloudwatch/",
        ),
        Component(
            name="AWS X-Ray",
            category="monitoring",
            vendor="AWS",
            icon_url=_AWS_XRAY,
            selection_criteria={
                "ideal_scale": "distributed tracing for AWS services",
                "use_cases": ["latency debugging", "service maps", "trace sampling"],
                "managed_service": True,
            },
            features=["Service map", "annotations", "Lambda/ECS integration"],
            trade_offs={
                "pros": ["Tight AWS integration", "low setup for supported runtimes"],
                "cons": ["Less full-featured than dedicated APM suites"],
            },
            pricing_model="per_trace",
            base_cost_usd=90.0,
            alternatives=[],
            config_examples={},
            docs_url="https://docs.aws.amazon.com/xray/",
        ),
        # ── Expanded GCP catalog ───────────────────────────────────────────────
        Component(
            name="Google Cloud SQL for PostgreSQL",
            category="database",
            vendor="GCP",
            icon_url=_GCP_CSQL,
            selection_criteria={
                "ideal_scale": "managed Postgres/MySQL on GCP",
                "use_cases": ["ACID", "relational apps", "regional HA"],
                "managed_service": True,
            },
            features=["Automated backups", "read replicas", "private IP"],
            trade_offs={
                "pros": ["Simple managed relational", "VPC-native networking"],
                "cons": ["Vertical scaling limits vs self-managed", "GCP coupling"],
            },
            pricing_model="per_hour",
            base_cost_usd=300.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/sql/docs/postgres",
        ),
        Component(
            name="Google AlloyDB for PostgreSQL",
            category="database",
            vendor="GCP",
            icon_url=_GCP_ALLOY,
            selection_criteria={
                "ideal_scale": "high-performance Postgres-compatible workloads",
                "use_cases": ["demanding OLTP", "HTAP-style patterns", "enterprise Postgres"],
                "managed_service": True,
            },
            features=["Columnar engine", "fast failover", "read pools"],
            trade_offs={
                "pros": ["Strong Postgres performance story on GCP"],
                "cons": ["Premium pricing vs Cloud SQL", "GCP-only"],
            },
            pricing_model="per_hour",
            base_cost_usd=520.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/alloydb",
        ),
        Component(
            name="Google Cloud Spanner",
            category="database",
            vendor="GCP",
            icon_url=_GCP_SPANNER,
            selection_criteria={
                "ideal_scale": "globally distributed strongly consistent SQL",
                "use_cases": ["global OLTP", "financial ledger patterns", "multi-region"],
                "managed_service": True,
            },
            features=["TrueTime", "horizontal scale", "99.999% SLA tiers"],
            trade_offs={
                "pros": ["Global consistency", "massive scale-out SQL"],
                "cons": ["Premium cost", "schema/query patterns must fit Spanner"],
            },
            pricing_model="per_node_hour",
            base_cost_usd=1800.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/spanner/docs",
        ),
        Component(
            name="Google BigQuery",
            category="database",
            vendor="GCP",
            icon_url=_GCP_BQ,
            selection_criteria={
                "ideal_scale": "petabyte analytics and warehouse workloads",
                "use_cases": ["BI", "data lake querying", "ML feature prep"],
                "managed_service": True,
            },
            features=["Columnar storage", "BQML", "Omni cross-cloud"],
            trade_offs={
                "pros": ["Serverless scale", "SQL over huge datasets"],
                "cons": ["Query cost without governance", "not OLTP"],
            },
            pricing_model="per_tb",
            base_cost_usd=700.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/bigquery/docs",
        ),
        Component(
            name="Google Firestore",
            category="database",
            vendor="GCP",
            icon_url=_SI_GCP,
            selection_criteria={
                "ideal_scale": "serverless document database for mobile/web",
                "use_cases": ["realtime apps", "user state", "offline-first clients"],
                "managed_service": True,
            },
            features=["Realtime listeners", "multi-region", "TTL policies"],
            trade_offs={
                "pros": ["Low ops", "great client SDKs"],
                "cons": ["Document/query model constraints", "complex transactions vs SQL"],
            },
            pricing_model="per_operation",
            base_cost_usd=120.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/firestore/docs",
        ),
        Component(
            name="Google Cloud Bigtable",
            category="database",
            vendor="GCP",
            icon_url=_SI_GCP,
            selection_criteria={
                "ideal_scale": "wide-column NoSQL at very high throughput",
                "use_cases": ["IoT time-series", "AdTech", "low-latency key access"],
                "managed_service": True,
            },
            features=["HBase API", "cluster scaling", "multi-cluster routing"],
            trade_offs={
                "pros": ["Predictable low latency at scale"],
                "cons": ["Operational modeling required", "not SQL"],
            },
            pricing_model="per_node_hour",
            base_cost_usd=880.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/bigtable/docs",
        ),
        Component(
            name="Google Kubernetes Engine (GKE)",
            category="compute",
            vendor="GCP",
            icon_url=_GCP_GKE,
            selection_criteria={
                "ideal_scale": "Kubernetes production clusters on GCP",
                "use_cases": ["microservices", "service mesh", "GPU node pools"],
                "managed_service": True,
            },
            features=["Autopilot", "Workload Identity", "multi-zonal clusters"],
            trade_offs={
                "pros": ["Mature GKE features", "strong GCP networking integration"],
                "cons": ["Kubernetes complexity", "cost without rightsizing"],
            },
            pricing_model="per_cluster_hour",
            base_cost_usd=720.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/kubernetes-engine/docs",
        ),
        Component(
            name="Google Cloud Run",
            category="compute",
            vendor="GCP",
            icon_url=_GCP_RUN,
            selection_criteria={
                "ideal_scale": "containerized HTTP services with scale-to-zero",
                "use_cases": ["APIs", "webhooks", "batch jobs (Cloud Run jobs)"],
                "managed_service": True,
            },
            features=["Scale to zero", "VPC connectors", "request-based billing"],
            trade_offs={
                "pros": ["Very low ops", "great burst economics"],
                "cons": ["Request timeout limits", "cold start sensitivity for some workloads"],
            },
            pricing_model="per_vcpu_second",
            base_cost_usd=210.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/run/docs",
        ),
        Component(
            name="Google Compute Engine",
            category="compute",
            vendor="GCP",
            icon_url=_GCP_CE,
            selection_criteria={
                "ideal_scale": "VMs with full OS control on GCP",
                "use_cases": ["lift-and-shift", "licensed software", "custom kernels"],
                "managed_service": False,
            },
            features=["Live migration", "Sole-tenant nodes", "preemptible VMs"],
            trade_offs={
                "pros": ["Maximum flexibility", "predictable performance tuning"],
                "cons": ["You manage patching/HA patterns"],
            },
            pricing_model="per_hour",
            base_cost_usd=430.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/compute/docs",
        ),
        Component(
            name="Google Cloud Pub/Sub",
            category="message_queue",
            vendor="GCP",
            icon_url=_SI_GCP,
            selection_criteria={
                "ideal_scale": "durable messaging and event ingestion at global scale",
                "use_cases": ["async pipelines", "log ingestion", "fan-out"],
                "managed_service": True,
            },
            features=["At-least-once delivery", "ordering keys", "schema topics"],
            trade_offs={
                "pros": ["Massive throughput", "simple publisher/subscriber model"],
                "cons": ["Different semantics than Kafka logs for replay patterns"],
            },
            pricing_model="per_gb",
            base_cost_usd=55.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/pubsub/docs",
        ),
        Component(
            name="Google Apigee API Management",
            category="api_gateway",
            vendor="GCP",
            icon_url=_GCP_APIGEE,
            selection_criteria={
                "ideal_scale": "enterprise API lifecycle and monetization",
                "use_cases": ["API products", "rate limits", "developer portal"],
                "managed_service": True,
            },
            features=["Policies", "analytics", "hybrid deployment options"],
            trade_offs={
                "pros": ["Enterprise-grade API program capabilities"],
                "cons": ["Higher cost/complexity vs lightweight gateways"],
            },
            pricing_model="subscription",
            base_cost_usd=1200.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/apigee/docs",
        ),
        Component(
            name="Google Vertex AI (Gemini & models)",
            category="llm_provider",
            vendor="GCP",
            icon_url=_GCP_VERTEX_DIR,
            selection_criteria={
                "ideal_scale": "GCP-native generative AI and model hosting",
                "use_cases": ["Gemini endpoints", "model tuning", "evaluation pipelines"],
                "managed_service": True,
            },
            features=["Model Garden", "VPC-SC", "private endpoints", "MLOps integration"],
            trade_offs={
                "pros": ["Unified AI platform on GCP", "enterprise controls"],
                "cons": ["Best when workloads already on GCP"],
            },
            pricing_model="per_token",
            base_cost_usd=510.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/vertex-ai/docs",
        ),
        Component(
            name="Vertex AI Vector Search",
            category="vector_database",
            vendor="GCP",
            icon_url=_GCP_VERTEX_DIR,
            selection_criteria={
                "ideal_scale": "managed vector retrieval at scale on GCP",
                "use_cases": ["RAG", "recommendations", "similarity search"],
                "managed_service": True,
            },
            features=["Sharding", "hybrid search patterns with ranking"],
            trade_offs={
                "pros": ["Native integration with Vertex AI", "managed scaling"],
                "cons": ["GCP-centric", "pricing tied to index sizing"],
            },
            pricing_model="per_node_hour",
            base_cost_usd=360.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/vertex-ai/docs/vector-search/overview",
        ),
        Component(
            name="Vertex AI Text Embeddings",
            category="embedding_model",
            vendor="GCP",
            icon_url=_GCP_VERTEX_DIR,
            selection_criteria={
                "ideal_scale": "hosted embeddings inside Vertex AI",
                "use_cases": ["RAG ingestion", "semantic search", "classification features"],
                "managed_service": True,
            },
            features=["Batch embedding", "multilingual models", "VPC controls"],
            trade_offs={
                "pros": ["Tight integration with Vertex vector stacks"],
                "cons": ["Compare catalog/pricing vs pure API vendors"],
            },
            pricing_model="per_token",
            base_cost_usd=105.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings",
        ),
        Component(
            name="Google Cloud Memorystore for Redis",
            category="cache",
            vendor="GCP",
            icon_url=_SI_GCP,
            selection_criteria={
                "ideal_scale": "managed Redis/Memcached on GCP",
                "use_cases": ["cache", "session store", "rate limiting"],
                "managed_service": True,
            },
            features=["Standard and cluster tiers", "VPC", "high availability"],
            trade_offs={
                "pros": ["Low ops", "predictable Redis semantics"],
                "cons": ["GCP-only", "memory-bound like any Redis"],
            },
            pricing_model="per_gb_hour",
            base_cost_usd=130.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/memorystore/docs/redis",
        ),
        Component(
            name="Google Cloud Logging & Monitoring",
            category="monitoring",
            vendor="GCP",
            icon_url=_SI_GCP,
            selection_criteria={
                "ideal_scale": "GCP-native observability (metrics/logs/alerts)",
                "use_cases": ["SRE dashboards", "SLO monitoring", "audit logs"],
                "managed_service": True,
            },
            features=["Cloud Monitoring", "Cloud Logging", "Error Reporting", "Uptime checks"],
            trade_offs={
                "pros": ["Deep GCP integration", "IAM-aware access"],
                "cons": ["Cross-cloud requires additional tooling", "cost at high log volume"],
            },
            pricing_model="per_GB",
            base_cost_usd=170.0,
            alternatives=[],
            config_examples={},
            docs_url="https://cloud.google.com/logging/docs",
        ),
        # ── Expanded Azure catalog ─────────────────────────────────────────────
        Component(
            name="Azure SQL Database",
            category="database",
            vendor="Azure",
            icon_url="/icons/Azure/azure-sql.svg",
            selection_criteria={
                "ideal_scale": "managed SQL Server engine on Azure",
                "use_cases": ["OLTP", "T-SQL apps", "elastic pools"],
                "managed_service": True,
            },
            features=["Hyperscale", "geo-replication", "AD auth"],
            trade_offs={
                "pros": ["Strong SQL Server compatibility", "PaaS patching"],
                "cons": ["Azure-centric", "licensing/cost tuning required"],
            },
            pricing_model="per_hour",
            base_cost_usd=340.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/azure-sql/database/",
        ),
        Component(
            name="Azure Cosmos DB",
            category="database",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "multi-model globally distributed database",
                "use_cases": ["NoSQL", "Gremlin/Cassandra APIs", "global apps"],
                "managed_service": True,
            },
            features=["Multi-region writes (optional)", "SLA tiers", "serverless option"],
            trade_offs={
                "pros": ["Global distribution", "flexible APIs"],
                "cons": ["RU/s modeling learning curve", "can get expensive without discipline"],
            },
            pricing_model="per_ru",
            base_cost_usd=600.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/cosmos-db/",
        ),
        Component(
            name="Azure Database for MySQL Flexible Server",
            category="database",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "managed MySQL on Azure",
                "use_cases": ["LAMP stacks", "web apps", "read replicas"],
                "managed_service": True,
            },
            features=["Burstable tiers", "HA zones", "private access"],
            trade_offs={
                "pros": ["Simple managed MySQL", "Azure networking integration"],
                "cons": ["Vertical scaling limits", "Azure coupling"],
            },
            pricing_model="per_hour",
            base_cost_usd=290.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/mysql/",
        ),
        Component(
            name="Azure Synapse Analytics",
            category="database",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "integrated analytics warehouse and Spark/SQL pools",
                "use_cases": ["enterprise DW", "lakehouse patterns on Azure"],
                "managed_service": True,
            },
            features=["Dedicated SQL pool", "Spark pools", "Pipelines"],
            trade_offs={
                "pros": ["Unified analytics workspace in Azure"],
                "cons": ["Complex pricing/components", "steep onboarding"],
            },
            pricing_model="per_dwu",
            base_cost_usd=1100.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/synapse-analytics/",
        ),
        Component(
            name="Azure Databricks",
            category="database",
            vendor="Azure",
            icon_url=_AZ_DB_BRICKS,
            selection_criteria={
                "ideal_scale": "lakehouse analytics and Spark workloads",
                "use_cases": ["ETL", "ML feature engineering", "Delta Lake"],
                "managed_service": True,
            },
            features=["Photon engine", "Unity Catalog", "MLflow"],
            trade_offs={
                "pros": ["Best-in-class Spark UX", "strong governance story"],
                "cons": ["Premium cost", "requires discipline to control cluster spend"],
            },
            pricing_model="per_dbu",
            base_cost_usd=950.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/databricks/",
        ),
        Component(
            name="Azure Kubernetes Service (AKS)",
            category="compute",
            vendor="Azure",
            icon_url=_K8S,
            selection_criteria={
                "ideal_scale": "managed Kubernetes on Azure",
                "use_cases": ["microservices", "service mesh", "GitOps"],
                "managed_service": True,
            },
            features=["Azure AD workload identity", "auto-upgrade channels", "node autoscale"],
            trade_offs={
                "pros": ["Mature AKS roadmap", "Azure networking integration"],
                "cons": ["Kubernetes operational complexity remains"],
            },
            pricing_model="per_cluster_hour",
            base_cost_usd=680.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/aks/",
        ),
        Component(
            name="Azure Container Apps",
            category="compute",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "serverless containers with scale-to-zero",
                "use_cases": ["microservices", "event-driven workers", "internal APIs"],
                "managed_service": True,
            },
            features=["KEDA autoscaling", "Dapr integration", "ingress"],
            trade_offs={
                "pros": ["Low ops vs AKS for many apps", "consumption pricing"],
                "cons": ["Less flexible than raw Kubernetes for exotic needs"],
            },
            pricing_model="per_vcpu_second",
            base_cost_usd=230.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/container-apps/",
        ),
        Component(
            name="Azure Functions",
            category="compute",
            vendor="Azure",
            icon_url=_SI_AZ_FN,
            selection_criteria={
                "ideal_scale": "event-driven functions and lightweight APIs",
                "use_cases": ["integrations", "webhooks", "scheduled jobs"],
                "managed_service": True,
            },
            features=["Durable Functions", "managed identities", "VNet integration"],
            trade_offs={
                "pros": ["Fast development", "elastic scale"],
                "cons": ["Cold starts", "timeouts/limits vs always-on VMs"],
            },
            pricing_model="per_execution",
            base_cost_usd=160.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/",
        ),
        Component(
            name="Azure Virtual Machines",
            category="compute",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "IaaS VMs with full control",
                "use_cases": ["lift-and-shift", "custom software", "GPU workloads"],
                "managed_service": False,
            },
            features=["Availability Sets/Zones", "Spot VMs", "disk options"],
            trade_offs={
                "pros": ["Maximum control", "broad SKU catalog"],
                "cons": ["Patching/HA is your responsibility unless automated"],
            },
            pricing_model="per_hour",
            base_cost_usd=480.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/virtual-machines/",
        ),
        Component(
            name="Azure Service Bus",
            category="message_queue",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "enterprise messaging (queues and topics)",
                "use_cases": ["reliable async processing", "pub/sub", "ordered workflows"],
                "managed_service": True,
            },
            features=["Sessions", "dead-lettering", "duplicate detection"],
            trade_offs={
                "pros": ["Strong enterprise messaging semantics"],
                "cons": ["Different model than Kafka for log-style replay"],
            },
            pricing_model="per_million_operations",
            base_cost_usd=85.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/service-bus-messaging/",
        ),
        Component(
            name="Azure Event Grid",
            category="message_queue",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "event routing for Azure resources and custom topics",
                "use_cases": ["reactive automation", "fan-out", "SaaS partner topics"],
                "managed_service": True,
            },
            features=["CloudEvents", "filters", "delivery retries"],
            trade_offs={
                "pros": ["Great Azure-native integration", "low ops"],
                "cons": ["Not a durable infinite log like Kafka by default"],
            },
            pricing_model="per_million_operations",
            base_cost_usd=40.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/event-grid/",
        ),
        Component(
            name="Azure Storage Queues",
            category="message_queue",
            vendor="Azure",
            icon_url=_AZ_QUEUE,
            selection_criteria={
                "ideal_scale": "simple durable queues backed by Azure Storage",
                "use_cases": ["task queues", "decoupling workers", "cheap buffering"],
                "managed_service": True,
            },
            features=["Long polling", "visibility timeout", "large messages via blob pattern"],
            trade_offs={
                "pros": ["Very low cost", "simple model"],
                "cons": ["Fewer features than Service Bus for enterprise patterns"],
            },
            pricing_model="per_operation",
            base_cost_usd=12.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/storage/queues/",
        ),
        Component(
            name="Azure Application Gateway",
            category="api_gateway",
            vendor="Azure",
            icon_url=_SI_AZURE,
            selection_criteria={
                "ideal_scale": "L7 load balancing and WAF in front of apps",
                "use_cases": ["path routing", "TLS termination", "WAF rules"],
                "managed_service": True,
            },
            features=["WAF policy", "autoscaling", "URL-based routing"],
            trade_offs={
                "pros": ["Native Azure integration", "strong WAF story"],
                "cons": ["Not a full API developer portal like APIM"],
            },
            pricing_model="per_hour",
            base_cost_usd=210.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/application-gateway/",
        ),
        Component(
            name="Azure Log Analytics",
            category="monitoring",
            vendor="Azure",
            icon_url=_AZ_LOG,
            selection_criteria={
                "ideal_scale": "centralized logs and queries across Azure resources",
                "use_cases": ["KQL queries", "security investigations", "audit trails"],
                "managed_service": True,
            },
            features=["KQL", "workspace retention policies", "cross-resource queries"],
            trade_offs={
                "pros": ["Deep Azure integration", "powerful query language"],
                "cons": ["Ingestion costs at scale", "requires governance"],
            },
            pricing_model="per_GB",
            base_cost_usd=150.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/azure-monitor/logs/",
        ),
        Component(
            name="Azure Machine Learning",
            category="llm_provider",
            vendor="Azure",
            icon_url=_AZ_ML,
            selection_criteria={
                "ideal_scale": "Azure ML platform for training and online endpoints",
                "use_cases": ["custom models", "MLOps", "managed online inference"],
                "managed_service": True,
            },
            features=["Endpoints", "pipelines", "responsible AI tooling"],
            trade_offs={
                "pros": ["Enterprise governance on Azure", "integrated with Azure AD"],
                "cons": ["More setup than pure API vendors for simple LLM chat"],
            },
            pricing_model="per_hour",
            base_cost_usd=560.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/machine-learning/",
        ),
        Component(
            name="Azure AI Search",
            category="vector_database",
            vendor="Azure",
            icon_url=_AZ_SEARCH,
            selection_criteria={
                "ideal_scale": "managed search with vector + semantic ranking",
                "use_cases": ["RAG", "enterprise search", "hybrid retrieval"],
                "managed_service": True,
            },
            features=["vector fields", "semantic ranker", "skillsets"],
            trade_offs={
                "pros": ["Strong hybrid search story in Azure", "private networking options"],
                "cons": ["Pricing tied to replicas/SKU", "tuning needed for best relevance"],
            },
            pricing_model="per_search_unit",
            base_cost_usd=380.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/search/",
        ),
        Component(
            name="Azure OpenAI Embeddings",
            category="embedding_model",
            vendor="Azure",
            icon_url=_AZ_OAI,
            selection_criteria={
                "ideal_scale": "OpenAI embedding models on private Azure endpoints",
                "use_cases": ["RAG ingestion", "semantic search features"],
                "managed_service": True,
            },
            features=["Private networking", "Azure AD auth", "quota controls"],
            trade_offs={
                "pros": ["Enterprise controls", "consistent with Azure OpenAI chat deployments"],
                "cons": ["Model availability follows Azure OpenAI catalog"],
            },
            pricing_model="per_token",
            base_cost_usd=115.0,
            alternatives=[],
            config_examples={},
            docs_url="https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/embeddings",
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
