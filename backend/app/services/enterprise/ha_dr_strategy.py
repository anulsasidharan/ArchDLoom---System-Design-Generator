"""High-availability and disaster-recovery strategy generator.

Translates RTO/RPO/availability targets into a recommended posture (single-AZ,
multi-AZ, multi-region active-passive, multi-region active-active) and emits
operational recommendations, backup cadence, drill schedule, and a failover
runbook outline.
"""

from __future__ import annotations

import re

from app.domain.components import ArchitecturePattern, ComponentSelectionResult
from app.domain.enterprise import HADRStrategy
from app.domain.requirements import ParsedRequirement


def _parse_minutes(value: str | None) -> float | None:
    """Best-effort parse of strings like '5 min', '2h', '15 minutes', '0.5 hour'."""
    if not value:
        return None
    s = value.strip().lower().replace(",", ".")
    m = re.search(r"([\d\.]+)\s*(ms|s|sec|second|seconds|m|min|minutes|h|hr|hour|hours|d|day|days)?", s)
    if not m:
        return None
    try:
        n = float(m.group(1))
    except ValueError:
        return None
    unit = (m.group(2) or "min").strip()
    if unit in {"ms"}:
        return n / 60_000.0
    if unit in {"s", "sec", "second", "seconds"}:
        return n / 60.0
    if unit in {"m", "min", "minutes"}:
        return n
    if unit in {"h", "hr", "hour", "hours"}:
        return n * 60.0
    if unit in {"d", "day", "days"}:
        return n * 60.0 * 24.0
    return n


def _availability_nines(value: str | None) -> float | None:
    """Return the count of nines from strings like '99.99%' -> 4.0."""
    if not value:
        return None
    m = re.search(r"99(?:\.(9+))?", value)
    if not m:
        return None
    decimals = m.group(1) or ""
    return 2.0 + len(decimals)


def _decide_posture(
    nines: float | None,
    rto_min: float | None,
    rpo_min: float | None,
) -> tuple[str, str]:
    """Return (posture_code, rationale) tuple."""
    score = 0
    why: list[str] = []

    if nines is not None:
        if nines >= 5:
            score += 3
            why.append(f"availability target ≥99.999% ({nines:g} nines)")
        elif nines >= 4:
            score += 2
            why.append(f"availability target ≥99.99% ({nines:g} nines)")
        elif nines >= 3:
            score += 1
            why.append(f"availability target ≥99.9% ({nines:g} nines)")

    if rto_min is not None:
        if rto_min <= 5:
            score += 3
            why.append(f"RTO ≤5 minutes ({rto_min:g} min)")
        elif rto_min <= 30:
            score += 2
            why.append(f"RTO ≤30 minutes ({rto_min:g} min)")
        elif rto_min <= 60:
            score += 1
            why.append(f"RTO ≤1 hour ({rto_min:g} min)")

    if rpo_min is not None:
        if rpo_min <= 1:
            score += 3
            why.append(f"RPO near-zero ({rpo_min:g} min)")
        elif rpo_min <= 15:
            score += 2
            why.append(f"RPO ≤15 minutes ({rpo_min:g} min)")
        elif rpo_min <= 60:
            score += 1
            why.append(f"RPO ≤1 hour ({rpo_min:g} min)")

    if score >= 6:
        return ("multi-region-active-active", "; ".join(why) or "aggressive RTO/RPO and availability targets")
    if score >= 3:
        return ("multi-region-active-passive", "; ".join(why) or "stricter availability/RTO than single-region")
    if score >= 1:
        return ("multi-az", "; ".join(why) or "single-region multi-AZ meets stated targets")
    return ("multi-az", "default safe posture absent stated targets")


def _backups_for(posture: str) -> list[str]:
    base = [
        "Automated daily snapshots with point-in-time recovery (PITR) where the engine supports it.",
        "Cross-region snapshot replication for production-critical datasets.",
        "Quarterly restore drills with timing captured against documented RTO.",
        "Backup encryption with managed keys; backup access logged separately from production.",
    ]
    if posture in {"multi-region-active-passive", "multi-region-active-active"}:
        base.append("Asynchronous logical or physical replication to a warm standby region.")
    if posture == "multi-region-active-active":
        base.append("Conflict-resolution strategy documented per dataset (LWW, vector clocks, CRDT, or app-level).")
    return base


