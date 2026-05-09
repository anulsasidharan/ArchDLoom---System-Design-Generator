"""Natural-language requirement extraction via Claude."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError

from app.domain.generation import GenerationOptions
from app.domain.requirements import ParsedRequirement
from app.exceptions import RequirementParseError
from app.services.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


_SYSTEM = """You are an expert solutions architect. Extract structured requirements from \
user text for system design documentation. Respond with a single JSON object only, no markdown \
outside JSON. Use sensible assumptions when details are missing; note uncertainties briefly \
in "summary". Set "clarification_questions" only when critical blocking details are missing \
(for example unspecified regulated data class when compliance is implied)."""


def build_parse_prompt(user_input: str, options: GenerationOptions | None) -> str:
    opts = options or GenerationOptions()
    return f"""Analyze this system design request and return JSON matching this shape:
{{
  "system_name": string,
  "domain": string (e.g. e-commerce, healthcare, fintech, education, general),
  "summary": string,
  "core_features": string[],
  "scale_metrics": {{
    "daily_active_users": number | null,
    "peak_requests_per_second": number | null,
    "data_volume_gb": number | null,
    "mvp_users": number | null,
    "growth_users": number | null
  }},
  "functional_requirements": [
    {{ "name": string, "description": string, "user_stories": [{{"role","action","benefit"}}] }}
  ],
  "non_functional_requirements": {{
    "latency_target": string | null,
    "availability_target": string | null,
    "throughput_target": string | null,
    "concurrent_users": string | null,
    "rto": string | null,
    "rpo": string | null
  }},
  "compliance_needs": [{{ "name": string, "description": string }}],
  "tech_preferences": {{ string: string }},
  "budget_constraints": {{ string: string }},
  "business_goals": string[],
  "success_metrics": [{{ "name", "target", "measurement" }}],
  "constraints": string[],
  "needs_async_processing": boolean,
  "has_ai_features": boolean,
  "clarification_questions": string[]
}}

Generation options (hints): focus_ai_ml={opts.focus_ai_ml}, compliance_emphasis=\
{opts.compliance_emphasis}, include_cost_estimates={opts.include_cost_estimates}.

User request:
---
{user_input}
---
"""


class RequirementParser:
    def __init__(self, client: ClaudeClient) -> None:
        self._client = client

    def parse(self, user_input: str, options: GenerationOptions | None = None) -> ParsedRequirement:
        prompt = build_parse_prompt(user_input.strip(), options)
        try:
            data = self._client.complete_json_object(system=_SYSTEM, user=prompt)
        except Exception as e:
            logger.exception("Claude JSON completion failed")
            raise RequirementParseError(str(e)) from e

        return _validate_parsed(data)


def _validate_parsed(data: dict[str, Any]) -> ParsedRequirement:
    try:
        return ParsedRequirement.model_validate(data)
    except ValidationError as e:
        logger.warning("ParsedRequirement validation failed: %s", e)
        raise RequirementParseError(f"Invalid structured requirement payload: {e}") from e
