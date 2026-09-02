"""Normalize one registry skill Mise graph."""
import json
import re

POLICY_TASKS = {
    "domain-research-policy": ([], "Validate current domain research receipts",
        "python3 scripts/check_domain_research.py ."),
    "use-case-policy": (["domain-research-policy"], "Validate domain-specific owners",
        "python3 scripts/check_use_case_contract.py ."),
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
    "mise-primitives-update": (["mise-latest"], "Refresh the Mise primitive catalog",
        "python3 scripts/sync_mise_primitives.py ."),
}
SECTION_RE = re.compile(r"(?m)^\[tasks\.([^]]+)\]\s*$")
NESTED_RE = re.compile(r"mise run ([a-z0-9][a-z0-9:-]*)")
DEPENDS_RE = re.compile(r"(?s)depends\s*=\s*\[(.*?)\]")
QUOTED_RE = re.compile(r'"([a-z0-9][a-z0-9:-]*)"')


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
    match = DEPENDS_RE.search(block)
    return QUOTED_RE.findall(match.group(1)) if match else []


def dependency_line(names):
    return "depends = [" + ", ".join(f'\"{name}\"' for name in names) + "]"


def normalize_existing(name, block):
    dependencies = declared_dependencies(block)
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
    return "\n".join([f"[tasks.{name}]", f'description = "{description}"',
                       f'run = "{command}"', dependency_line(depends)])


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


def normalize_mise(text, profile=None):
    preamble, existing = split_sections(text)
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
    return (preamble + "\n\n" if preamble else "") + "\n\n".join(blocks) + "\n"
