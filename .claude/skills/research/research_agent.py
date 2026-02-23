#!/usr/bin/env python3
"""
Research Agent — Framework-agnostic research tool.
Thin CLI wrapper — actual logic lives in skills_building._research_agent.

Usage:
    python3 research_agent.py "GLP-1 competitive landscape 2026"
    python3 research_agent.py --topic "AI chip market" --output reports/research.json
    python3 research_agent.py "topic" --max-results 10 --model gpt-4o-mini
"""

from skills_building._research_agent import main

if __name__ == "__main__":
    main()
