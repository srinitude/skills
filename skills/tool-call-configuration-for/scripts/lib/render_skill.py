"""Render a complete tool-specific skill from two checked profiles."""
import json
import shutil
from pathlib import Path

from common import generated_name, write_json
from render_evals import write_registry_evals


def description(tool, behavior):
    name = tool["identity"]["callable_name"]
    timing = behavior["rules"][0].get("timing", "in-scope")
    return (f"Use when configured {timing} behavior will invoke, skip, replace, wrap, "
            f"retry, resume, or handle a result from {name}. MANDATORY prerequisite: "
            f"load this skill before every in-scope {name} call and keep it active for "
            f"every configured phase. NEVER perform an in-scope {name} call without "
            "loading it. Do not trigger for mention-only text, similarly named tools, "
            "or calls outside the configured behavior.")


def rule_lines(behavior):
    lines = []
    for rule in behavior["rules"]:
        lines.append(f"- `{rule['id']}` ({rule['strength']}, {rule['timing']}): {rule['original']}")
    return lines


def safeguards(tool):
    caps = tool["contract"]["capabilities"]
    if caps.get("state_changing"):
        return [
            "- Obtain any required approval against the exact arguments before execution.",
            "- Do not retry an uncertain call until non-execution or idempotency is proved.",
            "- After success, perform an independent readback when the contract exposes one.",
            "- Preserve returned state handles and compare observed state with the requested result.",
        ]
    return [
        "- Treat the call as read-only only while the verified contract still says so.",
        "- Validate the result schema before using returned data in later work.",
        "- Retry only the failures named safe by the verified contract.",
    ]


def skill_text(source, name, tool, behavior):
    template = (source / "assets" / "generated-skill-template.md").read_text(
        encoding="utf-8")
    values = {"NAME": name, "DESCRIPTION": description(tool, behavior),
              "CALLABLE": tool["identity"]["callable_name"],
              "ORIGIN": tool["identity"]["origin_class"],
              "OWNER": tool["identity"]["provider_or_owner"],
              "RUNTIME": tool["identity"]["runtime_or_server"],
              "NAMESPACE": tool["identity"]["namespace"],
              "RULES": "\n".join(rule_lines(behavior)),
              "SAFEGUARDS": "\n".join(safeguards(tool))}
    for key, value in values.items():
        template = template.replace("%%" + key + "%%", value)
    return template


def contract_text(tool):
    identity = json.dumps(tool["identity"], indent=2, sort_keys=True)
    contract = json.dumps(tool["contract"], indent=2, sort_keys=True)
    return f"# Tool contract\n\nLoad this file before arguments, retries, cancellation, or recovery.\n\n## Identity\n\n```json\n{identity}\n```\n\n## Verified contract\n\n```json\n{contract}\n```\n"


def behavior_text(profile):
    data = json.dumps(profile, indent=2, sort_keys=True)
    return f"# Behavior profile\n\nLoad this file before every in-scope call and after any rule conflict.\n\n```json\n{data}\n```\n"


def generated_evals(name, tool, behavior):
    callable_name = tool["identity"]["callable_name"]
    original = behavior["rules"][0]["original"]
    cases = [{"id": index, "prompt": prompt, "expected_output": expected,
              "assertions": assertions} for index, prompt, expected, assertions in [
        (1, f"Use {callable_name} for one valid request.", "One configured call and verified result.", [f"The exact callable is {callable_name}.", original]),
        (2, f"Retry {callable_name} after an unknown result.", "A safety decision based on the contract.", ["Unknown execution is classified before retry."]),
        (3, f"Discuss the documentation for {callable_name} without calling it.", "No activation or call.", ["Mention-only text does not invoke the tool."]),
        (4, "Call a similarly named sibling tool.", "No activation for the sibling.", ["The exact identity is checked."]),
    ]]
    queries = [{"query": f"call {callable_name} now", "should_trigger": True},
               {"query": f"retry {callable_name} safely", "should_trigger": True},
               {"query": f"explain {callable_name} docs", "should_trigger": False},
               {"query": "call a sibling tool", "should_trigger": False}]
    return {"skill_name": name, "evals": cases}, queries


