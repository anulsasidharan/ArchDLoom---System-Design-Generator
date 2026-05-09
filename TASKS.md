# ArchDLoom — phased tasks & branches

Derived from `CLAUDE.md` (Development Workflow). Subtasks are ordered so each branch merges into `main` with **few cross-branch file conflicts**: earlier rows in a phase are foundations; merge top-to-bottom unless noted.

**Suggested merge discipline:** merge Phase *N* before starting Phase *N+1*. Within a phase, merge in task order (`P*-1` → `P*-n`) unless two tasks explicitly touch disjoint areas (still safer to serialize).

---

## Phase 1 — Foundation & Repository Setup

| Task | Branch | Status |
| --- | --- | --- |
| P1-1 · Monorepo layout, tooling, README | feature/p1-monorepo-scaffold | ✅ done |
| P1-2 · Docker Compose (API, Postgres, Redis) | feature/p1-docker-compose | ✅ done |
| P1-3 · Database schema migrations (Alembic) | feature/p1-db-migrations | ✅ done |
| P1-4 · FastAPI shell, settings, `/health`, OpenAPI | feature/p1-fastapi-bootstrap | ✅ done |
| P1-5 · Next.js 14 app shell, Tailwind, shadcn base | feature/p1-nextjs-bootstrap | ✅ done |
| P1-6 · Secrets/config pattern + Claude env documentation | feature/p1-config-claude-env | ✅ done |
| P1-7 · GitHub Actions CI (backend + frontend) | feature/p1-github-actions-ci | ✅ done |

---

## Phase 2 — Core Generation Engine

| Task | Branch | Status |
| --- | --- | --- |
| P2-1 · Shared domain models & SQLAlchemy foundations | feature/p2-domain-orm-base | ✅ done |
| P2-2 · Claude API client wrapper & errors | feature/p2-claude-client | ✅ done |
| P2-3 · Requirement parser service + Pydantic I/O | feature/p2-requirement-parser | ✅ done |
| P2-4 · Component table + repository + seed script | feature/p2-component-library-data | ✅ done |
| P2-5 · Component selector + rationale/trade-offs | feature/p2-component-selector | ✅ done |
| P2-6 · PRD-only document generator (python-docx) | feature/p2-prd-generator | ✅ done |
| P2-7 · Basic Mermaid diagram code generator | feature/p2-mermaid-basic | ✅ done |
| P2-8 · Celery worker + generation job API + status polling | feature/p2-async-jobs-api | ✅ done |

---

## Phase 3 — Full Document Suite & Packaging

| Task | Branch | Status |
| --- | --- | --- |
| P3-1 · Jinja2 templates layer (shared text blocks) | feature/p3-jinja-templates | ✅ done |
| P3-2 · HLD Word generator | feature/p3-hld-generator | ✅ done |
| P3-3 · LLD Word generator | feature/p3-lld-generator | ✅ done |
| P3-4 · Evolution markdown generator | feature/p3-evolution-generator | ✅ done |
| P3-5 · Pipeline: `architecture.md` + five-artifact orchestration | feature/p3-architecture-md-pipeline | ✅ done |
| P3-6 · Diagram embedding in Word (PNG/SVG bridge) | feature/p3-diagram-docx-embed | ✅ done |
| P3-7 · ZIP bundle + download route | feature/p3-zip-download | ✅ done |

---

## Phase 4 — Diagram Enhancement With Real Icons

| Task | Branch | Status |
| --- | --- | --- |
| P4-1 · Icon asset pipeline & storage (local/S3 stubs) | feature/p4-icon-assets-storage | ⬜ todo |
| P4-2 · SVG overlay engine (parse Mermaid SVG, inject groups) | feature/p4-svg-overlay-engine | ⬜ todo |
| P4-3 · Icon positioning & scaling algorithm | feature/p4-icon-layout | ⬜ todo |
| P4-4 · Diagram annotations (cost, SLA hooks) | feature/p4-diagram-annotations | ⬜ todo |
| P4-5 · Frontend diagram viewer (Mermaid / SVG preview) | feature/p4-diagram-viewer | ⬜ todo |
| P4-6 · Component detail panel (trade-offs, alternatives) | feature/p4-component-detail-panel | ⬜ todo |

