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
    linked_public_route,
)


def documented_content(files):
    found = set()
    for name, raw in files.items():
        if not name.endswith(".md"):
            continue
        text = raw.decode("utf-8")
        text = SCRIPT_LINK_RE.sub(lambda match: "" if linked_public_route(text, match) else match[0], text)
        for pattern in [SCRIPT_RE, SCRIPT_LINK_RE, FENCED_SCRIPT_PATH_RE, BARE_SCRIPT_PATH_RE]:
            found.update(match.group(1) for match in pattern.finditer(text))
    return sorted(path for path in found if path.endswith(".py") and "scripts/" + path in files)


def owner_records(tasks):
    owners = {}
    for name, task in tasks.items():
        for path in re.findall(r"scripts/([\w./-]+\.py)", str(task.get("run", ""))):
            owners[path] = name
    return owners


def task_name(path, reserved):
    parts = Path(path).with_suffix("").parts
    base = "-".join(parts).replace("_", "-")
    candidate, index = base, 2
    while candidate in reserved:
        candidate, index = f"{base}-{index}", index + 1
    return candidate


def enrich_profile(root, profile):
    from skill_package import owned_paths
    files = {path.relative_to(root).as_posix(): path.read_bytes() for path in owned_paths(root)}
    return enrich_content(files, profile)


def enrich_content(files, profile):
    result = copy.deepcopy(profile)
    specs = result.setdefault("script_tasks", {})
    public = result.setdefault("public_tasks", [])
    tasks = tomllib.loads(files["mise.toml"].decode("utf-8")).get("tasks", {})
    owners = owner_records(tasks)
    reserved = set(tasks)
    reserved.update(specs)
    for name, task in tasks.items():
        expected = f"Run the {result['primary_term']} {name} operation"
        if task.get("description") == expected and name not in public:
            public.append(name)
    for path in documented_content(files):
        owner = owners.get(path)
        if owner is None:
            owner = task_name(path, reserved)
            reserved.add(owner)
            specs[owner] = {"script": path, "runner": result.get("script_runner", "python3"),
                            "description": f"Run the {result['primary_term']} {owner} operation"}
        if owner not in public:
            public.append(owner)
    return result
