# Skills Building

Claude Code skills for automated research, branded document generation, and presentation creation.

## Skills

### `/research`
Research any topic using web sources and produce a structured, cited JSON file (`_research_output.json`). Uses a framework-agnostic Python agent powered by [Tavily](https://tavily.com/) for web search and [OpenAI](https://openai.com/) for content structuring — portable across Claude Code, LangChain, or standalone Python.

### `/jnj-markdown`
Generate a professional Markdown + standalone HTML document from `_research_output.json`. Features JnJ brand styling, Mermaid.js diagrams (pie charts, timelines, quadrant plots), data tables, metric cards, and inline citations. The HTML output is fully self-contained with embedded CSS and Mermaid CDN.

### `/jnj-deck`
Generate a branded Johnson & Johnson PowerPoint deck (`.pptx`) from `_research_output.json`. Supports title, bullet, metrics, two-column, section divider, and thank-you slide types with JnJ brand colors and footnote citations.

## Workflow

```
/research <topic>       →  _research_output.json
/jnj-markdown           →  branded .md + .html report
/jnj-deck               →  branded .pptx presentation
```

Skills can be chained: run `/research` first, then pipe the output to either renderer.

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI (for running skills as slash commands)

### Installation

```bash
# Clone the repo
git clone https://github.com/jzamalloa1/skills_building.git
cd skills_building

# Install dependencies
uv sync

# Configure API keys
cp .env.example .env
# Edit .env with your actual keys
```

### API Keys

The `/research` skill requires two API keys in a `.env` file at the project root:

| Variable          | Service | Purpose                          |
|-------------------|---------|----------------------------------|
| `OPENAI_API_KEY`  | OpenAI  | Structures research into JSON    |
| `TAVILY_API_KEY`  | Tavily  | Web search and content extraction|

## Universal JSON Schema

All skills share a universal JSON schema (`_research_output.json`) with a `meta` header and a `sections` array supporting 8 section types:

| Type         | Description                          |
|--------------|--------------------------------------|
| `heading`    | Section divider / chapter heading    |
| `text`       | Narrative paragraph(s) with analysis |
| `bullets`    | Bullet point list                    |
| `metrics`    | Key figures / KPIs (2-4 recommended) |
| `two_column` | Side-by-side comparison              |
| `table`      | Structured data table                |
| `mermaid`    | Visual diagram (pie, flowchart, etc) |
| `timeline`   | Chronological milestone list         |

## Project Structure

```
skills_building/
├── .claude/skills/
│   ├── research/
│   │   ├── SKILL.md              # Skill definition
│   │   └── research_agent.py     # Tavily + OpenAI research agent
│   ├── jnj-markdown/
│   │   ├── SKILL.md              # Skill definition
│   │   └── generate_markdown.py  # Markdown + HTML generator
│   └── jnj-deck/
│       ├── SKILL.md              # Skill definition
│       └── generate_deck.py      # PowerPoint generator
├── sample_output/                # Example generated files
├── .env.example                  # API key template
├── .gitignore
├── pyproject.toml                # Dependencies (uv)
└── README.md
```

## Example Usage

```bash
# In Claude Code:
/research GLP-1 drugs competitive landscape 2024-2031
/jnj-markdown    # generates .md + .html from research output
/jnj-deck        # generates .pptx from research output
```

Output destination is customizable — each renderer will ask where to save files if not specified.