---

## Phase 5 — AI/ML Specialization

| Task | Branch | Status |
| --- | --- | --- |
| P5-1 · RAG architecture template | feature/p5-template-rag | ⬜ todo |
| P5-2 · Fine-tuning pipeline template | feature/p5-template-finetuning | ⬜ todo |
| P5-3 · Real-time inference template | feature/p5-template-inference | ⬜ todo |
| P5-4 · Agentic AI system template | feature/p5-template-agents | ⬜ todo |
| P5-5 · Seed AI/ML components (vector DB, LLM, embeddings) | feature/p5-aiml-component-seed | ⬜ todo |
| P5-6 · AI-specific Mermaid/diagram patterns | feature/p5-aiml-diagram-patterns | ⬜ todo |

---

## Phase 6 — Enterprise Features

| Task | Branch | Status |
| --- | --- | --- |
| P6-1 · Cost estimation engine | feature/p6-cost-estimation | ⬜ todo |
| P6-2 · Compliance mapping (GDPR, HIPAA, SOC 2) | feature/p6-compliance-mapping | ⬜ todo |
| P6-3 · Network architecture diagrams | feature/p6-network-diagrams | ⬜ todo |
| P6-4 · Security architecture document sections | feature/p6-security-sections | ⬜ todo |
| P6-5 · HA/DR strategy generation | feature/p6-ha-dr-generation | ⬜ todo |
| P6-6 · Monitoring / observability sections | feature/p6-observability-sections | ⬜ todo |

---

## Phase 7 — Frontend Polish & UX

| Task | Branch | Status |
| --- | --- | --- |
| P7-1 · Landing page | feature/p7-landing-page | ⬜ todo |
| P7-2 · Generation progress & job UX | feature/p7-generation-progress | ⬜ todo |
| P7-3 · Document preview components | feature/p7-document-preview | ⬜ todo |
| P7-4 · Download & ZIP UX | feature/p7-download-ux | ⬜ todo |
| P7-5 · Project management (save/load) | feature/p7-projects-crud-ui | ⬜ todo |
| P7-6 · Component library browser | feature/p7-component-browser | ⬜ todo |

---

## Phase 8 — Testing, Deployment & Hardening

| Task | Branch | Status |
| --- | --- | --- |
| P8-1 · Integration tests (generation pipeline E2E) | feature/p8-integration-tests | ⬜ todo |
| P8-2 · Load / concurrency testing for jobs | feature/p8-load-testing | ⬜ todo |
| P8-3 · Document quality checks / regression fixtures | feature/p8-doc-quality-gates | ⬜ todo |
| P8-4 · Staging deployment (Vercel + backend host) | feature/p8-staging-deploy | ⬜ todo |
| P8-5 · Observability prod wiring (Sentry, CloudWatch) | feature/p8-production-monitoring | ⬜ todo |
| P8-6 · Performance optimization pass | feature/p8-perf-tuning | ⬜ todo |

---

## Phase 9 — Beta Launch & Iteration

| Task | Branch | Status |
| --- | --- | --- |
| P9-1 · Limited beta rollout (access flags, quotas) | feature/p9-beta-rollout | ⬜ todo |
| P9-2 · Feedback capture (in-app / analytics) | feature/p9-feedback-loop | ⬜ todo |
| P9-3 · Component selection tuning from feedback | feature/p9-selector-iteration | ⬜ todo |
| P9-4 · Requested templates & library updates | feature/p9-new-templates | ⬜ todo |
| P9-5 · Generation latency improvements | feature/p9-speed-optimization | ⬜ todo |
| P9-6 · Public launch checklist & polish | feature/p9-public-launch-prep | ⬜ todo |
