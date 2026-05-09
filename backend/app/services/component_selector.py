"""Score components from the library and produce rationale via Claude."""

from __future__ import annotations

import logging
import re

from sqlalchemy.orm import Session

from app.domain.components import (
    ArchitecturePattern,
    ComponentAlternative,
    ComponentDecision,
    ComponentSelectionResult,
    ComponentSummary,
    TradeOffSet,
)
from app.domain.generation import GenerationOptions
from app.domain.requirements import ParsedRequirement
from app.models.component import Component
from app.repositories.component_repository import ComponentRepository
from app.services.claude_client import ClaudeClient

logger = logging.getLogger(__name__)

_CATEGORIES_BASE = [
    "database",
    "cache",
    "api_gateway",
    "compute",
    "monitoring",
]
_CATEGORIES_ASYNC = ["message_queue"]
_CATEGORIES_AI = [
    "llm_provider",
    "vector_database",
    "embedding_model",
]


def _summary_from_orm(c: Component) -> ComponentSummary:
    features = c.features if isinstance(c.features, list) else []
    return ComponentSummary(
        id=str(c.id),
        name=c.name,
        category=c.category,
        vendor=c.vendor,
        features=features,
        icon_url=c.icon_url,
    )


def _trade_from_orm(c: Component) -> TradeOffSet:
    raw = c.trade_offs or {}
    if not isinstance(raw, dict):
        return TradeOffSet()
    pros = raw.get("pros")
    cons = raw.get("cons")
    if not isinstance(pros, list):
        pros = []
    if not isinstance(cons, list):
        cons = []
    return TradeOffSet(
        pros=[str(x) for x in pros],
        cons=[str(x) for x in cons],
    )


def _score_component(req: ParsedRequirement, c: Component) -> float:
    """Heuristic fit score; higher is better."""
    blob = " ".join(
        [
            c.name,
            c.category,
            c.vendor or "",
            str(c.features),
            str(c.selection_criteria),
        ]
    ).lower()
    keywords: list[str] = [req.domain.lower(), req.system_name.lower()]
    keywords.extend(req.core_features)
    for fr in req.functional_requirements:
        keywords.append(fr.name)
        keywords.append(fr.description)
    if req.has_ai_features:
        keywords.extend(["llm", "vector", "embedding", "model", "ml", "ai", "rag"])
    if req.needs_async_processing:
        keywords.extend(["queue", "async", "event", "stream"])
    text = " ".join(keywords).lower()
    tokens = {t for t in re.split(r"\W+", text) if len(t) > 2}
    hit = 0.0
    for t in tokens:
        if t in blob:
            hit += 1.0
    # prefer managed / lower operational burden when scale is high
    crit = c.selection_criteria or {}
    if isinstance(crit, dict) and crit.get("managed_service") is True:
        hit += 0.5
    if c.base_cost_usd is not None and req.budget_constraints:
        hit += 0.1
    return hit


def _pick_top(
    req: ParsedRequirement, candidates: list[Component], k: int = 4
) -> tuple[Component, list[Component]]:
    if not candidates:
        raise ValueError("No candidate components in library for this category")
    ranked = sorted(
        candidates,
        key=lambda c: (-_score_component(req, c), c.name),
    )
    primary = ranked[0]
    alts = ranked[1 : min(k, len(ranked))]
    return primary, alts


_OPTION_TO_PATTERN: dict[str, ArchitecturePattern] = {
    "rag": ArchitecturePattern.RAG_SYSTEM,
    "fine_tuning": ArchitecturePattern.FINE_TUNING_PIPELINE,
    "realtime_inference": ArchitecturePattern.REALTIME_INFERENCE,
    "agentic": ArchitecturePattern.AGENTIC_AI_SYSTEM,
}

_HINT_TO_PATTERN: dict[str, ArchitecturePattern] = {
    "rag": ArchitecturePattern.RAG_SYSTEM,
    "fine_tuning": ArchitecturePattern.FINE_TUNING_PIPELINE,
    "realtime_inference": ArchitecturePattern.REALTIME_INFERENCE,
    "agentic": ArchitecturePattern.AGENTIC_AI_SYSTEM,
}