def _recommendations_for(
    posture: str,
    pattern: ArchitecturePattern,
    components: ComponentSelectionResult,
) -> list[str]:
    recs: list[str] = []
    if posture == "multi-az":
        recs.extend(
            [
                "Deploy stateless tiers across ≥2 AZs behind an L7 load balancer with health checks.",
                "Use multi-AZ managed databases (e.g. RDS Multi-AZ, Aurora) with automated failover.",
                "Cache and message tiers also span AZs with replicated state.",
            ]
        )
    if posture == "multi-region-active-passive":
        recs.extend(
            [
                "Maintain a warm standby region with infrastructure as code parity and weekly smoke tests.",
                "Replicate stateful data asynchronously; document RPO drift alarms.",
                "Use global DNS / Anycast routing with health-checked failover.",
                "Pre-stage operator runbooks and access in the standby region.",
            ]
        )
    if posture == "multi-region-active-active":
        recs.extend(
            [
                "Active-active routing via geo-aware load balancing; pin per-tenant primaries to limit conflict surface.",
                "Globally distributed datastore (or per-region partitions with reconciliation) for write paths.",
                "Region-level circuit breakers and traffic-shifting controls (e.g. weighted records, feature flags).",
                "Continuous chaos / failover game days at least quarterly.",
            ]
        )

    if pattern in {
        ArchitecturePattern.RAG_SYSTEM,
        ArchitecturePattern.AGENTIC_AI_SYSTEM,
        ArchitecturePattern.REALTIME_INFERENCE,
    }:
        recs.append(
            "External LLM/vector service dependencies: configure provider failover, request-level timeouts, "
            "and graceful-degradation responses when the provider is degraded."
        )
    if pattern == ArchitecturePattern.FINE_TUNING_PIPELINE:
        recs.append(
            "Training jobs are batch — checkpoint to durable storage frequently and resume on alternate fleet on failure."
        )
    if "message_queue" in components.selections:
        recs.append(
            "Message broker: durable publishing, idempotent consumers, and dead-letter routing tied to alerting."
        )
    return recs


def _drills_for(posture: str) -> list[str]:
    drills = [
        "Monthly: backup restore for one production dataset, time captured.",
        "Quarterly: AZ-level failure simulation (terminate primary instance group).",
        "Annually: full DR exercise with executive scorecard.",
    ]
    if posture in {"multi-region-active-passive", "multi-region-active-active"}:
        drills.append("Quarterly: regional failover drill with traffic shift and rollback.")
    return drills


def _runbook_for(posture: str) -> list[str]:
    runbook: list[str] = [
        "Detect: alerts on availability SLO burn-rate (fast + slow burn windows).",
        "Decide: incident commander confirms scope; declare disaster if RTO at risk.",
        "Communicate: status page update + stakeholder broadcast within first 15 minutes.",
        "Execute failover: follow per-tier checklist (DNS / load balancer / data plane).",
        "Verify: synthetic monitors + smoke tests green for 15 minutes before declaring recovered.",
        "Postmortem: blameless review within 5 business days with remediation owners.",
    ]
    if posture == "multi-region-active-passive":
        runbook.insert(
            3,
            "Cut traffic via global DNS / Anycast policy; promote replica to primary in standby region.",
        )
    if posture == "multi-region-active-active":
        runbook.insert(
            3,
            "Drain affected region using weighted routing; reconcile replication lag before final cutover.",
        )
    return runbook


def build_hadr_strategy(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
) -> HADRStrategy:
    nfr = requirements.non_functional_requirements
    nines = _availability_nines(nfr.availability_target)
    rto_min = _parse_minutes(nfr.rto)
    rpo_min = _parse_minutes(nfr.rpo)
    posture, rationale = _decide_posture(nines, rto_min, rpo_min)

    return HADRStrategy(
        availability_target=nfr.availability_target or "Not specified — align with product SLO workshops.",
        rto=nfr.rto or "Not specified",
        rpo=nfr.rpo or "Not specified",
        posture=posture,
        posture_rationale=rationale,
        recommendations=_recommendations_for(posture, components.architecture_pattern, components),
        backup_strategy=_backups_for(posture),
        drills=_drills_for(posture),
        failover_runbook=_runbook_for(posture),
    )
