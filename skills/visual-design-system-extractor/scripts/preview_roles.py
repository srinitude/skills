"""Flatten an extraction into CSS custom properties and page roles.

Every token mapping in the document becomes one custom property, so the
rendered page carries the whole system rather than a chosen slice. Page
roles such as background, foreground, accent, and the type steps point at
those properties by name, with a literal fallback when the document leaves
a layer not applicable.
"""
from __future__ import annotations

import re

ROLE_WORDS = {
    "bg": ("paper", "background", "canvas", "surface", "base", "light"),
    "fg": ("ink", "text", "foreground", "body", "dark", "black"),
    "accent": ("accent", "brand", "primary", "action", "highlight", "signal"),
    "border": ("border", "rule", "divider", "line", "stroke", "outline"),
}
FALLBACKS = {"bg": "#ffffff", "fg": "#151515", "accent": "#151515",
             "border": "#d8d8d8"}
DARK_FALLBACKS = {"bg": "#131313", "fg": "#f2f2f2", "accent": "#f2f2f2"}
SIZE_PATTERN = re.compile(r"([0-9]*\.?[0-9]+)\s*(px|rem|em|pt)")


def flatten(node, prefix=""):
    """Return every token mapping in the document, keyed by dotted path."""
    found = {}
    if isinstance(node, dict):
        if isinstance(node.get("value"), (str, int, float)):
            found[prefix] = node
        for key, value in node.items():
            found.update(flatten(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            found.update(flatten(item, f"{prefix}.{index}"))
    return found


def css_name(path):
    """Return the custom property name for one token path."""
    return "--" + path.replace(".", "-").replace("_", "-")


def token_value(token):
    """Return the value a browser should use for one token."""
    for key in ("hex", "value"):
        value = token.get(key)
        if isinstance(value, (str, int, float)) and str(value).strip():
            return str(value).strip()
    return ""


def group_of(path):
    """Return the top level section a token path belongs to."""
    return path.split(".")[0]


def in_group(tokens, group):
    """Return the token paths inside one top level section."""
    return [path for path in tokens if group_of(path) == group]


def pick_color(tokens, role, dark=False):
    """Return the property reference for one colour role."""
    words = ROLE_WORDS[role]
    table = DARK_FALLBACKS if dark else FALLBACKS
    for path in sorted(in_group(tokens, "color_system")):
        is_dark_token = ".dark" in path or path.endswith("_dark")
        if is_dark_token == dark and any(word in path.casefold() for word in words):
            return f"var({css_name(path)}, {table.get(role, FALLBACKS[role])})"
    return table.get(role, FALLBACKS[role])


def size_of(token):
    """Return the numeric size a token declares, in px, or None."""
    match = SIZE_PATTERN.search(str(token.get("size") or token.get("value") or ""))
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2)
    return number * {"px": 1.0, "pt": 1.333, "rem": 16.0, "em": 16.0}[unit]


def sized_paths(tokens, group, inner=None):
    """Return token paths in one group that declare a size, largest first."""
    rows = []
    for path in in_group(tokens, group):
        if inner and inner not in path:
            continue
        found = size_of(tokens[path])
        if found is not None:
            rows.append((found, path))
    return [path for _, path in sorted(rows, reverse=True)]


def reference(tokens, path, fallback):
    """Return a property reference with a literal fallback."""
    return f"var({css_name(path)}, {fallback})" if path else fallback


def type_roles(tokens):
    """Return the type step roles read from the type scale, largest first."""
    steps = sized_paths(tokens, "typography", "type_scale")
    headings = steps[:4]
    rest = steps[4:] or steps[1:]
    body = next((path for path in rest if 14 <= (size_of(tokens[path]) or 0) <= 20), None)
    small = rest[-1] if rest else None
    display = reference(tokens, headings[0] if headings else None, "3rem")
    body_size = reference(tokens, body, "1rem")
    steps_out = {"--role-size-display": display, "--role-size-body": body_size,
                 "--role-size-small": reference(tokens, small,
                                                f"calc({body_size} * 0.85)")}
    for index, name in enumerate(("h2", "h3", "h4"), start=1):
        factor = (0.55, 0.38, 0.28)[index - 1]
        found = headings[index] if len(headings) > index else None
        steps_out[f"--role-size-{name}"] = reference(
            tokens, found, f"calc({display} * {factor})")
    return steps_out


def first_in(tokens, group, inner=None):
    """Return the first token path in a group, or None."""
    paths = sorted(path for path in in_group(tokens, group)
                   if not inner or inner in path)
    return paths[0] if paths else None


def space_roles(tokens):
    """Return the spacing step roles read from the spacing scale."""
    steps = sized_paths(tokens, "spacing")
    smallest = steps[-1] if steps else None
    small = reference(tokens, smallest, "8px")
    return {"--role-space-sm": small,
            "--role-space-md": f"calc({small} * 2)",
            "--role-space-lg": f"calc({small} * 4)",
            "--role-space-xl": f"calc({small} * 6)"}


def detail_roles(tokens):
    """Return radius, shadow, border, and motion roles."""
    motion = first_in(tokens, "motion")
    easing = tokens.get(motion, {}).get("easing") if motion else None
    return {
        "--role-radius": reference(tokens, first_in(tokens, "radii"), "0px"),
        "--role-shadow": reference(tokens, first_in(tokens, "shadows"), "none"),
        "--role-border-width": reference(tokens, first_in(tokens, "borders"), "1px"),
        "--role-duration": reference(tokens, motion, "200ms"),
        "--role-easing": str(easing or "ease"),
    }


def text_roles(tokens):
    """Return the weight, tracking, and leading roles."""
    return {
        "--role-weight-display": reference(
            tokens, first_in(tokens, "typography", "weights"), "600"),
        "--role-tracking-display": reference(
            tokens, first_in(tokens, "typography", "tracking"), "0em"),
        "--role-leading-display": reference(
            tokens, first_in(tokens, "typography", "leading"), "1.1"),
        "--role-leading-body": "1.55",
    }


def colour_roles(tokens):
    """Return the light and dark colour roles."""
    roles = {f"--role-{role}": pick_color(tokens, role) for role in ROLE_WORDS}
    for role in ("bg", "fg", "accent"):
        roles[f"--role-{role}-dark"] = pick_color(tokens, role, dark=True)
    return roles


def roles(tokens):
    """Return every page role the preview template consumes."""
    resolved = {}
    for part in (colour_roles(tokens), type_roles(tokens), space_roles(tokens),
                 detail_roles(tokens), text_roles(tokens)):
        resolved.update(part)
    return resolved
