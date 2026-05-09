"""Thin synchronous wrapper around the Anthropic Messages API."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from anthropic import Anthropic, APIError

from app.exceptions import ClaudeAPIError, ClaudeConfigurationError

logger = logging.getLogger(__name__)


_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


class ClaudeClient:
    """Minimal client for text + JSON extraction workflows."""

    def __init__(
        self,
        api_key: str | None,
        *,
        model: str = "claude-3-5-sonnet-20241022",
    ) -> None:
        if not api_key or not api_key.strip():
            raise ClaudeConfigurationError("ANTHROPIC_API_KEY is not set")
        self._client = Anthropic(api_key=api_key.strip())
        self._model = model

    def complete_text(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Return assistant plain text (leading/trailing whitespace stripped)."""
        try:
            msg = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except APIError as e:
            status_code = getattr(e, "status_code", None)
            if status_code == 429:
                logger.warning("Anthropic rate limited: %s", e)
            else:
                logger.warning("Anthropic API error: %s", e)
            raise ClaudeAPIError(str(e), status_code=status_code) from e

        parts: list[str] = []
        for block in msg.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "".join(parts).strip()

    def complete_json_object(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Ask for JSON; parse fenced or raw object from the assistant reply."""
        raw = self.complete_text(
            system=system,
            user=user,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        try:
            return _parse_json_object(raw)
        except json.JSONDecodeError as e:
            logger.debug("JSON parse failed; raw prefix: %s", raw[:500])
            raise ClaudeAPIError(f"Model did not return valid JSON: {e}") from e


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    m = _JSON_FENCE.search(text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)
