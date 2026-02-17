---
name: jnj-markdown
description: Generate a rich JnJ-branded Markdown + HTML document with Mermaid diagrams, tables, and cited sources
argument-hint: "[topic or outline]"
disable-model-invocation: true
allowed-tools: Bash, Write, Read, Glob, Grep
---

# JnJ Branded Markdown + HTML Document Generator

Generate a professional, richly formatted document in **two formats** simultaneously:
1. **Markdown** (`.md`) — HTML-enhanced Markdown with inline styles, Mermaid code blocks, and clickable citations. Best for developers using VS Code, GitHub, or similar tools.
2. **Standalone HTML** (`.html`) — A fully self-contained HTML file with JnJ-branded CSS, Mermaid CDN for diagram rendering, responsive design, and print styles. Best for sharing with non-technical stakeholders via browser.

## How It Works

This skill uses a **reusable Python script** located at:
`.claude/skills/jnj-markdown/generate_markdown.py`

You do NOT write new scripts each time. Instead:
1. If `_research_output.json` already exists (from `/research`), use it directly
2. Otherwise, compose a JSON content definition and write it to `_research_output.json`
3. Run the generator script — it produces **both** `.md` and `.html` automatically

## Input Source

The generator reads **`_research_output.json`** from the current working directory. This file follows the universal research schema (see `/research` skill).

If the user has already run `/research`, the file will exist. If not, compose the JSON content following the schema documented below and write it to `_research_output.json`.

## Instructions

1. **Check if `_research_output.json` exists** in the current working directory.
   - If yes: use it directly
   - If no: compose the content JSON and write it

2. **Determine the output destination.**
   - If the user specified a destination folder or file path, use it.
   - If the user did NOT specify a destination, **ask them** where they want the files saved before proceeding.
     Example prompt: "Where would you like the document saved? (e.g., `output/my-report.md` or just a folder like `reports/`)"
   - If only a folder is given, construct the filename as `<folder>/<slugified-topic>.md`.
   - The generator auto-creates any needed directories.
   - Remember: both `.md` and `.html` files will be written to the same directory.

3. **Run the generator**:
   ```bash
   uv run python3 .claude/skills/jnj-markdown/generate_markdown.py --input _research_output.json --output <destination>/<slugified-topic>.md && rm _research_output.json
   ```
   This produces **two files**:
   - `<destination>/<slugified-topic>.md` — Markdown with inline HTML styling
   - `<destination>/<slugified-topic>.html` — Standalone HTML (auto-generated from same `--output` flag by replacing `.md` → `.html`)

4. **Tell the user** both output file paths and section count.

## Brand Colors (embedded by the generator)

| Color            | Hex       | Usage                                          |
|------------------|-----------|-------------------------------------------------|
| **JnJ Red**      | `#D51900` | Section headings, accent borders, metric cards  |
| **JnJ Dark Red** | `#9B0600` | Sub-headings, column headers                    |
| **White**         | `#FFFFFF` | Card backgrounds, text on red                   |
| **Black**         | `#1A1A1A` | Body text                                       |
| **Light Gray**    | `#F2F2F2` | Alternate backgrounds, callout boxes            |
| **Medium Gray**   | `#6D6E71` | Captions, footnotes, secondary text             |

## JSON Input Schema

```json
{
    "meta": {
        "title": "Document Title",
        "subtitle": "Subtitle",
        "date": "2026-02-15",
        "topic": "original topic"
    },
    "sections": [
        {"type": "heading", "title": "Section Title"},
        {"type": "text", "title": "Title", "body": "Paragraph text...", "footnotes": [...]},
        {"type": "bullets", "title": "Title", "bullets": ["A", "B"], "footnotes": [...]},
        {"type": "metrics", "title": "Title", "metrics": [{"value": "$10B", "label": "Revenue"}], "footnotes": [...]},
        {"type": "two_column", "title": "Title", "left_title": "L", "left_bullets": ["A"], "right_title": "R", "right_bullets": ["B"], "footnotes": [...]},
        {"type": "table", "title": "Title", "columns": ["A", "B"], "rows": [["1", "2"]], "footnotes": [...]},
        {"type": "mermaid", "title": "Title", "chart": "pie title...\n  ...", "footnotes": [...]},
        {"type": "timeline", "title": "Title", "events": [{"date": "2024", "event": "..."}], "footnotes": [...]}
    ]
}
```

## Output Styling

### Markdown (`.md`)
- JnJ Red styled header block with title and subtitle (inline HTML)
- Section headings with red left-border accents
- Metric cards as inline HTML with red backgrounds and white text
- Two-column layouts using HTML flexbox
- Styled Markdown tables
- Mermaid diagram code blocks (render in GitHub, VS Code, etc.)
- Timelines as Mermaid timeline diagrams with text fallback
- Footnotes as numbered clickable hyperlinks below each section
- Collected references section at the end

### HTML (`.html`)
All the above, plus:
- Full CSS stylesheet with JnJ brand colors embedded
- Mermaid CDN (`mermaid@11`) loaded via ES module for browser-based diagram rendering
- Mermaid themed with JnJ brand colors (`primaryColor: #D51900`, etc.)
- Responsive layout — stacks columns and metrics on mobile (`@media max-width: 720px`)
- Print-optimized styles (`@media print`)
- Red-header tables with zebra-striped rows
- Self-contained — no external dependencies except the Mermaid CDN

## Example Usage

```
/jnj-markdown                              → uses existing _research_output.json
/jnj-markdown quarterly business review     → composes content + generates markdown + HTML
```

## Content Guidelines

- Use rich narrative in `text` sections — this is markdown, not slides; be descriptive
- Tables should have clear column headers and aligned data
- Include at least one Mermaid diagram for visual richness
- Footnotes appear inline below each section as small linked references
- Keep the document scannable: use headings, bullets, and metrics to break up text
- The HTML output is ideal for emailing or sharing via link with non-technical stakeholders
