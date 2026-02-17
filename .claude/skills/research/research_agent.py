#!/usr/bin/env python3
"""
Research Agent — Framework-agnostic research tool.
Uses Tavily API for web search and OpenAI for structuring results
into the universal _research_output.json schema.

Usage:
    python3 research_agent.py "GLP-1 competitive landscape 2026"
    python3 research_agent.py --topic "AI chip market" --output reports/research.json
    python3 research_agent.py "topic" --max-results 10 --model gpt-4o-mini
"""

import json
import os
import sys
import argparse
from datetime import date

from dotenv import load_dotenv, find_dotenv
from tavily import TavilyClient
from openai import OpenAI


# Maximum characters of raw_content to include per source
MAX_CONTENT_CHARS = 3500


# ═══════════════════════════════════════════════════════════
# JSON SCHEMA (embedded for the LLM structuring prompt)
# ═══════════════════════════════════════════════════════════

SCHEMA_REFERENCE = """
{
    "meta": {
        "title": "Document Title",
        "subtitle": "Subtitle or tagline",
        "date": "YYYY-MM-DD",
        "topic": "original topic from user"
    },
    "sections": [
        {"type": "heading", "title": "Section Title"},
        {"type": "text", "title": "Subsection Title", "body": "Narrative paragraph(s)...", "footnotes": [{"label": "Source Name, Year", "url": "https://..."}]},
        {"type": "bullets", "title": "Key Points", "bullets": ["Point 1", "Point 2"], "footnotes": [...]},
        {"type": "metrics", "title": "Key Numbers", "metrics": [{"value": "$10B", "label": "Revenue"}], "footnotes": [...]},
        {"type": "two_column", "title": "Comparison", "left_title": "Left", "left_bullets": ["A"], "right_title": "Right", "right_bullets": ["B"], "footnotes": [...]},
        {"type": "table", "title": "Data Table", "columns": ["Name", "Value"], "rows": [["A", "1"]], "footnotes": [...]},
        {"type": "mermaid", "title": "Diagram", "chart": "pie title Revenue\\n  \\"Seg A\\" : 45\\n  \\"Seg B\\" : 30", "footnotes": [...]},
        {"type": "timeline", "title": "Milestones", "events": [{"date": "2024", "event": "Something happened"}], "footnotes": [...]}
    ]
}
"""

SYSTEM_PROMPT = f"""You are a senior research analyst. Your task is to synthesize web search results into a structured JSON research document.

## Output Format
You MUST return a valid JSON object following this exact schema:
{SCHEMA_REFERENCE}

## Section Types Available
- "heading": Section divider (title only, no footnotes)
- "text": Narrative paragraphs with analysis (title, body, footnotes)
- "bullets": Bullet point lists (title, bullets array, footnotes)
- "metrics": Key figures / KPIs with 2-4 items (title, metrics array of {{value, label}}, footnotes)
- "two_column": Side-by-side comparison (title, left_title, left_bullets, right_title, right_bullets, footnotes)
- "table": Structured data table (title, columns array, rows 2D array, footnotes)
- "mermaid": Mermaid.js diagram — pie charts, xychart-beta bar charts, quadrantChart, or timeline (title, chart string, footnotes)
- "timeline": Chronological events (title, events array of {{date, event}}, footnotes)

## Rules
1. Every factual claim, statistic, or data point MUST have a footnote with a real URL from the provided sources.
2. Use ONLY URLs from the provided search results — never fabricate URLs.
3. Footnote label format: "Source Name, Year" (e.g., "CNBC - GLP-1 Market Report, 2025").
4. Each section can have 1-4 footnotes maximum.
5. Include at least one "table" and one "mermaid" or "timeline" per document.
6. Mix section types for variety — don't use all bullets.
7. Use "metrics" to highlight 2-4 key figures prominently.
8. Use rich narrative in "text" sections — be descriptive and analytical.
9. Aim for 15-30 sections total with a logical flow: overview → deep-dive → outlook.
10. The "meta.date" should be today's date.
11. For mermaid charts: use pie, xychart-beta (bar charts), quadrantChart, or timeline syntax.
12. Distinguish facts (with citations) from strategic analysis (no citation needed).
13. When a number can't be sourced from the provided results, note it as an estimate or omit it.
"""


# ═══════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════

