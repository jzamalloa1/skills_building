"""Skills Building — JnJ-branded research and document generation toolkit."""

from skills_building.research import research
from skills_building.markdown import render as render_markdown, generate_html, generate_markdown
from skills_building.deck import generate_deck

__all__ = [
    "research",
    "render_markdown",
    "generate_html",
    "generate_markdown",
    "generate_deck",
]
