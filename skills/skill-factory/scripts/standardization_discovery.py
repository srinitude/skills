"""Discover documented executable owners before rewriting a skill."""
import copy
import re
import tomllib
from pathlib import Path

from standardization_markdown import (
    BARE_SCRIPT_PATH_RE,
    FENCED_SCRIPT_PATH_RE,
    SCRIPT_LINK_RE,
    SCRIPT_RE,
)


def documented_paths(root):
    found = set()
    for markdown in root.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        found.update(match.group(1) for match in SCRIPT_RE.finditer(text))
        found.update(match.group(1) for match in SCRIPT_LINK_RE.finditer(text))
        found.update(match.group(1) for match in FENCED_SCRIPT_PATH_RE.finditer(text))
        found.update(match.group(1) for match in BARE_SCRIPT_PATH_RE.finditer(text))
    return sorted(path for path in found if path.endswith(".py")
                  and (root / "scripts" / path).is_file())


def existing_owners(root):
    with (root / "mise.toml").open("rb") as handle:
        tasks = tomllib.load(handle).get("tasks", {})
    owners = {}
    for name, task in tasks.items():
        for path in re.findall(r"scripts/([\w./-]+\.py)", str(task.get("run", ""))):
            owners[path] = name
    return owners, tasks


def task_name(path, reserved):
    parts = Path(path).with_suffix("").parts
    base = "-".join(parts).replace("_", "-")
    candidate, index = base, 2
    while candidate in reserved:
        candidate, index = f"{base}-{index}", index + 1
    return candidate


def enrich_profile(root, profile):
    result = copy.deepcopy(profile)
    specs = result.setdefault("script_tasks", {})
    public = result.setdefault("public_tasks", [])
    owners, tasks = existing_owners(root)
    reserved = set(tasks)
    reserved.update(specs)
    for name, task in tasks.items():
        expected = f"Run the {result['primary_term']} {name} operation"
        if task.get("description") == expected and name not in public:
            public.append(name)
    for path in documented_paths(root):
        owner = owners.get(path)
        if owner is None:
            owner = task_name(path, reserved)
            reserved.add(owner)
            specs[owner] = {"script": path, "runner": result.get("script_runner", "python3"),
                            "description": f"Run the {result['primary_term']} {owner} operation"}
        if owner not in public:
            public.append(owner)
    return result
