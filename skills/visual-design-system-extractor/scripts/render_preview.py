#!/usr/bin/env python3
"""Render an extracted design system as one standalone HTML document.

The page applies every token the document defines and exercises them
across a page header, nav, hero, body copy at reading length, headings at
every level, buttons in every state, form fields, a table, a card grid, a
code block, and a footer, plus a dark section when the document declares
dark mode. Screenshot the result and judge it by eye: schema validation
proves shape, and only the rendered page proves the system works.

Exit codes:
  0  the document rendered and covers every required group
  1  a required group defines no token, so the page cannot exercise it
  2  usage or input error

Example:
  uv run --no-project --with 'PyYAML>=6,<7' python scripts/render_preview.py \\
    assets/minimal-extraction.yaml --output preview.html
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from preview_roles import css_name, flatten, in_group, roles, token_value

ASSETS = Path(__file__).resolve().parents[1] / "assets"
TEMPLATE = ASSETS / "preview-template.html"
BODY = ASSETS / "preview-body.html"
REQUIRED_GROUPS = ("color_system", "typography", "spacing", "radii", "motion")
COMPONENTS = ('data-component="page-header"', 'data-component="nav"',
              'data-component="hero"', 'data-component="body-copy"',
              'data-component="form"', 'data-component="table"',
              'data-component="card-grid"', 'data-component="code-block"',
              'data-component="footer"', "<h1>", "<h2>", "<h3>", "<h4>",
              "button[disabled]", "button:focus-visible")
FONT_URL = "https://fonts.googleapis.com/css2?family="


def coverage(tokens):
    """Return one problem per required group that defines no token."""
    return [f"{group} defines no token with a value, so the rendered page "
            "cannot exercise it" for group in REQUIRED_GROUPS
            if not in_group(tokens, group)]


def families(document):
    """Return the display, text, and mono families the document selects."""
    slot = ((document.get("typography") or {}).get("font_families") or {})
    display = (slot.get("primary") or {}).get("family") or "Georgia"
    text = (slot.get("supporting") or {}).get("family") or display
    mono = next((item.get("family") for item in slot.get("rare_unique_candidates") or []
                 if "mono" in str(item.get("classification", "")).casefold()),
                "ui-monospace")
    return {"display": display, "text": text, "mono": mono}


def rarity_of(entry):
    """Return the recorded rarity percentile of one font entry as text."""
    rarity = (entry or {}).get("rarity") or {}
    return str(rarity.get("rarity_percentile", "not recorded"))


def font_links(names):
    """Return stylesheet links for each selected Google Fonts family."""
    wanted = sorted({name for name in names
                     if name not in ("ui-monospace", "Georgia")})
    links = [f'<link rel="stylesheet" href="{FONT_URL}'
             f'{name.replace(" ", "+")}&display=swap">' for name in wanted]
    return "\n".join(links)


def var_block(tokens):
    """Return one custom property line per token."""
    return "\n".join(f"  {css_name(path)}: {token_value(tokens[path])};"
                     for path in sorted(tokens))


def role_block(tokens):
    """Return one custom property line per page role."""
    return "\n".join(f"  {name}: {value};"
                     for name, value in sorted(roles(tokens).items()))


def declares_dark(document):
    """Return True when the colour system declares a dark mode."""
    colours = document.get("color_system")
    if not isinstance(colours, dict):
        return False
    modes = [str(item).casefold() for item in colours.get("modes") or []]
    return "dark" in modes or isinstance(colours.get("dark"), dict)


def stack(names, mono=False):
    """Return the CSS font stack for one selected family."""
    tail = "ui-monospace, monospace" if mono else "Georgia, serif"
    return f'"{names}", {tail}'


def section(document, mode):
    """Return one rendered page section for the given mode."""
    names = families(document)
    slot = ((document.get("typography") or {}).get("font_families") or {})
    fills = {
        "MODE": mode,
        "BRAND": "Extracted System",
        "HEADLINE": "The rendered system, judged by eye",
        "STANDFIRST": "This page applies every token in the extraction so the "
                      "result can be screenshotted and read at real sizes.",
        "DISPLAY_FAMILY": names["display"],
        "TEXT_FAMILY": names["text"],
        "DISPLAY_RARITY": rarity_of(slot.get("primary")),
        "TEXT_RARITY": rarity_of(slot.get("supporting")),
        "EXTRACTED_AT": str((document.get("meta") or {}).get("extracted_at", "")),
    }
    text = BODY.read_text(encoding="utf-8")
    for key, value in fills.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def swatch(path):
    """Return the applied sample cell for one token."""
    name = css_name(path)
    group = path.split(".")[0]
    shapes = {
        "color_system": f'<span class="swatch" style="background: var({name})"></span>',
        "spacing": f'<span class="bar" style="width: var({name})"></span>',
        "radii": f'<span class="box" style="border-radius: var({name})"></span>',
        "shadows": f'<span class="box" style="box-shadow: var({name})"></span>',
        "motion": f'<span class="box" style="transition: opacity var({name})"></span>',
    }
    return shapes.get(group, f'<span style="font-size: var({name})">Aa</span>')


def inventory(tokens):
    """Return one inventory row per token, with the token applied."""
    return "\n".join(
        f"<tr><td>{css_name(path)}</td><td>{token_value(tokens[path])}</td>"
        f"<td>{swatch(path)}</td></tr>" for path in sorted(tokens))


def build(document):
    """Return the standalone HTML document for one extraction."""
    tokens = flatten(document)
    names = families(document)
    dark = section(document, "dark") if declares_dark(document) else ""
    parts = {
        "TITLE": "Design system viability preview",
        "FONT_LINKS": font_links(names.values()),
        "ROOT_VARS": "\n".join([var_block(tokens), role_block(tokens),
                                f'  --role-font-display: {stack(names["display"])};',
                                f'  --role-font-text: {stack(names["text"])};',
                                f'  --role-font-mono: {stack(names["mono"], True)};']),
        "LIGHT_BLOCK": section(document, "light"),
        "DARK_BLOCK": dark,
        "INVENTORY": inventory(tokens),
    }
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in parts.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def parse(argv):
    """Return parsed arguments for the renderer."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", help="path to the extraction YAML")
    parser.add_argument("--output", help="write the HTML here instead of stdout")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse(argv)
    try:
        document = yaml.safe_load(Path(args.document).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    tokens = flatten(document)
    problems = coverage(tokens)
    report = {"token_count": len(tokens), "problems": problems,
              "dark_mode": declares_dark(document),
              "output": args.output or "stdout"}
    print(json.dumps(report, indent=2, sort_keys=True))
    if problems:
        return 1
    html = build(document)
    Path(args.output).write_text(html, encoding="utf-8") if args.output else print(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
