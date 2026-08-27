#!/usr/bin/env python3
"""Read every skill file and report its activation or consumption route.

Exit codes:
  0  every current file has a route and every consumer exists
  1  generated, unrouted, or missing-consumer files exist
  2  the input path or policy is invalid
"""
import argparse
import ast
import fnmatch
import json
import sys
from pathlib import Path

POLICY_PATH = "assets/file-trigger-policy.json"
GENERATED_PARTS = {"__pycache__"}


def relative_files(skill):
    return sorted(
        path.relative_to(skill).as_posix()
        for path in skill.rglob("*")
        if path.is_file() and ".artifacts" not in path.parts
    )


def read_bytes(skill, paths):
    return {path: (skill / path).read_bytes() for path in paths}


def text_views(contents):
    views = {}
    for path, raw in contents.items():
        try:
            views[path] = raw.decode("utf-8")
        except UnicodeDecodeError:
            views[path] = ""
    return views


def library_modules(paths):
    return {
        path[len("scripts/"):-3].replace("/", "."): path
        for path in paths
        if path.startswith("scripts/lib/") and path.endswith(".py")
    }


def import_names(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def import_targets(name, modules):
    return [
        target for module, target in modules.items()
        if name == module or name.startswith(module + ".")
    ]


def python_import_consumers(paths, texts):
    modules = library_modules(paths)
    consumers = {path: set() for path in paths}
    for source, text in texts.items():
        if not source.endswith(".py"):
            continue
        for name in import_names(text):
            for target in import_targets(name, modules):
                consumers[target].add(source)
    return consumers


def direct_consumers(paths, texts):
    found = {path: set() for path in paths}
    for target in paths:
        for source, text in texts.items():
            if source != target and target in text:
                found[target].add(source)
    return found


def inferred_mode(path):
    if path == "SKILL.md":
        return "activate"
    if path in {"mise.toml", ".github/workflows/ci.yml"}:
        return "configure"
    if path.startswith("scripts/lib/"):
        return "import"
    if path.startswith("scripts/tests/"):
        return "discover"
    if path.startswith("scripts/"):
        return "run"
    if path.startswith("evals/files/"):
        return "fixture"
    return "load"


def discovery_route(skill, path, policy, consumers, mode, trigger):
    missing = []
    for pattern, record in policy["discovery"].items():
        if not fnmatch.fnmatch(path, pattern):
            continue
        consumer = record["consumer"]
        if not (skill / consumer).is_file():
            missing.append({"path": path, "consumer": consumer})
        else:
            consumers.add(consumer)
            mode, trigger = record["mode"], record["trigger"]
    return consumers, mode, trigger, missing


def one_route(skill, path, size, policy, consumers):
    roots = set(policy["roots"])
    mode = inferred_mode(path)
    trigger = "A named instruction, command, import, manifest, or test consumes this file."
    if path in roots:
        trigger = "The skill runtime or repository task system selects this root."
    consumers, mode, trigger, missing = discovery_route(
        skill, path, policy, consumers, mode, trigger)
    route = {"path": path, "mode": mode, "trigger": trigger,
             "consumers": sorted(consumers), "bytes_read": size}
    return route, missing, path not in roots and not consumers


def route_files(skill, policy):
    paths = relative_files(skill)
    contents = read_bytes(skill, paths)
    texts = text_views(contents)
    direct = direct_consumers(paths, texts)
    imports = python_import_consumers(paths, texts)
    routes, unrouted, missing_consumers, generated = [], [], [], []
    for path in paths:
        if GENERATED_PARTS.intersection(Path(path).parts) or path.endswith(".pyc"):
            generated.append(path)
            continue
        route, missing, no_route = one_route(
            skill, path, len(contents[path]), policy,
            set(direct[path]) | set(imports[path]))
        routes.append(route)
        missing_consumers.extend(missing)
        if no_route:
            unrouted.append(path)
    errors = bool(unrouted or missing_consumers or generated)
    return {
        "status": "FAIL" if errors else "PASS",
        "files_read": len(paths) - len(generated),
        "generated": generated,
        "unrouted": unrouted,
        "missing_consumers": missing_consumers,
        "routes": routes,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill directory to audit")
    args = parser.parse_args(argv)
    skill = Path(args.skill_dir).resolve()
    policy_path = skill / POLICY_PATH
    if not (skill / "SKILL.md").is_file() or not policy_path.is_file():
        print("error: skill root or file trigger policy is missing", file=sys.stderr)
        return 2
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        report = route_files(skill, policy)
    except (KeyError, json.JSONDecodeError, OSError) as error:
        print(f"error: invalid file trigger policy: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
