#!/usr/bin/env python3
"""Seed the component library (idempotent by component name)."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy.exc import OperationalError, ProgrammingError

# Allow running as `python scripts/seed_components.py` from backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.models.component import Component  # noqa: E402
from app.repositories.component_repository import ComponentRepository  # noqa: E402


def _rows() -> list[Component]:
    return [
        Component(
            name="Amazon RDS for PostgreSQL",
            category="database",
            vendor="AWS",
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
        Component(
            name="Amazon ElastiCache for Redis",
            category="cache",
            vendor="AWS",
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
        Component(
            name="Amazon API Gateway",
            category="api_gateway",
            vendor="AWS",
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
        Component(
            name="AWS Fargate on ECS",
            category="compute",
            vendor="AWS",
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
        Component(
            name="Datadog",
            category="monitoring",
            vendor="Datadog",
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
        Component(
            name="Amazon MSK (Kafka)",
            category="message_queue",
            vendor="AWS",
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
        Component(
            name="OpenAI GPT API",
            category="llm_provider",
            vendor="OpenAI",
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
            name="Pinecone",
            category="vector_database",
            vendor="Pinecone",
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
            name="OpenAI text-embedding-3-large",
            category="embedding_model",
            vendor="OpenAI",
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
            name="Weaviate Cloud",
            category="vector_database",
            vendor="Weaviate",
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
        Component(
            name="AWS Bedrock (managed LLMs)",
            category="llm_provider",
            vendor="AWS",
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
        Component(
            name="Cohere Embed (v3)",
            category="embedding_model",
            vendor="Cohere",
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
    ]


def main() -> None:
    session = SessionLocal()
    repo = ComponentRepository(session)
    try:
        added = 0
        for row in _rows():
            if repo.find_by_name(row.name):
                continue
            session.add(row)
            added += 1
        session.commit()
        print(f"Seed complete ({added} inserted).")
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
            "Cannot reach PostgreSQL (connection refused or host unreachable).\n"
            "  Ensure DATABASE_URL matches a running server (env var or backend/.env).\n"
            "Fix:\n"
            "  1) Start Postgres — from repo root:  docker compose up -d db\n"
            "  2) Wait until it is healthy, then set DATABASE_URL if needed, e.g.\n"
            "     PowerShell: $env:DATABASE_URL='postgresql://archdloom:archdloom@127.0.0.1:5432/archdloom'\n"
            "  3) Run migrations:  docker compose exec api alembic upgrade head\n"
            "     (or alembic upgrade head from backend/ with the same DATABASE_URL)\n"
            "  4) Run this seed script again.\n"
            "On Windows, prefer 127.0.0.1 over localhost if you see IPv6 (::1) issues.",
            file=sys.stderr,
        )
        raise SystemExit(1) from e
    finally:
        session.close()


if __name__ == "__main__":
    main()
