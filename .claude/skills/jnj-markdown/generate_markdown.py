#!/usr/bin/env python3
"""
JnJ Branded Markdown + HTML Document Generator
Thin CLI wrapper — actual logic lives in skills_building._generate_markdown.

Usage:
    python3 generate_markdown.py --input _research_output.json --output document.md
    # Produces: document.md AND document.html
"""

from skills_building._generate_markdown import main

if __name__ == "__main__":
    main()
