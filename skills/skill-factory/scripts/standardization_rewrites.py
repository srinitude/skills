"""Apply reviewed, profile-bound text migrations."""
from pathlib import Path


def safe_target(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"unsafe text rewrite path: {relative}")
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"text rewrite leaves target: {relative}")
    if not path.is_file():
        raise ValueError(f"text rewrite target is missing: {relative}")
    return path


def terminal_replacement(value, remaining):
    terminal = value
    for rule in remaining:
        if rule["old"] == terminal:
            terminal = rule["new"]
    return terminal


def apply_rule(text, rule, remaining, relative, strict):
    old, new = rule["old"], rule["new"]
    if old in text or new in text:
        return text.replace(old, new)
    if terminal_replacement(new, remaining) in text:
        return text
    if not strict:
        return text
    raise ValueError(f"text rewrite source is missing: {relative}")


def apply_rewrites(root, profile, strict=True):
    for relative, rules in profile.get("text_rewrites", {}).items():
        path = safe_target(root, relative)
        text = path.read_text(encoding="utf-8")
        path.write_text(rewritten_text(text, rules, relative, strict), encoding="utf-8")


def rewritten_text(text, rules, relative, strict=True):
    for index, rule in enumerate(rules):
        text = apply_rule(text, rule, rules[index + 1:], relative, strict)
    return text


def apply_section_rewrites(root, profile):
    for rule in profile.get("section_rewrites", []):
        path = safe_target(root, rule["path"])
        text = path.read_text(encoding="utf-8")
        updated = rewritten_section(text, rule)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def rewritten_section(text, rule):
    replacement = rule["replacement"].rstrip() + "\n\n"
    if replacement in text:
        return text
    start = text.find(rule["heading"] + "\n")
    end = text.find(rule["until"] + "\n", start + 1)
    if start < 0 or end < 0:
        raise ValueError(f"section rewrite boundary is missing: {rule['path']}")
    return text[:start] + replacement + text[end:]
