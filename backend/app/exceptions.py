"""Application-specific errors."""


class ArchDLoomError(Exception):
    """Base error for ArchDLoom backend."""


class ClaudeConfigurationError(ArchDLoomError):
    """Missing or invalid Claude / Anthropic configuration."""


class ClaudeAPIError(ArchDLoomError):
    """Anthropic API request failed or returned an unexpected payload."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RequirementParseError(ArchDLoomError):
    """Could not parse model output into ParsedRequirement."""
