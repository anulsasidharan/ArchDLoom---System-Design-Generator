"""Shared Jinja2 environment for Markdown-oriented templates (no HTML escaping)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "templates"


@lru_cache
def get_markdown_template_env() -> Environment:
    """Environment for `.md.j2` artifacts (plain text; no HTML escaping)."""
    loader = FileSystemLoader(str(_templates_dir()))
    return Environment(
        loader=loader,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(name: str, **context: object) -> str:
    env = get_markdown_template_env()
    return env.get_template(name).render(**context)
