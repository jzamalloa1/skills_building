#!/usr/bin/env python3
"""
JnJ Branded Markdown + HTML Document Generator
Reads a universal _research_output.json and produces:
  1. An HTML-enhanced Markdown file (.md) for developers
  2. A standalone HTML file (.html) for stakeholder sharing

Usage:
    python3 generate_markdown.py --input _research_output.json --output document.md
    # Produces: document.md AND document.html
"""

import json
import sys
import os
import re
import argparse
from datetime import date
import html as html_module

# === JnJ Brand Colors ===
JNJ_RED = "#D51900"
JNJ_DARK_RED = "#9B0600"
WHITE = "#FFFFFF"
BLACK = "#1A1A1A"
LIGHT_GRAY = "#F2F2F2"
MEDIUM_GRAY = "#6D6E71"


# ═══════════════════════════════════════════════════════════
# MARKDOWN RENDERERS
# ═══════════════════════════════════════════════════════════

def render_footnotes(footnotes: list, all_refs: list) -> str:
    if not footnotes:
        return ""
    lines = []
    lines.append("")
    lines.append(f'<div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #E0E0E0;">')
    for fn in footnotes:
        label = fn.get("label", fn["url"])
        url = fn["url"]
        ref_entry = {"label": label, "url": url}
        if ref_entry not in all_refs:
            all_refs.append(ref_entry)
        ref_num = all_refs.index(ref_entry) + 1
        lines.append(f'  <small style="color: {MEDIUM_GRAY};">[{ref_num}] <a href="{url}" style="color: #0066CC;">{label}</a></small><br/>')
    lines.append('</div>')
    lines.append('')
    return '\n'.join(lines)


def render_header(meta: dict) -> str:
    title = meta.get("title", "Untitled Document")
    subtitle = meta.get("subtitle", "")
    doc_date = meta.get("date", date.today().isoformat())
    lines = []
    lines.append(f'<div style="background: {JNJ_RED}; padding: 40px 50px; border-radius: 8px; margin-bottom: 30px;">')
    lines.append(f'  <h1 style="color: {WHITE}; margin: 0; font-family: Arial, sans-serif; font-size: 2.2em;">{title}</h1>')
    if subtitle:
        lines.append(f'  <p style="color: rgba(255,255,255,0.85); margin: 10px 0 0 0; font-family: Arial, sans-serif; font-size: 1.1em;">{subtitle}</p>')
    lines.append(f'  <p style="color: rgba(255,255,255,0.65); margin: 8px 0 0 0; font-family: Arial, sans-serif; font-size: 0.9em;">{doc_date}</p>')
    lines.append('</div>')
    lines.append('')
    return '\n'.join(lines)


def render_heading(section: dict) -> str:
    title = section["title"]
    lines = []
    lines.append("---")
    lines.append("")
    lines.append(f'<h2 style="color: {JNJ_RED}; border-left: 4px solid {JNJ_RED}; padding-left: 16px; font-family: Arial, sans-serif;">{title}</h2>')
    lines.append('')
    return '\n'.join(lines)


