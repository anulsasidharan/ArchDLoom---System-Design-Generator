"""Cost estimation engine.

Translates `ComponentSelectionResult` baseline costs and `ScaleMetrics` signals into
a category-level monthly breakdown plus MVP/Growth/Enterprise phase projections.

The engine is intentionally heuristic — values are anchors for review meetings, not
billing predictions. It accounts for:
  * Pricing model family (per_hour, per_request, per_token, per_GB, ...).
  * Daily active users / peak RPS scaling.
  * Data volume scaling for storage-heavy categories.
  * AI/ML categories (LLM/embedding) when token-priced and traffic is known.
"""

from __future__ import annotations

import math

from app.domain.components import ComponentSelectionResult
from app.domain.enterprise import CostEstimate, CostLineItem, CostPhaseProjection
from app.domain.requirements import ParsedRequirement

_TRAFFIC_SENSITIVE = {
    "api_gateway",
    "compute",
    "cache",
    "monitoring",
    "vector_database",
    "llm_provider",
    "embedding_model",
    "message_queue",
}
_STORAGE_SENSITIVE = {"database", "vector_database"}

_DEFAULT_BASELINE_BY_CATEGORY: dict[str, float] = {
    "api_gateway": 80.0,
    "compute": 250.0,
    "database": 350.0,
    "cache": 90.0,
    "monitoring": 120.0,
    "message_queue": 90.0,
    "vector_database": 200.0,
    "llm_provider": 600.0,
    "embedding_model": 150.0,
}

_PHASE_FACTORS: dict[str, float] = {
    "MVP": 0.30,
    "Growth": 0.65,
    "Enterprise": 1.00,
}

_PHASE_NOTES: dict[str, str] = {
    "MVP": "Single-region managed services; defer redundancy and reserved capacity.",
    "Growth": "Add multi-AZ, autoscaling, and dedicated observability; introduce reserved/committed-use savings.",
    "Enterprise": "Full redundancy, DR, security tooling, and FinOps governance.",
}


def _scale_multiplier(req: ParsedRequirement, category: str) -> tuple[float, str]:
    """Return (multiplier, note) used to inflate baseline cost for the category."""
    sm = req.scale_metrics
    base = 1.0
    notes: list[str] = []

    if category in _TRAFFIC_SENSITIVE:
        if sm.peak_requests_per_second is not None:
            rps = float(sm.peak_requests_per_second)
            traffic_mult = 1.0 + math.log10(max(rps, 1.0) + 1.0) * 0.45
            base *= traffic_mult
            notes.append(f"peak_rps≈{rps:g}")
        elif sm.daily_active_users is not None:
            dau = float(sm.daily_active_users)
            traffic_mult = 1.0 + math.log10(max(dau, 1.0) + 1.0) * 0.30
            base *= traffic_mult
            notes.append(f"DAU≈{int(dau):,}")

    if category in _STORAGE_SENSITIVE and sm.data_volume_gb is not None:
        gb = float(sm.data_volume_gb)
        storage_mult = 1.0 + math.log10(max(gb, 1.0) + 1.0) * 0.55
        base *= storage_mult
        notes.append(f"data≈{gb:g} GB")

    if category in {"llm_provider", "embedding_model"} and req.has_ai_features:
        base *= 1.15
        notes.append("AI workloads in scope")

    base = max(0.5, min(base, 25.0))
    return base, ("; ".join(notes) if notes else "baseline scale")


def _baseline_for(category: str, baseline_cost: float | None) -> float:
    if baseline_cost is not None and baseline_cost > 0:
        return float(baseline_cost)
    return _DEFAULT_BASELINE_BY_CATEGORY.get(category, 100.0)


def estimate_costs(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
) -> CostEstimate:
    """Compute scale-adjusted line items, aggregate, and phase projections."""
    line_items: list[CostLineItem] = []
    aggregate = 0.0

    for cat in sorted(components.selections.keys()):
        decision = components.selections[cat]
        baseline = _baseline_for(cat, decision.estimated_monthly_cost_usd)
        mult, note = _scale_multiplier(requirements, cat)
        adjusted = round(baseline * mult, 2)
        aggregate += adjusted
        line_items.append(
            CostLineItem(
                category=cat,
                component=decision.selected.name,
                pricing_model=None,
                base_cost_usd=round(baseline, 2),
                scale_multiplier=round(mult, 3),
                estimated_monthly_cost_usd=adjusted,
                notes=note,
            )
        )

    aggregate = round(aggregate, 2)

    phases = [
        CostPhaseProjection(
            name=name,
            monthly_cost_usd=round(aggregate * factor, 2),
            notes=_PHASE_NOTES.get(name, ""),
        )
        for name, factor in _PHASE_FACTORS.items()
    ]

    assumptions: list[str] = [
        "Baselines come from the seeded component library or category defaults.",
        "Scale multipliers blend logarithmic traffic and data-volume signals; no real-time pricing is queried.",
        "Phase projections use 30% / 65% / 100% of the target architecture footprint as planning anchors.",
    ]
    if requirements.has_ai_features:
        assumptions.append(
            "AI/ML workloads include a small premium to reflect token / GPU consumption variance."
        )
    if requirements.scale_metrics.peak_requests_per_second is None and requirements.scale_metrics.daily_active_users is None:
        assumptions.append(
            "Traffic signals were not provided — review estimates after capturing DAU or peak RPS."
        )

    return CostEstimate(
        pattern=components.architecture_pattern.value,
        line_items=line_items,
        aggregate_monthly_usd=aggregate,
        phases=phases,
        assumptions=assumptions,
    )