def load_env():
    """Load environment variables from .env file."""
    load_dotenv(find_dotenv(usecwd=True))

    missing = []
    if not os.environ.get("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if not os.environ.get("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Please set them in your .env file. See .env.example for reference.", file=sys.stderr)
        sys.exit(1)


def truncate_content(text, max_chars=MAX_CONTENT_CHARS):
    """Truncate text to max_chars to stay within LLM token limits."""
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"


def tavily_search(topic, max_results=8):
    """Search the web using Tavily API with full content extraction."""
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    print(f"Searching for: {topic}", file=sys.stderr)
    print(f"Fetching up to {max_results} sources with full content...", file=sys.stderr)

    try:
        response = client.search(
            query=topic,
            search_depth="advanced",
            include_raw_content=True,
            max_results=max_results,
        )
    except Exception as e:
        print(f"Error: Tavily search failed: {e}", file=sys.stderr)
        sys.exit(1)

    results = response.get("results", [])
    print(f"Found {len(results)} sources.", file=sys.stderr)
    return response


def format_sources_for_llm(search_results):
    """Format Tavily results into a clean structure for the LLM prompt."""
    sources = []
    for i, result in enumerate(search_results.get("results", [])):
        # Prefer raw_content (full page), fall back to content (snippet)
        raw = result.get("raw_content") or ""
        snippet = result.get("content") or ""
        content = truncate_content(raw) if raw else snippet

        sources.append({
            "index": i + 1,
            "title": result.get("title", "Untitled"),
            "url": result.get("url", ""),
            "content": content,
        })
    return sources


def structure_research(topic, search_results, model="gpt-4o"):
    """Use OpenAI to structure raw search results into the universal JSON schema."""
    client = OpenAI()
    sources = format_sources_for_llm(search_results)

    if not sources:
        print("Error: No search results to structure.", file=sys.stderr)
        sys.exit(1)

    user_prompt = f"""Research Topic: {topic}
Today's Date: {date.today().isoformat()}

I found {len(sources)} sources. Here they are:

{json.dumps(sources, indent=2, ensure_ascii=False)}

Based on these sources, produce a comprehensive research document as a JSON object.
The document should have:
- A clear title and subtitle in "meta"
- 15-30 sections covering: executive summary, market landscape, key metrics, deep-dive analysis, competitive positioning, outlook
- At least 1 table, 1 mermaid diagram, and 1 timeline
- Every factual claim cited with footnotes using ONLY the URLs from the sources above
- Rich narrative in text sections — this is a report, not slides

Return ONLY the JSON object. No other text."""

    print(f"Structuring research with {model}...", file=sys.stderr)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
    except Exception as e:
        print(f"Error: OpenAI API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        print(f"Raw response:\n{content[:500]}...", file=sys.stderr)
        sys.exit(1)

    # Basic validation
    if "meta" not in result:
        result["meta"] = {
            "title": topic,
            "subtitle": "",
            "date": date.today().isoformat(),
            "topic": topic,
        }

    if "sections" not in result or not result["sections"]:
        print("Error: LLM returned no sections.", file=sys.stderr)
        sys.exit(1)

    return result


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Research a topic using Tavily search + OpenAI structuring. "
                    "Outputs a universal JSON file for use with renderer skills.",
    )
    parser.add_argument(
        "topic",
        nargs="?",
        help="The research topic (positional argument)",
    )
    parser.add_argument(
        "--topic", "-t",
        dest="topic_flag",
        help="The research topic (named argument, alternative to positional)",
    )
    parser.add_argument(
        "--output", "-o",
        default="_research_output.json",
        help="Output JSON file path (default: _research_output.json)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=8,
        help="Number of Tavily search results to fetch (default: 8)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use for structuring (default: gpt-4o)",
    )

    args = parser.parse_args()
    topic = args.topic or args.topic_flag

    if not topic:
        parser.error("Topic is required. Provide as positional argument or with --topic/-t flag.")

    # Load API keys
    load_env()

    # Step 1: Search the web
    search_results = tavily_search(topic, max_results=args.max_results)

    # Step 2: Structure into JSON schema
    structured = structure_research(topic, search_results, model=args.model)

    # Step 3: Write output
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # Summary
    section_count = len(structured.get("sections", []))
    urls = set()
    for section in structured.get("sections", []):
        for fn in section.get("footnotes", []):
            urls.add(fn.get("url", ""))

    print(f"\nResearch saved to: {args.output}", file=sys.stderr)
    print(f"Sections: {section_count}", file=sys.stderr)
    print(f"Unique sources cited: {len(urls)}", file=sys.stderr)
    print(f"Title: {structured.get('meta', {}).get('title', 'N/A')}", file=sys.stderr)


if __name__ == "__main__":
    main()
