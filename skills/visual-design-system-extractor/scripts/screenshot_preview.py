#!/usr/bin/env python3
"""Screenshot a rendered preview so the design system can be judged by eye.

Loads the local HTML file in a headless browser, waits for the web fonts
to load, and writes a full page PNG. Run it after scripts/render_preview.py
and then look at the PNG: the viability verdict comes from reading the
image, never from the fact that a file was produced.

Exit codes:
  0  the screenshot was written
  1  the browser or the page failed
  2  usage or input error

Example:
  uv run --no-project --with playwright python scripts/screenshot_preview.py \\
    preview.html --output preview.png --width 1280
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 900
FONT_WAIT_MS = 2500


def parse(argv):
    """Return parsed arguments for the screenshot command."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("page", help="path to the rendered HTML file")
    parser.add_argument("--output", required=True, help="PNG path to write")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--full-page", action="store_true", default=True)
    return parser.parse_args(argv)


def shoot(page_path, output, width, height, full_page):
    """Write one PNG of the local page and return the output path."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as driver:
        browser = driver.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(page_path.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(FONT_WAIT_MS)
        page.screenshot(path=output, full_page=full_page)
        browser.close()
    return output


def main(argv=None):
    args = parse(argv)
    source = Path(args.page)
    if not source.is_file():
        print(f"error: no such file: {source}", file=sys.stderr)
        return 2
    try:
        shoot(source, args.output, args.width, args.height, args.full_page)
    except ImportError:
        print("error: playwright is missing. Run: uv run --no-project --with "
              "playwright python -m playwright install chromium", file=sys.stderr)
        return 1
    except Exception as failure:  # the browser reports many failure types
        print(f"error: {failure}", file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