def _infer_pattern(
    req: ParsedRequirement, options: GenerationOptions | None = None
) -> ArchitecturePattern:
    opts = options or GenerationOptions()
    explicit = opts.aiml_architecture
    if explicit != "auto" and explicit in _OPTION_TO_PATTERN:
        return _OPTION_TO_PATTERN[explicit]

    hint = (req.aiml_architecture_hint or "").strip().lower()
    if hint in _HINT_TO_PATTERN:
        return _HINT_TO_PATTERN[hint]

    blob = " ".join(
        [
            req.summary or "",
            " ".join(req.core_features),
            *(f"{fr.name} {fr.description}" for fr in req.functional_requirements),
        ]
    ).lower()

    if any(
        x in blob
        for x in (
            "fine-tun",
            "fine tun",
            " sft",
            "rlhf",
            "lora",
            "qlora",
            "training pipeline",
            "supervised fine-tuning",
        )
    ):
        return ArchitecturePattern.FINE_TUNING_PIPELINE
    if any(
        x in blob
        for x in (
            "agentic",
            "multi-agent",
            "tool calling",
            "agent orchestration",
            "react agent",
        )
    ):
        return ArchitecturePattern.AGENTIC_AI_SYSTEM
    if any(
        x in blob
        for x in (
            "real-time inference",
            "realtime inference",
            "low-latency inference",
            "model serving",
            "inference endpoint",
            "online inference",
        )
    ):
        return ArchitecturePattern.REALTIME_INFERENCE
    if any(x in blob for x in ("rag", "retrieval augmented", "vector search", "embedding")):
        return ArchitecturePattern.RAG_SYSTEM

    t = " ".join(req.core_features).lower()
    if req.has_ai_features or "rag" in t or "embedding" in t:
        return ArchitecturePattern.RAG_SYSTEM
    if req.needs_async_processing or "event" in t:
        return ArchitecturePattern.EVENT_DRIVEN
    if "microservice" in t:
        return ArchitecturePattern.MICROSERVICES
    return ArchitecturePattern.THREE_TIER


def _needs_ai_component_categories(pattern: ArchitecturePattern) -> bool:
    return pattern in (
        ArchitecturePattern.RAG_SYSTEM,
        ArchitecturePattern.FINE_TUNING_PIPELINE,
        ArchitecturePattern.REALTIME_INFERENCE,
        ArchitecturePattern.AGENTIC_AI_SYSTEM,
    )


class ComponentSelector:
    def __init__(self, session: Session, client: ClaudeClient) -> None:
        self._repo = ComponentRepository(session)
        self._client = client

    def select(
        self,
        requirements: ParsedRequirement,
        options: GenerationOptions | None = None,
    ) -> ComponentSelectionResult:
        pattern = _infer_pattern(requirements, options)
        categories = list(_CATEGORIES_BASE)
        if requirements.needs_async_processing or pattern in (
            ArchitecturePattern.FINE_TUNING_PIPELINE,
            ArchitecturePattern.AGENTIC_AI_SYSTEM,
        ):
            categories.extend(_CATEGORIES_ASYNC)
        if requirements.has_ai_features or _needs_ai_component_categories(pattern):
            categories.extend(_CATEGORIES_AI)
        selections: dict[str, ComponentDecision] = {}
        total_cost = 0.0

        for cat in categories:
            candidates = self._repo.list_by_category(cat)
            if not candidates:
                logger.warning("No components seeded for category %s; skipping", cat)
                continue
            primary, alts = _pick_top(requirements, candidates)
            rationale = self._rationale(requirements, primary, alts, cat)
            alt_models = [
                ComponentAlternative(
                    name=a.name,
                    rejection_reason=self._rejection_blurb(primary, a, requirements),
                )
                for a in alts[:3]
            ]
            est = primary.base_cost_usd
            if est is not None:
                total_cost += float(est)
            selections[cat] = ComponentDecision(
                category=cat,
                selected=_summary_from_orm(primary),
                alternatives=alt_models,
                rationale=rationale,
                trade_offs=_trade_from_orm(primary),
                estimated_monthly_cost_usd=float(est) if est is not None else None,
            )

        return ComponentSelectionResult(
            selections=selections,
            total_monthly_cost_usd=total_cost if total_cost > 0 else None,
            architecture_pattern=pattern,
        )

    def _rationale(
        self,
        req: ParsedRequirement,
        primary: Component,
        alternatives: list[Component],
        category: str,
    ) -> str:
        alt_lines = "\n".join(f"- {a.name}" for a in alternatives[:3]) or "(none)"
        prompt = f"""You are reviewing architecture choices for a {req.domain} system \
named {req.system_name}.

Category: {category}
Selected: {primary.name} ({primary.vendor or 'unknown vendor'})
Alternatives considered:
{alt_lines}

In 3-5 sentences, explain why {primary.name} is a reasonable primary choice for this category \
given the requirements, and name one key trade-off. Stay factual and avoid repeating the full \
requirements list."""
        try:
            return self._client.complete_text(
                system="You write concise architecture review notes.",
                user=prompt,
                max_tokens=400,
                temperature=0.25,
            )
        except Exception as e:
            logger.warning("Rationale generation failed: %s", e)
            return (
                f"{primary.name} scores highest on library fit heuristics for this domain; "
                f"validate against your org standards and non-functional targets."
            )

    def _rejection_blurb(
        self, primary: Component, alt: Component, req: ParsedRequirement
    ) -> str:
        """Short default when Claude is not used per-alternative."""
        sp = _score_component(req, primary)
        sa = _score_component(req, alt)
        if sa < sp:
            return f"Lower fit score for stated domain/features vs {primary.name}."
        return f"Narrowly edged out by {primary.name} on tie-break ordering."
