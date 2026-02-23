"""Re-exports from the JnJ deck generator for package-level imports.

Usage:
    from skills_building.deck import generate_deck
    result = generate_deck(slide_data, output_path="output/deck.pptx")
    # result['pptx_bytes'], result['pptx_path'], result['slide_count']
"""

import sys
import os

# Add the skill directory to path so the original module is importable
_skill_dir = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "jnj-deck")
_skill_dir = os.path.abspath(_skill_dir)
if _skill_dir not in sys.path:
    sys.path.insert(0, _skill_dir)

from generate_deck import (  # noqa: E402
    generate_deck,
    # Slide builders
    build_title_slide,
    build_bullets_slide,
    build_metrics_slide,
    build_two_column_slide,
    build_section_slide,
    build_thankyou_slide,
    # Helpers
    set_slide_bg,
    add_red_accent_bar,
    add_slide_number,
    add_text_box,
    add_footnotes,
    add_white_separator,
    # Constants
    BUILDERS,
    SLIDE_WIDTH,
    SLIDE_HEIGHT,
    FONT_NAME,
)

__all__ = [
    "generate_deck",
    "build_title_slide",
    "build_bullets_slide",
    "build_metrics_slide",
    "build_two_column_slide",
    "build_section_slide",
    "build_thankyou_slide",
    "set_slide_bg",
    "add_red_accent_bar",
    "add_slide_number",
    "add_text_box",
    "add_footnotes",
    "add_white_separator",
    "BUILDERS",
    "SLIDE_WIDTH",
    "SLIDE_HEIGHT",
    "FONT_NAME",
]


def _cli():
    """CLI entry point for `skills-deck` command."""
    from generate_deck import main  # noqa: E402
    main()