def render_text(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    body = section.get("body", "")
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    lines.append(body)
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_bullets(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    bullets = section.get("bullets", [])
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    for bullet in bullets:
        lines.append(f"- {bullet}")
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_metrics(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    metrics = section.get("metrics", [])
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    lines.append('<div style="display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0;">')
    for m in metrics:
        lines.append(f'  <div style="background: {JNJ_RED}; color: {WHITE}; padding: 24px 32px; border-radius: 8px; text-align: center; flex: 1; min-width: 140px;">')
        lines.append(f'    <div style="font-size: 2em; font-weight: bold; font-family: Arial, sans-serif;">{m["value"]}</div>')
        lines.append(f'    <div style="font-size: 0.85em; margin-top: 8px; opacity: 0.9; font-family: Arial, sans-serif;">{m["label"]}</div>')
        lines.append(f'  </div>')
    lines.append('</div>')
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_two_column(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    left_title = section.get("left_title", "")
    left_bullets = section.get("left_bullets", [])
    right_title = section.get("right_title", "")
    right_bullets = section.get("right_bullets", [])
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    lines.append(f'<div style="display: flex; gap: 24px; margin: 16px 0;">')
    lines.append(f'  <div style="flex: 1; background: {LIGHT_GRAY}; padding: 20px; border-radius: 8px; border-top: 3px solid {JNJ_RED};">')
    lines.append(f'    <strong style="color: {JNJ_DARK_RED}; font-family: Arial, sans-serif; font-size: 1.1em;">{left_title}</strong>')
    lines.append(f'    <ul style="color: {BLACK}; font-family: Arial, sans-serif; padding-left: 20px; margin-top: 12px;">')
    for b in left_bullets:
        lines.append(f'      <li style="margin-bottom: 6px;">{b}</li>')
    lines.append(f'    </ul>')
    lines.append(f'  </div>')
    lines.append(f'  <div style="flex: 1; background: {LIGHT_GRAY}; padding: 20px; border-radius: 8px; border-top: 3px solid {JNJ_RED};">')
    lines.append(f'    <strong style="color: {JNJ_DARK_RED}; font-family: Arial, sans-serif; font-size: 1.1em;">{right_title}</strong>')
    lines.append(f'    <ul style="color: {BLACK}; font-family: Arial, sans-serif; padding-left: 20px; margin-top: 12px;">')
    for b in right_bullets:
        lines.append(f'      <li style="margin-bottom: 6px;">{b}</li>')
    lines.append(f'    </ul>')
    lines.append(f'  </div>')
    lines.append('</div>')
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_table(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    columns = section.get("columns", [])
    rows = section.get("rows", [])
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    lines.append("| " + " | ".join(f"**{c}**" for c in columns) + " |")
    lines.append("|" + "|".join(" --- " for _ in columns) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_mermaid(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    chart = section.get("chart", "")
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    lines.append("```mermaid")
    lines.append(chart)
    lines.append("```")
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_timeline(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    events = section.get("events", [])
    footnotes = section.get("footnotes", [])
    lines = []
    if title:
        lines.append(f'### <span style="color: {JNJ_DARK_RED};">{title}</span>')
        lines.append("")
    lines.append("```mermaid")
    lines.append("timeline")
    lines.append(f"    title {title}")
    for ev in events:
        lines.append(f"    {ev['date']} : {ev['event']}")
    lines.append("```")
    lines.append("")
    lines.append('<details><summary>Timeline (text fallback)</summary>')
    lines.append("")
    for ev in events:
        lines.append(f'- **{ev["date"]}** — {ev["event"]}')
    lines.append("")
    lines.append('</details>')
    lines.append(render_footnotes(footnotes, all_refs))
    return '\n'.join(lines)


def render_references(all_refs: list) -> str:
    if not all_refs:
        return ""
    lines = []
    lines.append("---")
    lines.append("")
    lines.append(f'<h2 style="color: {JNJ_RED}; border-left: 4px solid {JNJ_RED}; padding-left: 16px; font-family: Arial, sans-serif;">References</h2>')
    lines.append("")
    for i, ref in enumerate(all_refs):
        lines.append(f'{i + 1}. [{ref["label"]}]({ref["url"]})')
    lines.append("")
    return '\n'.join(lines)


def render_footer() -> str:
    lines = []
    lines.append("---")
    lines.append("")
    lines.append(f'<div style="text-align: center; padding: 20px; color: {MEDIUM_GRAY}; font-family: Arial, sans-serif; font-size: 0.8em;">')
    lines.append(f'  <span style="color: {JNJ_RED};">&#9632;</span> Generated with JnJ Branded Markdown Generator')
    lines.append('</div>')
    return '\n'.join(lines)


RENDERERS = {
    "heading": lambda s, refs: render_heading(s),
    "text": render_text,
    "bullets": render_bullets,
    "metrics": render_metrics,
    "two_column": render_two_column,
    "table": render_table,
    "mermaid": render_mermaid,
    "timeline": render_timeline,
}


# ═══════════════════════════════════════════════════════════
# HTML RENDERERS (standalone, with Mermaid CDN)
# ═══════════════════════════════════════════════════════════

def html_escape(text: str) -> str:
    return html_module.escape(text)


def html_footnotes(footnotes: list, all_refs: list) -> str:
    if not footnotes:
        return ""
    parts = ['<div class="footnotes">']
    for fn in footnotes:
        label = fn.get("label", fn["url"])
        url = fn["url"]
        ref_entry = {"label": label, "url": url}
        if ref_entry not in all_refs:
            all_refs.append(ref_entry)
        ref_num = all_refs.index(ref_entry) + 1
        parts.append(f'  <span class="fn">[{ref_num}] <a href="{html_escape(url)}" target="_blank">{html_escape(label)}</a></span>')
    parts.append('</div>')
    return '\n'.join(parts)


def html_header(meta: dict) -> str:
    title = html_escape(meta.get("title", "Untitled Document"))
    subtitle = html_escape(meta.get("subtitle", ""))
    doc_date = meta.get("date", date.today().isoformat())
    parts = [f'<div class="hero">']
    parts.append(f'  <h1>{title}</h1>')
    if subtitle:
        parts.append(f'  <p class="subtitle">{subtitle}</p>')
    parts.append(f'  <p class="date">{doc_date}</p>')
    parts.append('</div>')
    return '\n'.join(parts)


def html_heading(section: dict) -> str:
    return f'<h2 class="section-heading">{html_escape(section["title"])}</h2>\n<hr/>'


def html_text(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    body = section.get("body", "")
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    parts.append(f'<p class="body-text">{html_escape(body)}</p>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_bullets(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    bullets = section.get("bullets", [])
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    parts.append('<ul class="bullet-list">')
    for b in bullets:
        parts.append(f'  <li>{html_escape(b)}</li>')
    parts.append('</ul>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_metrics(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    metrics = section.get("metrics", [])
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    parts.append('<div class="metrics-row">')
    for m in metrics:
        parts.append(f'  <div class="metric-card">')
        parts.append(f'    <div class="metric-value">{html_escape(m["value"])}</div>')
        parts.append(f'    <div class="metric-label">{html_escape(m["label"])}</div>')
        parts.append(f'  </div>')
    parts.append('</div>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_two_column(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    parts.append('<div class="two-col">')
    for side in ["left", "right"]:
        col_title = section.get(f"{side}_title", "")
        col_bullets = section.get(f"{side}_bullets", [])
        parts.append(f'  <div class="col">')
        parts.append(f'    <strong class="col-title">{html_escape(col_title)}</strong>')
        parts.append(f'    <ul>')
        for b in col_bullets:
            parts.append(f'      <li>{html_escape(b)}</li>')
        parts.append(f'    </ul>')
        parts.append(f'  </div>')
    parts.append('</div>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_table(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    columns = section.get("columns", [])
    rows = section.get("rows", [])
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    parts.append('<div class="table-wrap"><table>')
    parts.append('  <thead><tr>')
    for c in columns:
        parts.append(f'    <th>{html_escape(c)}</th>')
    parts.append('  </tr></thead>')
    parts.append('  <tbody>')
    for row in rows:
        parts.append('    <tr>')
        for cell in row:
            parts.append(f'      <td>{html_escape(str(cell))}</td>')
        parts.append('    </tr>')
    parts.append('  </tbody>')
    parts.append('</table></div>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_mermaid(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    chart = section.get("chart", "")
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    # Do NOT html_escape chart content — Mermaid needs raw syntax including quotes
    parts.append(f'<pre class="mermaid">\n{chart}\n</pre>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_timeline(section: dict, all_refs: list) -> str:
    title = section.get("title", "")
    events = section.get("events", [])
    footnotes = section.get("footnotes", [])
    parts = []
    if title:
        parts.append(f'<h3 class="subsection">{html_escape(title)}</h3>')
    # Mermaid timeline — do NOT html_escape, Mermaid needs raw syntax
    chart_lines = ["timeline", f"    title {title}"]
    for ev in events:
        chart_lines.append(f"    {ev['date']} : {ev['event']}")
    chart = '\n'.join(chart_lines)
    parts.append(f'<pre class="mermaid">\n{chart}\n</pre>')
    # Styled fallback list
    parts.append('<div class="timeline-list">')
    for ev in events:
        parts.append(f'  <div class="tl-item"><span class="tl-date">{html_escape(ev["date"])}</span> <span class="tl-event">{html_escape(ev["event"])}</span></div>')
    parts.append('</div>')
    parts.append(html_footnotes(footnotes, all_refs))
    return '\n'.join(parts)


def html_references(all_refs: list) -> str:
    if not all_refs:
        return ""
    parts = ['<hr/>', '<h2 class="section-heading">References</h2>', '<ol class="references">']
    for ref in all_refs:
        parts.append(f'  <li><a href="{html_escape(ref["url"])}" target="_blank">{html_escape(ref["label"])}</a></li>')
    parts.append('</ol>')
    return '\n'.join(parts)


def html_footer() -> str:
    return f'''<div class="footer">
  <span style="color: {JNJ_RED};">&#9632;</span> Generated with JnJ Branded Document Generator
</div>'''


HTML_RENDERERS = {
    "heading": lambda s, refs: html_heading(s),
    "text": html_text,
    "bullets": html_bullets,
    "metrics": html_metrics,
    "two_column": html_two_column,
    "table": html_table,
    "mermaid": html_mermaid,
    "timeline": html_timeline,
}


def generate_html(data: dict) -> str:
    """Generate a complete standalone HTML document."""
    meta = data.get("meta", {})
    sections = data.get("sections", [])
    title = html_escape(meta.get("title", "Untitled Document"))

    all_refs = []
    body_parts = []
    body_parts.append(html_header(meta))
    for section in sections:
        section_type = section.get("type", "bullets")
        renderer = HTML_RENDERERS.get(section_type)
        if not renderer:
            continue
        body_parts.append(renderer(section, all_refs))
    body_parts.append(html_references(all_refs))
    body_parts.append(html_footer())
    body_content = '\n\n'.join(body_parts)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    color: {BLACK};
    background: #FAFAFA;
    line-height: 1.6;
    padding: 0;
  }}
  .container {{
    max-width: 960px;
    margin: 40px auto;
    padding: 0 24px;
  }}
  /* Hero header */
  .hero {{
    background: {JNJ_RED};
    padding: 48px 56px;
    border-radius: 10px;
    margin-bottom: 36px;
  }}
  .hero h1 {{
    color: {WHITE};
    font-size: 2.4em;
    margin-bottom: 8px;
  }}
  .hero .subtitle {{
    color: rgba(255,255,255,0.85);
    font-size: 1.15em;
    margin-top: 8px;
  }}
  .hero .date {{
    color: rgba(255,255,255,0.6);
    font-size: 0.9em;
    margin-top: 6px;
  }}
  /* Section headings */
  hr {{
    border: none;
    border-top: 1px solid #E0E0E0;
    margin: 36px 0 16px 0;
  }}
  .section-heading {{
    color: {JNJ_RED};
    border-left: 4px solid {JNJ_RED};
    padding-left: 16px;
    font-size: 1.6em;
    margin: 12px 0 20px 0;
  }}
  .subsection {{
    color: {JNJ_DARK_RED};
    font-size: 1.25em;
    margin: 24px 0 12px 0;
  }}
  /* Body text */
  .body-text {{
    margin: 8px 0 16px 0;
    line-height: 1.75;
  }}
  /* Bullet lists */
  .bullet-list {{
    margin: 8px 0 16px 24px;
    line-height: 1.8;
  }}
  .bullet-list li {{
    margin-bottom: 6px;
  }}
  /* Metric cards */
  .metrics-row {{
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 16px 0 20px 0;
  }}
  .metric-card {{
    background: {JNJ_RED};
    color: {WHITE};
    padding: 28px 20px;
    border-radius: 10px;
    text-align: center;
    flex: 1;
    min-width: 150px;
  }}
  .metric-value {{
    font-size: 2.2em;
    font-weight: bold;
    line-height: 1.2;
  }}
  .metric-label {{
    font-size: 0.85em;
    margin-top: 10px;
    opacity: 0.9;
  }}
  /* Two-column layout */
  .two-col {{
    display: flex;
    gap: 24px;
    margin: 16px 0 20px 0;
  }}
  .two-col .col {{
    flex: 1;
    background: {LIGHT_GRAY};
    padding: 22px;
    border-radius: 8px;
    border-top: 3px solid {JNJ_RED};
  }}
  .two-col .col-title {{
    color: {JNJ_DARK_RED};
    font-size: 1.1em;
    display: block;
    margin-bottom: 10px;
  }}
  .two-col ul {{
    padding-left: 20px;
    line-height: 1.7;
  }}
  .two-col li {{
    margin-bottom: 5px;
  }}
  /* Tables */
  .table-wrap {{
    overflow-x: auto;
    margin: 12px 0 20px 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95em;
  }}
  th {{
    background: {JNJ_RED};
    color: {WHITE};
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
  }}
  td {{
    padding: 10px 16px;
    border-bottom: 1px solid #E0E0E0;
  }}
  tr:nth-child(even) td {{
    background: {LIGHT_GRAY};
  }}
  /* Mermaid diagrams */
  pre.mermaid {{
    background: {WHITE};
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 24px;
    margin: 16px 0;
    text-align: center;
  }}
  /* Mermaid text visibility overrides */
  pre.mermaid text {{
    fill: {BLACK} !important;
  }}
  /* Pie chart: slice labels on colored backgrounds need white */
  pre.mermaid .pieCircle + text,
  pre.mermaid .slice text {{
    fill: {WHITE} !important;
  }}
  /* Pie legend text must be dark */
  pre.mermaid .legend text,
  pre.mermaid .pieChart .legend text {{
    fill: {BLACK} !important;
  }}
  /* XY chart / bar chart axis and labels */
  pre.mermaid .xychart-plot text {{
    fill: {BLACK} !important;
  }}
  /* Quadrant chart labels and title */
  pre.mermaid .quadrant-point-label {{
    fill: {BLACK} !important;
  }}
  /* Timeline title and section text */
  pre.mermaid .timeline-title,
  pre.mermaid .timeline text {{
    fill: {BLACK} !important;
  }}
  /* Timeline fallback list */
  .timeline-list {{
    display: none;
    margin: 12px 0;
    padding-left: 4px;
  }}
  .tl-item {{
    padding: 8px 0;
    border-left: 3px solid {JNJ_RED};
    padding-left: 16px;
    margin-bottom: 4px;
  }}
  .tl-date {{
    font-weight: bold;
    color: {JNJ_RED};
    margin-right: 8px;
  }}
  .tl-event {{
    color: {BLACK};
  }}
  /* Footnotes */
  .footnotes {{
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid #E0E0E0;
  }}
  .fn {{
    display: block;
    font-size: 0.8em;
    color: {MEDIUM_GRAY};
    margin-bottom: 2px;
  }}
  .fn a {{
    color: #0066CC;
    text-decoration: none;
  }}
  .fn a:hover {{
    text-decoration: underline;
  }}
  /* References */
  .references {{
    padding-left: 20px;
    line-height: 2;
  }}
  .references a {{
    color: #0066CC;
    text-decoration: none;
  }}
  .references a:hover {{
    text-decoration: underline;
  }}
  /* Footer */
  .footer {{
    text-align: center;
    padding: 32px 0;
    color: {MEDIUM_GRAY};
    font-size: 0.82em;
    margin-top: 24px;
    border-top: 1px solid #E0E0E0;
  }}
  /* Responsive */
  @media (max-width: 720px) {{
    .metrics-row {{ flex-direction: column; }}
    .two-col {{ flex-direction: column; }}
    .hero {{ padding: 28px 24px; }}
    .hero h1 {{ font-size: 1.6em; }}
  }}
  /* Print */
  @media print {{
    body {{ background: white; }}
    .container {{ max-width: 100%; margin: 0; padding: 0; }}
    .hero {{ border-radius: 0; }}
    pre.mermaid {{ break-inside: avoid; }}
    .metric-card {{ break-inside: avoid; }}
  }}
</style>
</head>
<body>
<div class="container">
{body_content}
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'base',
    themeVariables: {{
      primaryColor: '{JNJ_RED}',
      primaryTextColor: '{BLACK}',
      primaryBorderColor: '{JNJ_DARK_RED}',
      lineColor: '{MEDIUM_GRAY}',
      secondaryColor: '#E85D4A',
      tertiaryColor: '#F4A261',
      quaternaryColor: '#6D6E71',
      fontFamily: 'Arial, sans-serif',
      /* Pie chart */
      pieSectionTextColor: '{WHITE}',
      pieLegendTextColor: '{BLACK}',
      pieLegendTextSize: '14px',
      pieOuterStrokeColor: '{WHITE}',
      pieStrokeWidth: '2px',
      pie1: '{JNJ_RED}',
      pie2: '#E85D4A',
      pie3: '#F4A261',
      pie4: '{MEDIUM_GRAY}',
      pie5: '{JNJ_DARK_RED}',
      pie6: '#2A9D8F',
      pie7: '#264653',
      pie8: '#E76F51',
      /* XY Chart / Bar chart */
      xyChart: {{
        titleColor: '{BLACK}',
        xAxisLabelColor: '{BLACK}',
        xAxisTitleColor: '{BLACK}',
        xAxisTickColor: '{MEDIUM_GRAY}',
        xAxisLineColor: '{MEDIUM_GRAY}',
        yAxisLabelColor: '{BLACK}',
        yAxisTitleColor: '{BLACK}',
        yAxisTickColor: '{MEDIUM_GRAY}',
        yAxisLineColor: '{MEDIUM_GRAY}',
        plotColorPalette: '{JNJ_RED}, #E85D4A, #F4A261, {MEDIUM_GRAY}, {JNJ_DARK_RED}, #2A9D8F'
      }},
      /* Quadrant chart */
      quadrant1Fill: '#FDE8E5',
      quadrant2Fill: '#E8F5E9',
      quadrant3Fill: '{LIGHT_GRAY}',
      quadrant4Fill: '#FFF3E0',
      quadrant1TextFill: '{BLACK}',
      quadrant2TextFill: '{BLACK}',
      quadrant3TextFill: '{BLACK}',
      quadrant4TextFill: '{BLACK}',
      quadrantTitleFill: '{BLACK}',
      quadrantPointFill: '{JNJ_RED}',
      quadrantPointTextFill: '{BLACK}',
      quadrantXAxisTextFill: '{BLACK}',
      quadrantYAxisTextFill: '{BLACK}',
      quadrantExternalBorderStrokeFill: '{MEDIUM_GRAY}',
      quadrantInternalBorderStrokeFill: '#E0E0E0',
      /* Timeline */
      cScale0: '{JNJ_RED}',
      cScale1: '#E85D4A',
      cScale2: '#F4A261',
      cScale3: '{MEDIUM_GRAY}',
      cScale4: '{JNJ_DARK_RED}',
      cScaleLabel0: '{WHITE}',
      cScaleLabel1: '{WHITE}',
      cScaleLabel2: '{BLACK}',
      cScaleLabel3: '{WHITE}',
      cScaleLabel4: '{WHITE}'
    }}
  }});
</script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════

def generate_markdown(data: dict) -> str:
    """Generate JnJ-branded Markdown from a research JSON dict.

    Args:
        data: Research JSON dict with 'meta' and 'sections' keys.

    Returns:
        str: The generated Markdown string.
    """
    meta = data.get("meta", {})
    sections = data.get("sections", [])

    all_refs = []
    doc_parts = []
    doc_parts.append(render_header(meta))
    for section in sections:
        section_type = section.get("type", "bullets")
        renderer = RENDERERS.get(section_type)
        if not renderer:
            print(f"Warning: Unknown section type '{section_type}', skipping.", file=sys.stderr)
            continue
        doc_parts.append(renderer(section, all_refs))
    doc_parts.append(render_references(all_refs))
    doc_parts.append(render_footer())

    return '\n'.join(doc_parts)


def render(data: dict, output_path: str | None = None) -> dict:
    """Render both Markdown and HTML from a research JSON dict.

    This is the primary entry point for importing this module as a library.

    Args:
        data: Research JSON dict with 'meta' and 'sections' keys.
        output_path: Optional path for .md file. HTML is auto-generated
                     alongside with .html extension. If None, files are
                     not written to disk — strings are only returned.

    Returns:
        dict with keys:
            'markdown': str — the Markdown content
            'html': str — the standalone HTML content
            'md_path': str | None — path written (if output_path given)
            'html_path': str | None — path written (if output_path given)
            'section_count': int
            'ref_count': int
    """
    md_output = generate_markdown(data)
    html_output = generate_html(data)
    sections = data.get("sections", [])

    md_path = None
    html_path = None

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(md_output)
        md_path = output_path

        html_path = os.path.splitext(output_path)[0] + ".html"
        with open(html_path, "w") as f:
            f.write(html_output)

    # Count refs by re-generating (lightweight — just counting)
    all_refs = []
    for section in sections:
        for fn in section.get("footnotes", []):
            ref_entry = {"label": fn.get("label", fn.get("url", "")), "url": fn.get("url", "")}
            if ref_entry not in all_refs:
                all_refs.append(ref_entry)

    return {
        "markdown": md_output,
        "html": html_output,
        "md_path": md_path,
        "html_path": html_path,
        "section_count": len(sections),
        "ref_count": len(all_refs),
    }


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate JnJ-branded Markdown + HTML documents from JSON")
    parser.add_argument("--input", "-i", required=True, help="Path to research JSON file")
    parser.add_argument("--output", "-o", required=True, help="Output .md filename (.html auto-generated alongside)")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    result = render(data, output_path=args.output)

    print(f"Markdown saved to: {result['md_path']}")
    print(f"Sections: {result['section_count']}")
    print(f"Unique sources cited: {result['ref_count']}")
    print(f"HTML saved to:     {result['html_path']}")


if __name__ == "__main__":
    main()
