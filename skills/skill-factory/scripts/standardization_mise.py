"""Normalize one registry skill Mise graph."""
import json
import re
import tomllib
from graphlib import TopologicalSorter

from check_task_graph import dependency_name

from standardization_runtime import (CATALOG_RUN, catalog_task, isolate_python_helpers, runtime_preamble)

POLICY_TASKS = {
    "validate": ([], "Validate the current skill package and changed-output declarations",
        "uv run --with PyYAML==6.0.3 scripts/validate_skill.py . --accept"),
    "setup-runtime": ([], "Install exact locked skill code-check dependencies",
        "npm ci --include=dev --ignore-scripts 1>&2"),
    "check-runtime": (["setup-runtime"], "Type-check owned skill TypeScript",
        "npm exec --no -- tsc --noEmit --project tsconfig.json"),
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
SECTION_RE = re.compile(r"(?m)^\[tasks\.([^]]+)\]\s*$")
NESTED_RE = re.compile(r"mise run ([a-z0-9][a-z0-9:-]*)")


def split_sections(text):
    matches = list(SECTION_RE.finditer(text))
    preamble = text[:matches[0].start()] if matches else text
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[match.end():end].strip("\n")))
    return preamble.rstrip(), sections


def strip_key(block, key):
    lines, output, skipping = block.splitlines(), [], False
    for line in lines:
        if skipping:
            skipping = not line.strip().endswith("]")
            continue
        if re.match(rf"^{re.escape(key)}\s*=", line):
            skipping = "[" in line and not line.strip().endswith("]")
            continue
        output.append(line)
    return "\n".join(output).strip()


def nested_dependencies(block):
    found = []
    for name in NESTED_RE.findall(block):
        if name not in found:
            found.append(name)
    return found


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
    if name == "ci":
        dependencies += [item for item in nested_dependencies(block)
                         if item not in dependencies]
    if name == "ci" and "decision-policy" not in dependencies:
        dependencies.append("decision-policy")
    result = strip_key(strip_key(block, "run" if name == "ci" else "depends"), "depends")
    parts = [result, dependency_line(dependencies)] if result else [dependency_line(dependencies)]
    return "\n".join(parts)


def policy_block(name, spec):
    depends, description, command = spec
    block = "\n".join([f'description = {json.dumps(description)}',
                         f'run = {json.dumps(command)}', dependency_line(depends)])
    if name == 'mise-primitives-update':
        block = catalog_task(block)
    return f'[tasks.{name}]\n{block}'


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
    if name in scripts:
        return script_task_block(name, scripts[name])
    if name in commands:
        return command_task_block(name, commands[name])
    if profile and name == profile["main_task"] and profile.get("main_run"):
        return main_task_block(profile)
    return f"[tasks.{name}]\n{normalize_existing(name, block)}"



def runtime_dependencies(name, dependencies, names):
    result = list(dependencies)
    provider = {"test": "lint-code", "lint-code": "check-runtime"}.get(name)
    if provider in names and provider not in result:
        result.append(provider)
    # Remove only edges duplicated by this exact declared native preparation chain.
    if "test" in result and "lint-code" in names:
        result = [item for item in result if item not in ("lint-code", "setup-runtime", "check-runtime")]
    elif "lint-code" in result:
        result = [item for item in result if item not in ("setup-runtime", "check-runtime")]
    elif "check-runtime" in result:
        result = [item for item in result if item != "setup-runtime"]
    return result


def order_runtime_tasks(text):
    preamble, sections = split_sections(text)
    tasks = tomllib.loads(text)["tasks"]
    for name in ["setup-runtime", "check-runtime"]:
        if name in tasks and (tasks[name].get("run") != POLICY_TASKS[name][2]
                              or tasks[name].get("depends") != POLICY_TASKS[name][0]):
            raise ValueError("native runtime task needs explicit reconciliation: " + name)
    blocks, graph = {}, {}
    for name, block in sections:
        block = isolate_python_helpers(block)
        dependencies = runtime_dependencies(name, tasks[name].get("depends", []), tasks)
        graph[name] = [dependency_name(value) for value in dependencies + tasks[name].get("depends_post", [])]
        if not set(graph[name]) <= set(tasks):
            raise ValueError("unknown task reading dependency: " + name)
        if dependencies != tasks[name].get("depends"):
            block = strip_key(block, "depends") + "\n" + dependency_line(dependencies)
        blocks[name] = f"[tasks.{name}]\n{block}"
    # Definition-reading order includes post-task definitions, not their execution order.
    ordered = [blocks[name] for name in TopologicalSorter(graph).static_order()]
    return preamble + "\n\n" + "\n\n".join(ordered) + "\n"


def normalize_mise(text, profile=None):
    preamble, existing = split_sections(text)
    preamble = runtime_preamble(preamble)
    names = {name for name, _ in existing}
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
