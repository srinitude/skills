"""Normalize one registry skill Mise graph."""
import json
import re
import tomllib
from pathlib import Path

from mise_text import field, sections, table_defaults, value
from mise_task_graph import cycle

BARE_MISE = re.compile(r"mise run ([a-z0-9][a-z0-9:-]*)")
NATIVE_CHAIN = {"runtime-install", "lint-code", "typecheck-native", "test-native"}


def migrate_call(block, task, dependencies):
    commands = task.get("run", [])
    commands = [commands] if isinstance(commands, str) else commands
    if not any(isinstance(cmd, str) and "mise run" in cmd for cmd in commands):
        return block, dependencies
    match = BARE_MISE.fullmatch(commands[0]) if len(commands) == 1 else None
    execution = set(task) - {"run", "depends", "description", "alias"}
    if not match or dependencies or execution:
        raise ValueError("nested Mise call needs an explicit task migration preserving arguments, order and environment")
    return field(block, "run", None), [match[1]]


def normalize_existing(name, block):
    block = re.sub(r"scripts/validate_skill\.py \.(?! --accept)",
                   "scripts/validate_skill.py . --accept", block)
    task = tomllib.loads(block)
    dependencies = task.get("depends", [])
    if not isinstance(dependencies, list):
        raise ValueError(f"tasks.{name}.depends needs an explicit array migration")
    block, dependencies = migrate_call(block, task, dependencies)
    if name == "ci" and "decision-policy" not in dependencies:
        dependencies.append("decision-policy")
    return field(block, "depends", value(dependencies))


def template(profile):
    path = Path(__file__).resolve().parents[1] / "assets/mise-template.toml"
    name = (profile or {}).get("skill", "skill")
    text = path.read_text().replace("{{NAME}}", json.dumps(name)[1:-1])
    config = tomllib.loads(text)
    _, blocks = sections(text)
    return config, {name: body for name, body in blocks if name != "info"}


def reaches(tasks, start, target):
    seen, pending = set(), [start]
    while pending:
        name = pending.pop()
        if name == target:
            return True
        if name in seen:
            continue
        seen.add(name)
        pending.extend(item for item in tasks.get(name, {}).get("depends", [])
                       if isinstance(item, str) and item in tasks)
    return False


def wire_checks(text, defaults):
    tasks = tomllib.loads(text)["tasks"]
    for name in ["lint-code", "typecheck-native", "test-native", "test", "ci"]:
        deps = tasks[name]["depends"]
        for dependency in defaults[name]["depends"]:
            if not reaches(tasks, name, dependency):
                deps.append(dependency)
    graph = {name: [d for d in task["depends"] if isinstance(d, str) and d in tasks]
             for name, task in tasks.items()}
    if cycle(graph):
        raise ValueError("native prerequisites conflict with existing order; reconcile the task cycle explicitly")
    preamble, blocks = sections(text)
    result = []
    for name, body in blocks:
        deps = tasks[name]["depends"]
        kept = [item for item in deps if not (isinstance(item, str) and item in NATIVE_CHAIN
                and any(isinstance(other, str) and other != item and reaches(tasks, other, item)
                        for other in deps))]
        key = name if re.fullmatch(r"[A-Za-z0-9_-]+", name) else json.dumps(name)
        result.append(f"[tasks.{key}]\n{field(body, 'depends', value(kept))}")
    return preamble + "\n\n" + "\n\n".join(result) + "\n"


def main_task_block(profile):
    name = profile["main_task"]
    description = f"Run the {profile['primary_term']} operation"
    command = json.dumps(profile["main_run"])
    return "\n".join([f"[tasks.{name}]", f'description = "{description}"',
                       f"run = {command}", "depends = []"])


def script_task_block(name, spec):
    suffix = f" {spec['args']}" if spec.get("args") else ""
    runner = spec.get("runner", "python3")
    command = json.dumps(f"{runner} scripts/{spec['script']}{suffix}")
    description = json.dumps(spec["description"])
    return "\n".join([f"[tasks.{name}]", f"description = {description}",
                       f"run = {command}", "depends = []"])


def command_task_block(name, spec):
    return "\n".join([f"[tasks.{name}]",
                       f"description = {json.dumps(spec['description'])}",
                       f"run = {json.dumps(spec['run'])}", "depends = []"])


def existing_block(name, block, profile):
    scripts = profile.get("script_tasks", {}) if profile else {}
    commands = profile.get("command_tasks", {}) if profile else {}
    replacement = None
    if name in scripts:
        replacement = script_task_block(name, scripts[name])
    elif name in commands:
        replacement = command_task_block(name, commands[name])
    elif profile and name == profile["main_task"] and profile.get("main_run"):
        block = field(block, "run", value(profile["main_run"]))
    if replacement:
        updates = tomllib.loads(replacement)["tasks"][name]
        for key in ["description", "run"]:
            block = field(block, key, value(updates[key]))
    key = name if re.fullmatch(r"[A-Za-z0-9_-]+", name) else json.dumps(name)
    return f"[tasks.{key}]\n{normalize_existing(name, block)}"


def normalize_mise(text, profile=None):
    config, defaults = template(profile)
    text = table_defaults(text, "tools", config["tools"])
    preamble, existing = sections(text)
    names = {name for name, _ in existing}
    blocks = [existing_block(name, block, profile) for name, block in existing]
    blocks += [f"[tasks.{name}]\n{body}" for name, body in defaults.items()
               if name not in names]
    if profile and profile["main_task"] not in names | set(defaults):
        if not profile.get("main_run"):
            raise ValueError("profile main_task needs main_run when the task is missing")
        blocks.append(main_task_block(profile))
    if profile:
        blocks += [script_task_block(name, spec)
                   for name, spec in profile.get("script_tasks", {}).items()
                   if name not in names | set(defaults)]
        blocks += [command_task_block(name, spec)
                   for name, spec in profile.get("command_tasks", {}).items()
                   if name not in names | set(defaults)]
    output = (preamble + "\n\n" if preamble else "") + "\n\n".join(blocks) + "\n"
    return wire_checks(output, config["tasks"])
