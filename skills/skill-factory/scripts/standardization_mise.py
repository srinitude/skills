"""Normalize one registry skill Mise graph."""
import json
import re
import tomllib
from graphlib import TopologicalSorter
from pathlib import Path
from task_definitions import load_tasks

from check_task_graph import dependency_name, path_counts
from standardization_seed import base_mise, normalize_cache_sources

FACTORY_TASKS = load_tasks(Path(__file__).resolve().parents[1])
CI_CHECKS = tomllib.loads(base_mise({"primary_term": "skill"}))["tasks"]["ci"]["depends"]

from standardization_runtime import (MARKDOWN_TASKS, check_runtime_tasks, CATALOG_RUN, catalog_task, isolate_python_helpers, runtime_preamble,
                                     runtime_dependencies, strip_key, nested_dependencies, split_sections, split_task_body, task_header)

POLICY_TASKS = {
    "task-tools": (["check-runtime"], FACTORY_TASKS["task-tools"]["description"], "node scripts/task_tools.ts"),
    "render-file-graph": (["setup-graph-renderer"], "Prepare or render the recorded agent skill file graph", "python3 scripts/render_file_graph.py"),
    "setup-graph-renderer": (["lint-code"], "Prepare or render the recorded agent skill file graph", FACTORY_TASKS["setup-graph-renderer"]["run"]),
    "validate": ([], "Validate the current skill package and changed-output declarations",
        "uv run --with PyYAML==6.0.3 scripts/validate_skill.py . --accept"),
    "setup-runtime": ([], "Install exact locked skill code-check dependencies",
        ["npm ci --include=dev --ignore-scripts 1>&2",
         "npm ci --prefix runtime/standardization --omit=peer --ignore-scripts 1>&2"]),
    "check-runtime": (["setup-runtime"], FACTORY_TASKS["check-runtime"]["description"],
        "node scripts/runtime_gate.ts"),
    "ledger": (["check-runtime"], "Read skill ledger context or apply a caller-scoped file change through native Mastra",
        "node scripts/run_review_ledger.ts"),
    "domain-research-policy": ([], "Validate current domain research receipts",
        "python3 scripts/check_domain_research.py ."),
    "use-case-policy": (["domain-research-policy"], "Validate domain-specific owners",
        "python3 scripts/check_use_case_contract.py . --accept"),
    "mise-primitives-policy": (["use-case-policy"], "Validate Mise primitive use",
        "python3 scripts/check_mise_primitives.py ."),
    "primitive-lifecycle-policy": (["mise-primitives-policy"], "Validate lifecycle ownership",
        "python3 scripts/check_primitive_lifecycle.py ."),
    "task-graph-policy": (["primitive-lifecycle-policy"], "Validate the Mise task graph",
        "python3 scripts/check_task_graph.py ."),
    "decision-policy": (["task-graph-policy"], "Validate motivated decisions",
        "python3 scripts/check_decision_records.py ."),
    "improvement-policy": ([], "Validate nonregressing improvement trials",
        "python3 scripts/check_improvement_contract.py ."),
    "invocation-policy": ([], "Validate one task-accounting receipt",
        "python3 scripts/check_invocation_receipt.py ."),
    "agentic-request": ([], "Dispatch one typed model-owned request",
        "python3 scripts/run_agentic_request.py"),
    "mise-latest": ([], "Update Mise after accepted work",
        "mise self-update --yes --no-plugins"),
    "mise-primitives-plan": ([], "Plan exact selected-version catalog bytes without effects",
        "python3 scripts/sync_mise_primitives.py . --plan"),
    "mise-primitives-update": (["mise-latest"], "Apply a current reviewed Mise primitive catalog", CATALOG_RUN),
}
POLICY_TASKS.update({name: (task["depends"], task["description"], task["run"])
                     for name, task in MARKDOWN_TASKS.items()})

def declared_dependencies(block):
    values = tomllib.loads('[task]\n' + block)['task'].get('depends', [])
    if not isinstance(values, list):
        raise ValueError('dependencies must be an explicit array')
    for value in values:
        dependency_name(value)
    return values

def dependency_line(names):
    parts = []
    for value in names:
        dependency_name(value)
        parts.append(json.dumps(value) if isinstance(value, str) else
                     '{ ' + ', '.join(f'{key} = {json.dumps(item)}' for key, item in value.items()) + ' }')
    return 'depends = [' + ', '.join(parts) + ']'


def normalize_existing(name, block):
    if name == "mise-primitives-update":
        block = catalog_task(block)
    for checker in ["validate_skill", "check_use_case_contract"]:
        block = re.sub(rf"scripts/{checker}\.py \.(?! --accept)",
                       f"scripts/{checker}.py . --accept", block)
    dependencies = declared_dependencies(block)
    if name == "lint-code" and "check-runtime" not in dependencies:
        dependencies.append("check-runtime")
    nested = nested_dependencies(block) if name == "ci" else []
    dependencies += [item for item in nested if item not in dependencies]
    if name == "ci" and "decision-policy" not in dependencies:
        dependencies.append("decision-policy")
    result = strip_key(block, "depends")
    if nested:
        result = strip_key(result, "run")
    return normalize_cache_sources(name, "\n".join(filter(None, [result, dependency_line(dependencies)])), FACTORY_TASKS)