def render(root, tool, behavior, source_skill):
    name = generated_name(tool)
    target = Path(root).resolve() / name
    for part in ["references", "assets", "examples", "scripts/tests", "evals",
                 ".github/workflows"]:
        (target / part).mkdir(parents=True, exist_ok=True)
    text = skill_text(source_skill, name, tool, behavior)
    (target / "SKILL.md").write_text(text, encoding="utf-8")
    (target / "references" / "tool-contract.md").write_text(contract_text(tool), encoding="utf-8")
    (target / "references" / "behavior-profile.md").write_text(behavior_text(behavior), encoding="utf-8")
    write_json(target / "assets" / "tool-identity.json", tool["identity"])
    write_support_files(target, source_skill, name, tool, behavior)
    return target


def write_support_files(target, source, name, tool, behavior):
    for filename in ["validate_skill.py", "lint_writing.py", "check_code_rules.py",
                     "check_placeholders.py", "check_evals.py"]:
        shutil.copy(source / "scripts" / filename, target / "scripts" / filename)
    shutil.copy(source / "references" / "generation-contract.md",
                target / "references" / "generation-contract.md")
    shutil.copy(source / "assets" / "generated-mise.toml", target / "mise.toml")
    shutil.copy(source / "assets" / "generated-ci.yml", target / ".github/workflows/ci.yml")
    shutil.copy(source / "assets" / "generated-contract-test.py",
                target / "scripts/tests/test_contract.py")
    evals, queries = generated_evals(name, tool, behavior)
    write_json(target / "evals/evals.json", evals)
    write_json(target / "evals/trigger-queries.json", queries)
    write_examples(target, tool, behavior)
    write_registry_evals(target, name, tool["identity"]["callable_name"])


def write_examples(target, tool, behavior):
    callable_name = tool["identity"]["callable_name"]
    rule = behavior["rules"][0]["original"]
    help_text = f"# Example: help\n\nGuess this example removes: which exact callable and rule this skill owns.\n\n## User says\n\n```\nhelp\n```\n\n## Executor replies\n\n```\nExact callable: {callable_name}\nConfigured rule: {rule}\nEnforcement: instruction-only unless current runtime evidence proves more.\n```\n\n## Commands run\n\nNone.\n\n## Files created\n\nNone.\n\n## What the run proves\n\nThe reply names the exact identity and does not claim a runtime hook.\n"
    call_text = f"# Example: call\n\nGuess this example removes: whether a similarly named tool is allowed.\n\n## User says\n\n```\nCall {callable_name} with valid arguments.\n```\n\n## Executor replies\n\n```\nValidated the live identity and schema, applied {rule}, then classified the result.\n```\n\n## Commands run\n\nThe runtime call is host-owned and is not invented here.\n\n## Files created\n\nNone.\n\n## What the run proves\n\nThe procedure scopes behavior to one exact callable.\n"
    fail_text = f"# Example: identity failure\n\nGuess this example removes: what happens when the name resolves to more than one tool.\n\n## User says\n\n```\nCall {callable_name}.\n```\n\n## Executor replies\n\n```\nStopped: the supplied name resolves to more than one callable. Provide the origin, owner, runtime, namespace, and exact callable name.\n```\n\n## Commands run\n\nNone.\n\n## Files created\n\nNone.\n\n## What the run proves\n\nAmbiguous identity stops before a call.\n"
    (target / "examples/example-help.md").write_text(help_text, encoding="utf-8")
    (target / "examples/example-call.md").write_text(call_text, encoding="utf-8")
    (target / "examples/example-failure.md").write_text(fail_text, encoding="utf-8")
