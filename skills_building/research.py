"""Re-exports from the research agent for package-level imports.

Usage:
    from skills_building.research import research
    result = research("GLP-1 competitive landscape", max_results=8)
"""

from skills_building._research_agent import (
    research,
    tavily_search,
    format_sources_for_llm,
    structure_research,
    load_env,
    truncate_content,
    main,
    SCHEMA_REFERENCE,
    SYSTEM_PROMPT,
    MAX_CONTENT_CHARS,
)

__all__ = [
    "research",
    "tavily_search",
    "format_sources_for_llm",
    "structure_research",
    "load_env",
    "truncate_content",
    "SCHEMA_REFERENCE",
    "SYSTEM_PROMPT",
    "MAX_CONTENT_CHARS",
]


def _cli():
    """CLI entry point for `skills-research` command."""
    main()
