"""Re-exports from the research agent skill for package-level imports.

Usage:
    from skills_building.research import research
    result = research("GLP-1 competitive landscape", max_results=8)
"""

import sys
import os

# Add the skill directory to path so the original module is importable
_skill_dir = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "research")
_skill_dir = os.path.abspath(_skill_dir)
if _skill_dir not in sys.path:
    sys.path.insert(0, _skill_dir)

from research_agent import (  # noqa: E402
    research,
    tavily_search,
    format_sources_for_llm,
    structure_research,
    load_env,
    truncate_content,
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
    from research_agent import main  # noqa: E402
    main()
