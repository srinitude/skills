#!/usr/bin/env python3
"""Read the question files without depending on anything outside the standard library.

The question files use one fixed shape: a top level key, then a block sequence
of mappings whose scalars are double quoted and whose lists are inline. This
reader parses exactly that shape. When a full parser is installed it is used
instead, and scripts/tests/test_yamlread.py proves both paths agree.

Exit codes:
  0  the file parsed and its record count printed
  1  the file is missing
  2  usage error or a line the reader cannot parse

Examples:
  python3 scripts/yamlread.py assets/questions/accessibility.yaml
  python3 scripts/yamlread.py assets/index.yaml --key categories
"""
import argparse
import pathlib
import sys

NUMERIC = {"confidence", "count"}
NUMLIST = {"weights"}


def unquote(raw):
    """Turn one double quoted scalar into its text."""
    body = raw.strip()
    if not (body.startswith('"') and body.endswith('"')):
        return body
    out, escaped = [], False
    for char in body[1:-1]:
        if escaped:
            out.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        else:
            out.append(char)
    return "".join(out)


def scan_step(state, char):
    """Advance the inline list scanner by one character."""
    buffer, items, inside, escaped = state
    if escaped:
        return (buffer + [char], items, inside, False)
    if char == "\\":
        return (buffer, items, inside, True)
    if char == '"':
        return (buffer + [char], items, not inside, False)
    if char == "," and not inside:
        return ([], items + ["".join(buffer)], inside, False)
    return (buffer + [char], items, inside, False)


def split_items(inline):
    """Split an inline list body into its quoted items."""
    state = ([], [], False, False)
    for char in inline:
        state = scan_step(state, char)
    buffer, items = state[0], state[1]
    parts = items + ["".join(buffer)]
    return [unquote(part) for part in parts if part.strip()]


def parse_value(key, raw):
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        if key in NUMLIST:
            body = value[1:-1].strip()
            return [float(part) for part in body.split(",") if part.strip()]
        return split_items(value[1:-1])
    if key in NUMERIC:
        return float(value) if "." in value else int(value)
    return unquote(value)


def parse(text, key):
    """Return the list of mappings stored under one top level key.

    A file may hold several top level keys, so the block ends at the next
    unindented line rather than running to the end of the file.
    """
    records, current, started = [], None, False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(f"{key}:"):
            started = True
            continue
        if not started:
            continue
        if not line.startswith((" ", "\t")):
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            current = {}
            records.append(current)
            stripped = stripped[2:]
        if current is None or ":" not in stripped:
            continue
        field, _, raw = stripped.partition(":")
        current[field.strip()] = parse_value(field.strip(), raw)
    return records


def load(path, key):
    """Read one file with the installed parser when present."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        return parse(text, key)
    return yaml.safe_load(text)[key]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read one question file and report its record count.",
        epilog="exit codes: 0 parsed, 1 file missing, 2 usage error")
    parser.add_argument("path")
    parser.add_argument("--key", default="questions")
    args = parser.parse_args(argv)
    target = pathlib.Path(args.path)
    if not target.is_file():
        sys.stderr.write(f"no file at {target}\n")
        return 1
    sys.stdout.write(f"{len(load(target, args.key))}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
