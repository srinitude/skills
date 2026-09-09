"""Normalize one registry skill Mise graph."""
import json
import re
import tomllib
from pathlib import Path

from mise_text import field, sections, table_defaults, value
from mise_task_graph import cycle, reference

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
    if name == "ci" and not any(reference(item)[0] == "decision-policy" for item in dependencies):
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
        pending.extend(reference(item)[0] for item in tasks.get(name, {}).get("depends", [])
                       if reference(item)[0] in tasks)
    return False


def wire_checks(text, defaults):
    tasks = tomllib.loads(text)["tasks"]
    for name in ["lint-code", "typecheck-native", "test-native", "test", "ci"]:
        deps = tasks[name]["depends"]
        for dependency in defaults[name]["depends"]:
            if not reaches(tasks, name, reference(dependency)[0]):
                deps.append(dependency)
    graph = {name: [reference(d)[0] for d in task["depends"] if reference(d)[0] in tasks]
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
    return wire_matrix(wire_checks(output, config["tasks"]))


def matrix_tasks(tasks):
    selected = {"domain-research-policy", "use-case-policy", "decision-policy", "evals"} & tasks.keys()
    while True:
        added = {name for name, task in tasks.items() if any(reference(item)[0] in selected
                 for field in ["depends", "depends_post"] for item in task.get(field, []))}
        if added <= selected:
            return selected
        selected.update(added)


def matrix_usage(name):
    spec = ['flag "--human-context <file>" required=#true',
            'flag "--human-context-sha256 <sha>" required=#true']
    flags = ' --human-context "$usage_human_context" --human-context-sha256 "$usage_human_context_sha256"'
    if name == "use-case-policy":
        spec.append('flag "--inspect-legacy"')
        for key in ["source", "coverage", "source-sha256", "coverage-sha256"]:
            spec.append(f'flag "--{key} <value>" default=""')
            flags += f' --{key} "$usage_{key.replace("-", "_")}"'
        flags += ' "$@"'
    if name == "evals":
        for key in ["min-cases", "min-queries"]:
            spec.append(f'flag "--{key} <value>" default="4"')
            flags += f' --{key} "$usage_{key.replace("-", "_")}"'
    return "\n".join(spec), flags


def matrix_block(name, body, task, selected):
    spec, flags = matrix_usage(name)
    if "usage" in task and task["usage"] != spec:
        raise ValueError("matrix arguments conflict with existing task usage; reconcile explicitly: " + name)
    body = field(body, "usage", value(spec))
    for key in ["depends", "depends_post"]:
        if key in task:
            deps = [matrix_dependency(item) if reference(item)[0] in selected else item for item in task[key]]
            body = field(body, key, value(deps))
    if name in {"domain-research-policy", "use-case-policy", "decision-policy", "evals"}:
        scripts = {"domain-research-policy": "check_domain_research", "use-case-policy": "check_use_case_contract",
                   "decision-policy": "check_decision_records", "evals": "check_evals"}
        command = "python3 scripts/" + scripts[name] + ".py ."
        prefix = 'set --\nif [ "${usage_inspect_legacy:-false}" = "true" ]; then set -- --inspect-legacy; fi\n' if name == "use-case-policy" else ""
        expected = prefix + command + flags
        if task.get("run") not in {command, expected} or "run_windows" in task:
            raise ValueError("matrix consumer command needs explicit integration preserving existing behavior: " + name)
        body = field(body, "run", value(expected))
    return body


def matrix_dependency(item):
    name, _ = reference(item)
    args = ["--human-context", "{{usage.human_context}}", "--human-context-sha256", "{{usage.human_context_sha256}}"]
    if isinstance(item, dict):
        if item.get("args") == args:
            return item
        raise ValueError("matrix dependency arguments need explicit integration: " + name)
    if item != name:
        raise ValueError("matrix dependency needs explicit argument migration: " + name)
    return {"task": name, "args": args}


def wire_matrix(text):
    tasks = tomllib.loads(text)["tasks"]
    selected = matrix_tasks(tasks)
    preamble, blocks = sections(text)
    rendered = [f"[tasks.{name if re.fullmatch(r'[A-Za-z0-9_-]+', name) else value(name)}]\n" + (matrix_block(name, body, tasks[name], selected)
                if name in selected else body) for name, body in blocks]
    return preamble + "\n\n" + "\n\n".join(rendered) + "\n"
