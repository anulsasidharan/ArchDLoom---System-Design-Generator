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


def build_parse_prompt(
    user_input: str,
    options: GenerationOptions | None,
    *,
    existing_document_text: str | None = None,
    existing_document_filename: str | None = None,
    reference_document_text: str | None = None,
    reference_document_filename: str | None = None,
) -> str:
    opts = options or GenerationOptions()
    base = f"""Analyze this system design request and return JSON matching this shape:
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
  "aiml_architecture_hint": string | null,
  "clarification_questions": string[]
}}

When the system is clearly AI/ML-specific, set aiml_architecture_hint to one of:
"rag", "fine_tuning", "realtime_inference", "agentic", or null if unclear or not AI-focused.

Generation options (hints): focus_ai_ml={opts.focus_ai_ml}, compliance_emphasis=\
{opts.compliance_emphasis}, include_cost_estimates={opts.include_cost_estimates}.
"""

    sections: list[str] = [base.rstrip()]

    if existing_document_text:
        name = existing_document_filename or "uploaded_project_document"
        sections.append(
            f"""
### Uploaded project document to enhance (primary source)
The user wants this material treated as an existing PRD, HLD, LLD, architecture note, \
or mixed documentation. Your job is to **expertly enhance** it:
- Preserve accurate facts, names, and constraints from the upload; infer and fill sensible \
values only where unclear.
- Strengthen completeness: missing NFRs, scale, risks, compliance, observability, and data flows \
should be inferred or surfaced in "constraints" / "clarification_questions".
- Output the same JSON schema as usual; derive `system_name` and `summary` from the document \
if the written instructions below are brief or empty.

File name hint: {name}

--- begin uploaded document ---
{existing_document_text}
--- end uploaded document ---
"""
        )

    if reference_document_text:
        rname = reference_document_filename or "reference_document"
        sections.append(
            f"""
### Reference document (style and depth guide)
Use this as a **reference** for tone, structure expectations, terminology, and level of detail. \
Apply it when enriching the structured requirements; **do not** treat it as the product under \
design unless it clearly describes the same system. When it conflicts with the user's written \
instructions or the uploaded project document, prefer the user's instructions and project upload.

File name hint: {rname}

--- begin reference ---
{reference_document_text}
--- end reference ---
"""
        )

    sections.append(
        f"""
### Written instructions from the user (may be empty if the upload is the main input)
---
{user_input}
---
"""
    )

    sections.append(
        """
Return only the JSON object described in the schema above."""
    )
    return "\n".join(sections)


class RequirementParser:
    def __init__(self, client: ClaudeClient) -> None:
        self._client = client

    def parse(
        self,
        user_input: str,
        options: GenerationOptions | None = None,
        *,
        existing_document_text: str | None = None,
        existing_document_filename: str | None = None,
        reference_document_text: str | None = None,
        reference_document_filename: str | None = None,
    ) -> ParsedRequirement:
        prompt = build_parse_prompt(
            user_input.strip(),
            options,
            existing_document_text=existing_document_text,
            existing_document_filename=existing_document_filename,
            reference_document_text=reference_document_text,
            reference_document_filename=reference_document_filename,
        )
        system = _SYSTEM
        if existing_document_text:
            system += (
                "\n\nWhen an uploaded project document is provided, treat it as the primary "
                "source of truth for names and stated facts; expand and harden it into the "
                "JSON schema without inventing contradictory requirements."
            )
        if reference_document_text:
            system += (
                "\n\nWhen a reference document is provided, use it for documentation style, "
                "terminology, and expected depth; the product under design still follows user "
                "instructions and any project upload unless the reference clearly describes the "
                "same initiative."
            )
        try:
            data = self._client.complete_json_object(system=system, user=prompt)
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
