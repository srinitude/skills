"""Route the reviewed scaffold prose into native model work units."""
import json
import re
import tomllib

from skill_package import sha
from standardization_runtime import task_header


START_RULES = ("**Start here.** Read this whole SKILL.md on every load.\n"
                  "Run `mise run rule:read` with this exact body as text.\n"
                  "Read `mise tasks info task-tools --json` for the tool and reply contract.\n"
                  "Use the same bound request and state for required tasks.")

def route_cue(name):
    return (f"- **Run `mise run {name}`.** Read its full rules in "
            "[the task file](mise.toml) before its work.")


def template_inputs(root):
    source = (root / "assets/skill-template.md").read_bytes()
    routes = json.loads((root / "assets/skill-template-routes.json").read_text())
    if routes["source_sha256"] != sha(source):
        raise ValueError("Template changed; review its complete task mapping")
    blocks = re.split(r"\n\s*\n", source.decode("utf-8"))
    owners = {entry["block"]: entry["owner"] for entry in routes["routes"]}
    if len(owners) != len(routes["routes"]):
        raise ValueError("Duplicate template block owner")
    expected = set(range(len(blocks))) - set(routes["keep"])
    if set(owners) != expected:
        raise ValueError("Template task mapping has missing or extra blocks")
    for index in routes["keep"]:
        block = blocks[index]
        if index != 0 and not block.startswith(("## ", "SCAFFOLD-PLACEHOLDER:", "[use-case-contract]:")):
            raise ValueError("Unrouted template instructions need review")
    return blocks, owners


def task_text(name, owner, paragraphs, references):
    work = "\n\n".join(paragraphs)
    used = set(re.findall(r"\[[^]\n]+\]\[([^]\n]+)\]", work))
    links = "\n".join(line for line in references.splitlines()
                      if line.split("]:", 1)[0].lstrip("[") in used)
    return (f"# `{name}`\n\n## Why this runs\n\n"
            "Keep the full skill-specific rules with their real work owner.\n\n"
            f"## When to run\n\nFollow the trigger and duties of `{owner}`.\n\n"
            "## Inputs\n\nRead this whole task, SKILL.md and the bound request.\n"
            "Use the same request and state as the required prior task.\n\n"
            f"## Work\n\n{work}\n\n{links}\n\n"
            "## Proof\n\nReturn actual evidence, reasons and remaining gaps.\n"
            "Resume this task through Mise with its exact input-bound reply.\n"
            "A workflow pass checks bindings, not meaning or human acceptance.\n")


def rule_spec(name, owner, paragraphs, references, tasks):
    parent = tasks.get(owner)
    if not parent or parent.get("run") != "node scripts/run_rule.ts " + owner:
        raise ValueError("Template requires its native rule owner: " + owner)
    if name in tasks:
        raise ValueError("Generated template task collides with an existing owner: " + name)
    return {"description": task_text(name, owner, paragraphs, references),
            "env": dict(parent["env"]), "depends": [owner],
            "run": "node scripts/run_rule.ts " + name}


def task_toml(name, spec):
    lines = [task_header(name), "description = " + json.dumps(spec["description"]),
             "depends = " + json.dumps(spec["depends"]), "run = " + json.dumps(spec["run"])]
    lines.append("env = { " + ", ".join(key + " = " + json.dumps(value)
                                      for key, value in spec["env"].items()) + " }")
    return "\n".join(lines)


def routed_template(root, tokens, mise, renderer):
    blocks, owners = template_inputs(root)
    blocks = [renderer(block.encode(), tokens).decode() for block in blocks]
    tasks = tomllib.loads(mise)["tasks"]
    groups, output, seen = {}, [], set()
    for index, block in enumerate(blocks):
        owner = owners.get(index)
        if owner is None:
            output.append(block)
            continue
        name = "rule:body-" + owner.removeprefix("rule:")
        groups.setdefault(name, (owner, []))[1].append(block)
        if name not in seen:
            output.append(route_cue(name))
            seen.add(name)
    specs = {name: rule_spec(name, owner, parts, blocks[-1], tasks)
             for name, (owner, parts) in groups.items()}
    output.insert(1, START_RULES)
    output.insert(-1, "Read the [first-run example](examples/example-first-run.md) before first use through "
                  "`mise run rule:body-examples`.\n"
                  "Use [local cases](evals/evals.json) through `mise run rule:body-eval-design`.\n"
                  "Follow each task's full rules and required checks.")
    body = "\n\n".join(output).rstrip() + "\n"
    rendered_mise = mise.rstrip() + "\n\n" + "\n\n".join(
        task_toml(name, spec) for name, spec in specs.items()) + "\n"
    return body, rendered_mise, specs


def public_rule_records(raw, specs):
    contract = json.loads(raw)
    operations = contract["task_graph"]["public_operations"]
    present = {item["task"] for item in operations}
    for name in specs:
        if name in present:
            raise ValueError("Generated template operation already exists: " + name)
        operations.append({"task": name, "outcome": "Apply this skill's full " + name + " rules.",
                           "motivation": "Keep the source rules attached to their work.",
                           "why_default_path": "Use this one native task and its required prior owner.",
                           "proof": "Fresh bound evidence and required model or human review; not an exit code alone."})
    return (json.dumps(contract, indent=2, ensure_ascii=False) + "\n").encode()


def rule_documents(root, tokens, renderer, normalizer):
    mise = renderer((root / "assets/mise-template.toml").read_bytes(), tokens).decode()
    body, mise, specs = routed_template(root, tokens, normalizer(mise), renderer)
    contract = renderer((root / "assets/use-case-contract-template.json").read_bytes(), tokens)
    return {"SKILL.md": body.encode(), "mise.toml": mise.encode(),
            "assets/use-case-contract.json": public_rule_records(contract, specs)}