def policy_block(name, spec):
    depends, description, command = spec
    block = "\n".join([f'description = {json.dumps(description)}',
                         f'run = {json.dumps(command)}', dependency_line(depends)])
    if name in MARKDOWN_TASKS or name == 'check-runtime':
        block = 'env = { UV_PYTHON = "{{tools.python.path}}" }\n' + block
    if name == 'mise-primitives-update':
        block = catalog_task(block)
    return f'{task_header(name)}\n{block}'


def command_task_block(name, spec):
    return "\n".join([task_header(name),
                       f"description = {json.dumps(spec['description'])}",
                       f"run = {json.dumps(spec['run'])}", "depends = []"])


def main_task_block(profile):
    return command_task_block(profile["main_task"], {
        "description": f"Run the {profile['primary_term']} operation", "run": profile["main_run"]})


def script_task_block(name, spec):
    suffix = f" {spec['args']}" if spec.get("args") else ""
    return command_task_block(name, {"description": spec["description"],
        "run": f"{spec.get('runner', 'python3')} scripts/{spec['script']}{suffix}"})


def existing_block(name, block, profile):
    block, children = split_task_body(block)
    scripts = profile.get("script_tasks", {}) if profile else {}
    commands = profile.get("command_tasks", {}) if profile else {}
    replacement = None
    if name in scripts:
        replacement = script_task_block(name, scripts[name])
    elif name in commands:
        replacement = command_task_block(name, commands[name])
    elif profile and name == profile["main_task"] and profile.get("main_run"):
        replacement = main_task_block(profile)
    if replacement:
        before = tomllib.loads('[task]\n' + block)['task']
        desired = tomllib.loads(replacement)['tasks'][name]
        changes = [key for key in ['run', 'description'] if before.get(key) != desired[key]]
        for key in changes:
            block = strip_key(block, key) + '\n' + key + ' = ' + json.dumps(desired[key])
        expected = dict(before, run=desired['run'], description=desired['description'])
        if tomllib.loads('[task]\n' + block)['task'] != expected:
            raise ValueError('task command replacement needs explicit reconciliation: ' + name)
    return f"{task_header(name)}\n{normalize_existing(name, block)}" + ("\n" + children if children else "")


def connect_ci_checks(blocks, graph):
    for check in CI_CHECKS:
        if path_counts({name: {'depends': edges} for name, edges in graph.items()}, 'ci')[check]:
            continue
        current = tomllib.loads(blocks['ci'])['tasks']['ci']['depends']
        block, children = split_task_body(blocks['ci'])
        blocks['ci'] = strip_key(block, 'depends') + '\n' + dependency_line(current + [check])
        if children:
            blocks['ci'] += '\n' + children
        graph['ci'].append(check)


def order_runtime_tasks(text):
    preamble, sections = split_sections(text)
    tasks = tomllib.loads(text)["tasks"]
    check_runtime_tasks(tasks, POLICY_TASKS)
    blocks, graph = {}, {}
    for name, block in sections:
        block, children = split_task_body(block)
        block = isolate_python_helpers(block, tasks[name])
        dependencies = runtime_dependencies(name, tasks[name].get("depends", []), tasks)
        graph[name] = [dependency_name(value) for value in dependencies + tasks[name].get("depends_post", [])]
        if not set(graph[name]) <= set(tasks):
            raise ValueError("unknown task reading dependency: " + name)
        if dependencies != tasks[name].get("depends"):
            block = strip_key(block, "depends") + "\n" + dependency_line(dependencies)
        blocks[name] = f"{task_header(name)}\n{block}" + ("\n" + children if children else "")
    connect_ci_checks(blocks, graph)
    # Definition-reading order includes post-task definitions, not their execution order.
    ordered = [blocks[name] for name in TopologicalSorter(graph).static_order()]
    return preamble + "\n\n" + "\n\n".join(ordered) + "\n"


def normalize_mise(text, profile=None):
    preamble, existing = split_sections(text)
    preamble = runtime_preamble(preamble)
    names = {name for name, _ in existing}
    baseline = split_sections(base_mise(profile or {'primary_term': 'skill'}))[1]
    existing += [(name, block) for name, block in baseline if name not in names]
    names.update(name for name, _ in existing)
    blocks = [existing_block(name, block, profile) for name, block in existing]
    blocks += [policy_block(name, spec) for name, spec in POLICY_TASKS.items()
               if name not in names]
    if profile and profile["main_task"] not in names | set(POLICY_TASKS):
        if not profile.get("main_run"):
            raise ValueError("profile main_task needs main_run when the task is missing")
        blocks.append(main_task_block(profile))
    if profile:
        blocks += [script_task_block(name, spec)
                   for name, spec in profile.get("script_tasks", {}).items()
                   if name not in names | set(POLICY_TASKS)]
        blocks += [command_task_block(name, spec)
                   for name, spec in profile.get("command_tasks", {}).items()
                   if name not in names | set(POLICY_TASKS)]
    combined = (preamble + "\n\n" if preamble else "") + "\n\n".join(blocks) + "\n"
    return order_runtime_tasks(combined)
