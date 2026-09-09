"""Read and validate one registry-skill domain profile."""
import json
from pathlib import Path

DIMENSIONS = [
    "actors", "objects", "actions", "states", "invariants", "variants",
    "interfaces", "authorities", "failures", "recoveries", "evidence",
    "time", "resources", "quality", "terminology", "exclusions",
]
PRIMITIVES = [
    "skill_body", "references", "assets", "scripts", "tests", "mise_tasks",
    "examples", "evals", "policies", "schemas", "records",
]
PHASES = [
    "discover", "research", "experiment", "decide", "create", "inspect",
    "update", "validate", "accept", "restore", "deprecate", "retire",
]


def load_profile(path, skill=None):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"profile cannot be read: {error}") from error
    if "profiles" in data:
        if not skill or skill not in data["profiles"]:
            raise ValueError(f"profile set has no entry for {skill}")
        return data["profiles"][skill]
    return data


def text(value):
    return isinstance(value, str) and bool(value.strip())


def profile_problems(data):
    found = []
    for field in ["skill", "primary_term", "outcome", "main_task"]:
        if not text(data.get(field)):
            found.append(f"{field} must be nonempty text")
    terms = data.get("domain_terms", [])
    if not isinstance(terms, list) or len(terms) < 3 or not all(map(text, terms)):
        found.append("domain_terms needs three nonempty phrases")
    sources = data.get("sources", [])
    if not isinstance(sources, list) or len(sources) < 4:
        found.append("sources needs four current records")
    else:
        found += source_problems(sources)
    if "main_run" in data and not text(data["main_run"]):
        found.append("main_run must be nonempty text when present")
    found += public_task_problems(data.get("public_tasks", []))
    found += script_task_problems(data.get("script_tasks", {}))
    found += command_task_problems(data.get("command_tasks", {}))
    found += line_route_problems(data.get("line_task_routes", []))
    found += rewrite_problems(data.get("text_rewrites", {}))
    return found


def public_task_problems(tasks):
    if not isinstance(tasks, list) or not all(map(text, tasks)):
        return ["public_tasks must be an array of task names"]
    return []


def script_task_problems(tasks):
    if not isinstance(tasks, dict):
        return ["script_tasks must be an object"]
    found = []
    for name, item in tasks.items():
        valid = (text(name) and isinstance(item, dict)
                 and text(item.get("script")) and text(item.get("description")))
        if not valid or Path(str(item.get("script", ""))).name != item.get("script"):
            found.append(f"script_tasks.{name} is invalid")
        if "args" in item and not text(item["args"]):
            found.append(f"script_tasks.{name}.args must be nonempty text")
        if "runner" in item and not text(item["runner"]):
            found.append(f"script_tasks.{name}.runner must be nonempty text")
    return found


def command_task_problems(tasks):
    if not isinstance(tasks, dict):
        return ["command_tasks must be an object"]
    found = []
    for name, item in tasks.items():
        valid = (text(name) and isinstance(item, dict)
                 and text(item.get("run")) and text(item.get("description")))
        if not valid:
            found.append(f"command_tasks.{name} is invalid")
    return found


def line_route_problems(routes):
    if not isinstance(routes, list):
        return ["line_task_routes must be an array"]
    found = []
    for index, item in enumerate(routes):
        valid = (isinstance(item, dict) and text(item.get("contains"))
                 and isinstance(item.get("tasks"), list)
                 and bool(item["tasks"]) and all(map(text, item["tasks"])))
        if not valid:
            found.append(f"line_task_routes.{index} is invalid")
    return found


def rewrite_problems(rewrites):
    if not isinstance(rewrites, dict):
        return ["text_rewrites must be an object"]
    found = []
    for path, rules in rewrites.items():
        if not text(path) or not isinstance(rules, list) or not rules:
            found.append("text_rewrites entries need a path and rules")
            continue
        for rule in rules:
            valid = (isinstance(rule, dict) and text(rule.get("old"))
                     and isinstance(rule.get("new"), str))
            if not valid:
                found.append(f"text_rewrites.{path} has an invalid rule")
    return found


def source_problems(sources):
    found = []
    required = {"source", "source_class", "claim", "limitations"}
    for index, item in enumerate(sources):
        if not isinstance(item, dict) or not required <= set(item):
            found.append(f"sources.{index} is incomplete")
            continue
        if not all(text(item[field]) for field in required):
            found.append(f"sources.{index} has blank fields")
    return found


def validate_profile(data, target):
    found = profile_problems(data)
    if data.get("skill") != target.name:
        found.append("profile skill must match the target directory")
    if found:
        raise ValueError("; ".join(found))
    return data
