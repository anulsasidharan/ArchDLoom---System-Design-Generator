"""Monitoring & observability plan generator.

Builds an `ObservabilityPlan` covering the four pillars (metrics, logs, traces,
events / synthetic + RUM), SLO targets, paging policy, and dashboard outlines.
The plan is consumed by HLD docx and the architecture markdown shared template.
"""

from __future__ import annotations

from app.domain.components import ArchitecturePattern, ComponentSelectionResult
from app.domain.enterprise import ObservabilityPillar, ObservabilityPlan
from app.domain.requirements import ParsedRequirement


def _slo_targets(req: ParsedRequirement) -> list[str]:
    nfr = req.non_functional_requirements
    targets: list[str] = []
    if nfr.latency_target:
        targets.append(f"Latency SLO: {nfr.latency_target} (track p50/p95/p99 separately).")
    else:
        targets.append("Latency SLO: define p95 / p99 budgets per critical journey.")
    if nfr.availability_target:
        targets.append(f"Availability SLO: {nfr.availability_target} (rolling 28-day window).")
    else:
        targets.append("Availability SLO: align rolling 28-day target with product expectations.")
    if nfr.throughput_target:
        targets.append(f"Throughput target: {nfr.throughput_target}.")
    targets.append("Error budget consumed beyond 50% triggers reliability investment freeze on new features.")
    return targets


def _ai_pillar_alerts(pattern: ArchitecturePattern) -> list[str]:
    if pattern == ArchitecturePattern.RAG_SYSTEM:
        return [
            "Retrieval miss-rate spike (>2× 7-day baseline) for 10 min.",
            "Grounded-answer share <80% for 15 min.",
            "Vector index freshness lag >1h.",
        ]
    if pattern == ArchitecturePattern.REALTIME_INFERENCE:
        return [
            "p95 token latency >SLO for 5 min.",
            "Provider 5xx ratio >1% for 5 min.",
            "Cost per request 90th percentile >2× rolling baseline.",
        ]
    if pattern == ArchitecturePattern.AGENTIC_AI_SYSTEM:
        return [
            "Tool-call failure rate >5% for 10 min.",
            "Average steps per task >2× rolling baseline (looping risk).",
            "Per-task cost ceiling exceeded.",
        ]
    if pattern == ArchitecturePattern.FINE_TUNING_PIPELINE:
        return [
            "Training job failure rate >3 in 24h.",
            "GPU utilization <40% on running jobs (waste alarm).",
            "Eval regression vs prior checkpoint on guardrail metrics.",
        ]
    return []


def build_observability_plan(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
) -> ObservabilityPlan:
    pattern = components.architecture_pattern
    pillars: list[ObservabilityPillar] = [
        ObservabilityPillar(
            name="Metrics (RED + USE)",
            purpose="Quantify request rate, errors, duration; resource utilization, saturation, errors per node.",
            instruments=[
                "Service-level RED metrics emitted from every HTTP/gRPC handler.",
                "USE metrics on hosts, pods, message brokers, and database engines.",
                "Business KPIs (signups, conversions, retention) emitted alongside system metrics.",
            ],
            alerts=[
                "Multi-window multi-burn-rate SLO alerting (fast 5m / slow 1h windows).",
                "Saturation alerts on CPU / memory / connection pools at 80% sustained.",
            ],
        ),
        ObservabilityPillar(
            name="Logs",
            purpose="Structured, searchable record of authoritative events for debugging and audit.",
            instruments=[
                "JSON logs with trace / span / request IDs and tenant identifier.",
                "PII / PHI redaction at the logger; deny-list verified in CI.",
                "Centralized aggregation with tiered hot/warm/cold retention.",
            ],
            alerts=[
                "Anomaly detection on error log volume per service.",
                "Specific log patterns for security signals (auth failures, 4xx surges).",
            ],
        ),
        ObservabilityPillar(
            name="Traces",
            purpose="Cross-service causality and latency attribution.",
            instruments=[
                "OpenTelemetry SDK in every service; W3C Trace-Context propagation end-to-end.",
                "Tail-based or head-based sampling with explicit budget; always-sample on errors.",
                "Span attributes for tenant, route, dependency, and cache outcome.",
            ],
            alerts=[
                "Critical path p99 latency regression vs 7-day baseline.",
                "New downstream dependency detected (drift alarm).",
            ],
        ),
        ObservabilityPillar(
            name="Synthetics & RUM",
            purpose="Outside-in availability and real-user performance signal.",
            instruments=[
                "Synthetic checks from ≥3 geographies covering top 5 user journeys.",
                "Real-user monitoring (RUM) for web/mobile entry points.",
                "Black-box probes hitting critical APIs (incl. auth-protected paths).",
            ],
            alerts=[
                "Multi-region synthetic failure for >2 minutes.",
                "RUM core web vitals regression on a release candidate.",
            ],
        ),
    ]

    if requirements.has_ai_features or pattern in {
        ArchitecturePattern.RAG_SYSTEM,
        ArchitecturePattern.REALTIME_INFERENCE,
        ArchitecturePattern.AGENTIC_AI_SYSTEM,
        ArchitecturePattern.FINE_TUNING_PIPELINE,
    }:
        pillars.append(
            ObservabilityPillar(
                name="AI/ML telemetry",
                purpose="Quality, safety, cost, and drift signals specific to model-backed flows.",
                instruments=[
                    "Per-call: prompt template id, model id, token in/out counts, latency, cost.",
                    "Quality eval hooks (groundedness, answer relevance, refusal rate) on a sample.",
                    "Drift monitors on input distribution and retrieval relevance.",
                ],
                alerts=_ai_pillar_alerts(pattern),
            )
        )

    paging: list[str] = [
        "PagerDuty / Opsgenie rotation aligned to service ownership; primary + secondary engineer.",
        "Severity matrix (SEV1..SEV4) with response-time and update-cadence commitments.",
        "Auto-escalation to incident commander on SEV1 if not acknowledged within 5 minutes.",
        "Quiet hours / follow-the-sun for distributed teams; no overnight paging for SEV3+.",
    ]

    dashboards: list[str] = [
        "Service-level dashboard per bounded context (RED + dependencies).",
        "SLO burn-rate dashboard with error budget remaining.",
        "Capacity dashboard (CPU / memory / connection pools / queue depth).",
        "Incident-response dashboard for live war rooms.",
    ]
    if requirements.has_ai_features:
        dashboards.append("AI quality / cost dashboard (token usage, eval scores, drift).")

    return ObservabilityPlan(
        pillars=pillars,
        slo_targets=_slo_targets(requirements),
        paging=paging,
        dashboards=dashboards,
        log_retention="Hot 30d / warm 90d / cold 1y; security events in immutable storage 1y+.",
        trace_sampling="Adaptive sampling targeting 1–5% of healthy traffic; 100% of errors and slow spans.",
    )
