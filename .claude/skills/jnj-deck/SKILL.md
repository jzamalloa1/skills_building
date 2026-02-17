---
name: jnj-deck
description: Generate a branded Johnson & Johnson PowerPoint deck with JnJ company colors and styling
argument-hint: "[topic or outline]"
disable-model-invocation: true
allowed-tools: Bash, Write, Read, Glob, Grep
---

# JnJ Branded PowerPoint Deck Generator

Generate a professional PowerPoint presentation using official Johnson & Johnson brand colors and styling.

## How It Works

This skill uses a **reusable Python script** located at:
`.claude/skills/jnj-deck/generate_deck.py`

You do NOT write a new Python script each time. Instead:
1. Compose a JSON slide definition
2. Pipe it to the generator script via stdin

## Brand Colors (for reference when writing content)

| Color            | Hex       | Usage                                      |
|------------------|-----------|---------------------------------------------|
| **JnJ Red**      | `#D51900` | Primary accent, title bars, key highlights  |
| **JnJ Dark Red** | `#9B0600` | Secondary accent, darker elements, footers  |
| **White**         | `#FFFFFF` | Backgrounds, text on red backgrounds        |
| **Black**         | `#1A1A1A` | Body text                                   |
| **Light Gray**    | `#F2F2F2` | Alternate slide backgrounds, content boxes  |
| **Medium Gray**   | `#6D6E71` | Subtitles, captions, secondary text         |

## Input Sources

The generator accepts two JSON formats:

1. **`_research_output.json`** (from `/research` skill) — universal research format with `meta` + `sections`. The skill must convert this to slide format before passing to the generator.
2. **`_deck_input.json`** (native slide format) — direct slide definitions with `slides` array.

**If `_research_output.json` exists**, use it. Convert the universal sections to slides:
- `heading` → `section` slide
- `text` → `bullets` slide (split body into bullet points)
- `bullets` → `bullets` slide
- `metrics` → `metrics` slide
- `two_column` → `two_column` slide
- `table` → `bullets` slide (summarize key rows)
- `mermaid` → skip (not supported in .pptx)
- `timeline` → `bullets` slide (list events as bullets)
- Add a `title` slide from `meta.title` / `meta.subtitle` at the start
- Add a `thankyou` slide at the end
- Preserve all `footnotes` arrays

## Instructions

1. **Ensure dependencies are installed**:
   ```bash
   uv sync
   ```

2. **Check for input files** in this priority order:
   - If `_research_output.json` exists → convert to slide JSON, write to `_deck_input.json`
   - If `_deck_input.json` exists → use it directly
   - Otherwise → gather the topic from `$ARGUMENTS`, compose slide JSON, write to `_deck_input.json`

3. **Determine the output destination.**
   - If the user specified a destination folder or file path, use it.
   - If the user did NOT specify a destination, **ask them** where they want the file saved before proceeding.
     Example prompt: "Where would you like the deck saved? (e.g., `output/my-deck.pptx` or just a folder like `reports/`)"
   - If only a folder is given, construct the filename as `<folder>/<slugified-topic>-deck.pptx`.
   - The generator will auto-create any needed directories.

4. **Plan the slide structure.** A typical deck includes:
   - Title slide (red background, white text)
   - Agenda / Overview slide
   - Content slides (bullets, two-column, metrics)
   - Summary / Next Steps
   - Thank You / Q&A slide (red background)

5. **Run the generator** and **delete the JSON file(s)** afterward:

   ```bash
   uv run python3 .claude/skills/jnj-deck/generate_deck.py --input _deck_input.json --output <destination>/<slugified-topic>-deck.pptx && rm -f _deck_input.json _research_output.json
   ```

6. **Tell the user** the output file path and slide count.

## JSON Schema

```json
{
    "slides": [
        {
            "type": "title",
            "title": "Presentation Title",
            "subtitle": "Optional subtitle"
        },
        {
            "type": "bullets",
            "title": "Slide Title",
            "bullets": ["Point 1", "Point 2", "Point 3"]
        },
        {
            "type": "metrics",
            "title": "Key Numbers",
            "metrics": [
                {"value": "$10B", "label": "Revenue"},
                {"value": "25%", "label": "Growth"}
            ]
        },
        {
            "type": "two_column",
            "title": "Comparison",
            "left_title": "Left Header",
            "left_bullets": ["A", "B"],
            "right_title": "Right Header",
            "right_bullets": ["C", "D"]
        },
        {
            "type": "section",
            "title": "Section Divider Title"
        },
        {
            "type": "thankyou",
            "title": "Thank you",
            "subtitle": "Questions & Discussion"
        }
    ]
}
```

### Slide Types

| Type          | Required Fields                                                    | Description                               |
|---------------|---------------------------------------------------------------------|-------------------------------------------|
| `title`       | `title`, optional `subtitle`                                       | Red bg, white text, opening slide          |
| `bullets`     | `title`, `bullets` (array of strings)                              | White bg, red accent bar, bullet list      |
| `metrics`     | `title`, `metrics` (array of `{value, label}`)                    | Gray bg, red metric boxes (2-4 recommended)|
| `two_column`  | `title`, `left_title`, `left_bullets`, `right_title`, `right_bullets` | White bg, side-by-side columns          |
| `section`     | `title`                                                            | Red bg section divider                     |
| `thankyou`    | optional `title`, optional `subtitle`                              | Red bg closing slide                       |

### Footnotes / Citations (optional on any slide)

Any slide type (except `title`, `section`, `thankyou`) can include an optional `footnotes` array. These render as small numbered hyperlinks at the bottom of the slide.

```json
{
    "type": "bullets",
    "title": "Market overview",
    "bullets": ["Global market valued at $12B", "Growing at 8% CAGR"],
    "footnotes": [
        {"label": "Grand View Research, 2025", "url": "https://example.com/report"},
        {"label": "JnJ Annual Report 2024", "url": "https://example.com/annual-report"}
    ]
}
```

Each footnote has:
- `label` — Display text for the hyperlink (e.g. source name)
- `url` — The clickable URL

## Content Guidelines

- Keep slides concise: 5-7 bullet points max per slide
- Use sentence case for titles (not ALL CAPS)
- Aim for 8-12 slides unless the user specifies otherwise
- Mix slide types for visual variety (don't use all bullets)
- If the user provides a detailed outline, follow it closely
- If the user gives only a topic, create a sensible structure
- Always offer to adjust slide count, content, or styling after generating

## Example Usage

```
/jnj-deck Q3 2024 Business Review
/jnj-deck New Product Launch Strategy
/jnj-deck Team Onboarding Overview
```
