"""Re-exports from the JnJ markdown/HTML generator for package-level imports.

Usage:
    from skills_building.markdown import render
    result = render(research_data, output_path="output/report.md")
    # result['markdown'], result['html'], result['md_path'], result['html_path']
"""

from skills_building._generate_markdown import (
    render,
    generate_markdown,
    generate_html,
    main,
    # Individual renderers (Markdown)
    render_header,
    render_heading,
    render_text,
    render_bullets,
    render_metrics,
    render_two_column,
    render_table,
    render_mermaid,
    render_timeline,
    render_references,
    render_footnotes,
    render_footer,
    # Individual renderers (HTML)
    html_header,
    html_heading,
    html_text,
    html_bullets,
    html_metrics,
    html_two_column,
    html_table,
    html_mermaid,
    html_timeline,
    html_references,
    html_footnotes,
    html_footer,
    # Constants
    JNJ_RED,
    JNJ_DARK_RED,
    WHITE,
    BLACK,
    LIGHT_GRAY,
    MEDIUM_GRAY,
)

__all__ = [
    "render",
    "generate_markdown",
    "generate_html",
    "render_header",
    "render_heading",
    "render_text",
    "render_bullets",
    "render_metrics",
    "render_two_column",
    "render_table",
    "render_mermaid",
    "render_timeline",
    "render_references",
    "render_footnotes",
    "render_footer",
    "html_header",
    "html_heading",
    "html_text",
    "html_bullets",
    "html_metrics",
    "html_two_column",
    "html_table",
    "html_mermaid",
    "html_timeline",
    "html_references",
    "html_footnotes",
    "html_footer",
    "JNJ_RED",
    "JNJ_DARK_RED",
    "WHITE",
    "BLACK",
    "LIGHT_GRAY",
    "MEDIUM_GRAY",
]


def _cli():
    """CLI entry point for `skills-markdown` command."""
    main()
