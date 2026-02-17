---
name: research
description: Research a topic with web sources and output a universal cited JSON file for use with any renderer (decks, markdown, HTML)
argument-hint: "[topic or outline]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# Research — Cited Content Generator

Research a topic using web sources and produce a `_research_output.json` file with structured, cited content that **any renderer skill can consume** (decks, markdown documents, HTML reports, etc.).

## How It Works

This skill uses a **framework-agnostic Python script** located at:
`.claude/skills/research/research_agent.py`

The script uses:
- **Tavily API** for web search and content extraction (replaces manual web browsing)
- **OpenAI API** for structuring raw search results into the universal JSON schema

This design makes the research step portable — it works in Claude Code, LangChain, standalone Python, or any other framework.

### Flow
1. The script searches the web for 4-8 authoritative sources via Tavily
2. It feeds the raw content to OpenAI, which structures it into the universal JSON schema
3. The output `_research_output.json` is consumed by a renderer skill of the user's choice:
   - `/jnj-deck` → branded PowerPoint
   - `/jnj-markdown` → branded Markdown + HTML document
   - Future: `/generic-deck`, `/jnj-html`, etc.

## Prerequisites

API keys must be set in a `.env` file at the project root (see `.env.example`):
```
OPENAI_API_KEY=your-key-here
TAVILY_API_KEY=your-key-here
```

Dependencies must be installed:
```bash
uv sync
```

## Instructions

1. **Get the topic** from the user's `$ARGUMENTS` or ask them what the content should cover.

2. **Run the research agent**:
   ```bash
   uv run python3 .claude/skills/research/research_agent.py "<topic>" --output _research_output.json
   ```

   Optional flags:
   - `--max-results N` — number of web sources to fetch (default: 8)
   - `--model <model>` — OpenAI model to use (default: `gpt-4o`)

3. **Read and verify the output** — open `_research_output.json` and confirm:
   - The `meta` section has a clear title and subtitle
   - Sections cover the topic comprehensively (15-30 sections expected)
   - Citations use real URLs from the search results
   - There is a mix of section types (text, bullets, metrics, tables, mermaid, timeline)

4. **Tell the user** the results and instruct them to run a renderer:
   ```
   /jnj-deck        → reads _research_output.json → outputs branded .pptx
   /jnj-markdown    → reads _research_output.json → outputs branded .md + .html
   ```

## Universal JSON Schema

```json
{
    "meta": {
        "title": "Document Title",
        "subtitle": "Subtitle or tagline",
        "date": "2026-02-15",
        "topic": "original topic from user"
    },
    "sections": [
        {
            "type": "heading",
            "title": "Section Title"
        },
        {
            "type": "text",
            "title": "Subsection Title",
            "body": "One or more paragraphs of narrative text. Can be multiple sentences providing context and analysis.",
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        },
        {
            "type": "bullets",
            "title": "Key Points",
            "bullets": ["Point 1", "Point 2", "Point 3"],
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        },
        {
            "type": "metrics",
            "title": "Key Numbers",
            "metrics": [
                {"value": "$10B", "label": "Revenue"},
                {"value": "25%", "label": "Growth"}
            ],
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        },
        {
            "type": "two_column",
            "title": "Comparison",
            "left_title": "Left Header",
            "left_bullets": ["A", "B"],
            "right_title": "Right Header",
            "right_bullets": ["C", "D"],
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        },
        {
            "type": "table",
            "title": "Data Table",
            "columns": ["Name", "Value", "Change"],
            "rows": [
                ["Product A", "$5.2B", "+12%"],
                ["Product B", "$3.1B", "+8%"]
            ],
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        },
        {
            "type": "mermaid",
            "title": "Visual Diagram",
            "chart": "pie title Revenue by Segment\n  \"Oncology\" : 45\n  \"Neuroscience\" : 30\n  \"MedTech\" : 25",
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        },
        {
            "type": "timeline",
            "title": "Key Milestones",
            "events": [
                {"date": "Mar 2024", "event": "FDA approval of Drug X"},
                {"date": "Aug 2025", "event": "Competitor entry"},
                {"date": "H1 2026", "event": "Phase 3 readout expected"}
            ],
            "footnotes": [
                {"label": "Source Name, Year", "url": "https://..."}
            ]
        }
    ]
}
```

### Section Types

| Type          | Required Fields                                         | Description                               | Supports footnotes? |
|---------------|---------------------------------------------------------|-------------------------------------------|---------------------|
| `heading`     | `title`                                                 | Section divider / chapter heading          | No                  |
| `text`        | `title`, `body`                                         | Narrative paragraph(s) with analysis       | Yes                 |
| `bullets`     | `title`, `bullets` (string array)                       | Bullet point list                          | Yes                 |
| `metrics`     | `title`, `metrics` (array of `{value, label}`)          | Key figures / KPIs (2-4 recommended)       | Yes                 |
| `two_column`  | `title`, `left_title`, `left_bullets`, `right_title`, `right_bullets` | Side-by-side comparison      | Yes                 |
| `table`       | `title`, `columns` (string array), `rows` (2D array)   | Data table                                 | Yes                 |
| `mermaid`     | `title`, `chart` (Mermaid.js syntax string)             | Visual diagram (pie, flowchart, timeline)  | Yes                 |
| `timeline`    | `title`, `events` (array of `{date, event}`)            | Chronological milestone list               | Yes                 |

### Renderer Compatibility

Renderers consume this JSON and adapt it to their output format:

| Section type  | `/jnj-deck` maps to        | `/jnj-markdown` maps to          |
|---------------|-----------------------------|-----------------------------------|
| `heading`     | Section divider slide       | `## Heading` with styled divider  |
| `text`        | Bullet slide (split body)   | Styled paragraph                  |
| `bullets`     | Bullet slide                | Bullet list                       |
| `metrics`     | Metrics slide (red boxes)   | Styled metric cards (HTML)        |
| `two_column`  | Two-column slide            | Side-by-side HTML table/columns   |
| `table`       | Bullet slide (summarized)   | Markdown table                    |
| `mermaid`     | *(skipped or summarized)*   | Mermaid code block                |
| `timeline`    | Bullet slide (listed)       | Mermaid timeline or styled list   |

## Citation Rules

- **Every factual claim, statistic, or data point must have a footnote** linking to its source
- Use **real URLs** from the web search results — never fabricate URLs
- Keep footnote labels short: "Source Name, Year" format (e.g., "JnJ 10-K Filing, 2024")
- A section can have 1-4 footnotes; avoid more to keep it clean
- If multiple items come from the same source, use one footnote entry (don't duplicate)
- Headings do not need footnotes
- Clearly distinguish facts (with citations) from strategic recommendations (no citation needed)
- When a number can't be sourced, note it as an estimate or omit it

## Content Guidelines

- Use `text` sections for richer narrative content (context, analysis, transitions)
- Use `bullets` for concise data-heavy lists
- Use `metrics` to highlight 2-4 key figures prominently
- Use `table` for structured comparisons or multi-row data
- Use `mermaid` for visual breakdowns (pie charts, flowcharts, timelines)
- Use `timeline` for chronological events (approvals, milestones, catalysts)
- Mix section types for variety — don't use all bullets
- Include at least one `table` and one `mermaid` or `timeline` per research output

## Example Usage

```
/research jnj prostate cancer drugs market outlook
/research tesla EV market share 2026
/research global AI chip market competitive landscape
```
