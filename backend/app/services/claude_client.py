"""Thin synchronous wrapper around the Anthropic Messages API."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from anthropic import Anthropic, APIError

from app.exceptions import ClaudeAPIError, ClaudeConfigurationError

logger = logging.getLogger(__name__)

_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)

_RETRY_STATUS_CODES = {500, 502, 503, 529}
_MAX_RETRIES = 3
_RETRY_DELAY = 5  # seconds


class ClaudeClient:
    """Minimal client for text + JSON extraction workflows."""

    def __init__(
        self,
        api_key: str | None,
        *,
        model: str = "claude-sonnet-4-6",
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
        """Return assistant plain text using streaming (supports large max_tokens)."""
        last_exc: APIError | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                with self._client.messages.stream(
                    model=self._model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                ) as stream:
                    msg = stream.get_final_message()
                break
            except APIError as e:
                status_code = getattr(e, "status_code", None)
                last_exc = e
                if status_code in _RETRY_STATUS_CODES and attempt < _MAX_RETRIES:
                    logger.warning(
                        "Anthropic transient error (attempt %d/%d, status %s): %s",
                        attempt, _MAX_RETRIES, status_code, e,
                    )
                    time.sleep(_RETRY_DELAY * attempt)
                    continue
                if status_code == 429:
                    logger.warning("Anthropic rate limited: %s", e)
                else:
                    logger.warning("Anthropic API error: %s", e)
                raise ClaudeAPIError(str(e), status_code=status_code) from e
        else:
            status_code = getattr(last_exc, "status_code", None)
            raise ClaudeAPIError(str(last_exc), status_code=status_code) from last_exc

        parts: list[str] = []
        for block in msg.content:
            if hasattr(block, "text"):
                parts.append(block.text)

        result = "".join(parts).strip()

        if not result:
            logger.error(
                "Empty response from model. stop_reason=%s, content_blocks=%d, model=%s",
                msg.stop_reason,
                len(msg.content),
                self._model,
            )
            raise ClaudeAPIError(
                f"Model returned empty response (stop_reason={msg.stop_reason!r}). "
                "This may be a transient API issue — please retry."
            )

        if msg.stop_reason == "max_tokens":
            logger.warning("Response hit max_tokens limit; JSON may be truncated.")

        return result

    def complete_json_object(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 32768,
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
            logger.error("JSON parse failed; raw prefix: %.500s", raw)
            raise ClaudeAPIError(f"Model did not return valid JSON: {e}") from e


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    m = _JSON_FENCE.search(text)
    if m:
        text = m.group(1).strip()
    else:
        # Truncated response: fence was opened but never closed — strip the opening marker
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    return json.loads(text)
