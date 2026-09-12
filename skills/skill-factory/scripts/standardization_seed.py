"""Seed and reconcile baseline owners for a registry skill."""
import json
import re
import tomllib
from pathlib import Path

BASE_MISE = '''[tools]
python = "3.11.15"
uv = "0.11.29"

[tasks.test]
description = "Run {term} contract tests"
depends = []
run = "uv run --with PyYAML==6.0.3 python -m unittest discover -s scripts/tests -p 'test_*.py' -v --failfast"

[tasks.validate]
description = "Validate the {term} package"
depends = []
run = "uv run --with PyYAML==6.0.3 scripts/validate_skill.py . --accept"

[tasks.lint-writing]
description = "Check {term} Markdown"
depends = []
run = "python3 scripts/lint_writing.py ."

[tasks.lint-code]
description = "Check {term} code limits"
depends = []
run = "python3 scripts/check_code_rules.py ."

[tasks.lint-placeholders]
description = "Reject {term} placeholders"
depends = []
run = "python3 scripts/check_placeholders.py ."

[tasks.evals]
description = "Validate {term} behavior cases"
depends = []
run = "python3 scripts/check_evals.py ."

[tasks.ci]
description = "Run the complete {term} gate"
depends = ["test", "validate", "lint-writing", "lint-code", "lint-placeholders", "evals"]
'''


def base_mise(profile):
    return BASE_MISE.format(term=profile["primary_term"])


def draft(profile, detail):
    return f"SCAFFOLD-PLACEHOLDER {profile['primary_term']}: {detail}"


def eval_case(item, index, profile):
    required = item.get("required") or item.get("assertions") or []
    expected = item.get("expected_output") or item.get("decision")
    if not expected:
        expected = draft(profile, "state the observable expected output.")
    return {"id": index, "prompt": item.get("prompt", draft(profile, "supply a realistic domain request.")),
            "expected_output": str(expected),
            "assertions": required or [draft(profile, "state a verifiable assertion.")]}


def build_evals(root, profile):
    source = root / "evals/cases.json"
    data = json.loads(source.read_text()) if source.is_file() else {}
    items = data.get("cases", [])
    while len(items) < 4:
        items.append({"prompt": draft(profile, f"author domain case {len(items) + 1}.")})
    return {"skill_name": profile["skill"],
            "evals": [eval_case(item, index, profile)
                      for index, item in enumerate(items, start=1)]}


def build_triggers(root, profile):
    source = root / "evals/trigger-cases.json"
    data = json.loads(source.read_text()) if source.is_file() else {}
    items = data.get("cases", [])
    queries = [{"query": item.get("prompt", ""),
                "should_trigger": item.get("should_trigger")} for item in items]
    for detail, label in [
        ("author a real activating request.", True),
        ("author a second activating request with a file path.", True),
        ("author a near miss sharing domain terms.", False),
        ("author an unrelated request.", False),
    ]:
        if len(queries) < 4 or not any(item["should_trigger"] is label for item in queries):
            queries.append({"query": draft(profile, detail), "should_trigger": label})
    return queries


def json_bytes(value):
    return (json.dumps(value, indent=2) + '\n').encode('utf-8')

def seeds(root, files, profile, factory):
    files.setdefault('mise.toml', base_mise(profile).encode())
    for name, build in [('evals/evals.json', build_evals),
                        ('evals/trigger-queries.json', build_triggers)]:
        if name not in files:
            files[name] = json_bytes(build(root, profile))
    files.setdefault('.github/workflows/ci.yml', (factory / 'assets/ci/ci.yml').read_bytes())
    files.setdefault('references/decisions.md', (
        f"# {profile['primary_term']} decisions\n\n"
        'Record accepted choices through `mise run decision-policy`. '
        'Return a failed claim to its smallest owner.\n').encode())


def graph_task_records(term):
    return {
        "setup-graph-renderer": {
            "outcome": f"Prepare the locked browser for the {term} skill file graph.",
            "motivation": f"The {term} package cannot depend on an ambient browser.",
            "value": f"Install the browser selected by the locked {term} renderer before its tests and graph rendering.",
            "proof": f"The {term} renderer actually starts and renders its graph; installation alone proves no readability or domain result.",
            "applicability": f"Before {term} graph rendering or renderer tests, with authorized network access and a supported platform."},
        "render-file-graph": {
            "outcome": f"Render every recorded {term} skill file node and connector into a bound SVG.",
            "motivation": f"An incomplete {term} maintenance graph can hide a missing file or relationship.",
            "value": f"Verify the bound {term} native ledger result, retain original records, refuse overwrites and check exact SVG topology.",
            "proof": f"Actual {term} renderer tests reject modified inputs, omissions and duplicates and reproduce parallel/self-loop SVGs. Review live inventory and readable pixels separately.",
            "applicability": f"After a current {term} native ledger file-graph capture; supply its path, new output directory, SHA-256 and positive timeout."}}


def markdown_task_records(term):
    roles = {
        'inventory': ('Read and bind each Markdown file and all review inputs.', 'Require a complete file inventory and exact input identities.'),
        'mechanical': ('Report parse, size, reading-level, link and layout findings.', 'Require findings tied to each full file; early quality failures stay visible.'),
        'review-request': ('Give the model the whole file, source rules and current findings.', 'Require full bound text and explicit questions before model review.'),
        'macro-review': ('Judge whole-file purpose, coverage, order and form choices.', 'Require a current model reply with reasons and cited source evidence.'),
        'micro-review': ('Judge sections, blocks, preserved rules and rendered form.', 'Require whole-file review first and a bound render for direct inspection.'),
        'line-review': ('Judge simple language, exact terms and honest score exclusions.', 'Require section review first; do not trade a rule for a low reading score.'),
        'review-check': ('Check all model review stages and mechanical findings together.', 'Reject failed findings, missing stages, stale inputs and unsupported citations.'),
        'accept': ('Close the writing checks while retaining other acceptance duties.', 'Require the full chain; keep real human and domain acceptance separate.'),
    }
    return {f"markdown:{phase}": {
        "outcome": f"For the {term} skill package: {role}",
        "motivation": f"The {term} reader needs clear instructions with no missing rule or proof.",
        "value": f"Use the {term} {phase} findings before the next dependent writing step.",
        "proof": f"For the {term} skill package: {proof}",
        "applicability": f"For each existing, new or generated {term} Markdown file; preserve required human review.",
    } for phase, (role, proof) in roles.items()}


def task_records(profile, tasks):
    term = profile["primary_term"]
    records = {name: {
        "outcome": f"Advance the {term} result through {name}.",
        "motivation": f"The {term} package needs the {name} gate.",
        "value": f"Produce current {term} evidence from {name}.",
        "proof": f"The {term} {name} task exits zero with readable output.",
        "applicability": f"Use {name} for its declared {term} responsibility.",
    } for name in tasks}

    records.update({name: row for name, row in (graph_task_records(term) | markdown_task_records(term)).items() if name in tasks})
    return records


def operations(profile, tasks):
    candidates = [profile["main_task"], "invocation-policy", "agentic-request",
                  "improvement-policy", "mise-primitives-plan", "mise-primitives-update", "ledger", "render-file-graph", "markdown:accept"]
    candidates += profile.get("public_tasks", [])
    candidates = list(dict.fromkeys(candidates))
    term = profile["primary_term"]
    records = [{"task": name, "outcome": f"Produce the named {term} {name} result.",
             "motivation": f"The {term} workflow needs one {name} entry.",
             "why_default_path": f"This is the single declared {term} {name} route.",
             "proof": f"Fresh {term} {name} output and exit status."}
            for name in candidates if name in tasks]

    for row in records:
        if row["task"] in {"render-file-graph", "markdown:accept"}:
            detail = (graph_task_records(term) | markdown_task_records(term))[row["task"]]
            row.update({key: detail[key] for key in ["outcome", "motivation", "proof"]})
    return records


def normalize_cache_sources(name, block, canonical):
    owners = {"lint-writing": "lint_writing", "lint-placeholders": "check_placeholders"}
    if name not in owners:
        return block
    task = tomllib.loads("[task]\n" + block)["task"]
    desired = canonical[name]["sources"]
    if task.get("sources") in (None, desired):
        return block
    legacy = ["**/*.md"] + (["**/*.json"] if name == "lint-placeholders" else [])
    legacy.append("scripts/" + owners[name] + ".py")
    if task["sources"] != legacy:
        raise ValueError("cache sources need explicit reconciliation: " + name)
    pattern = r"(?m)^(sources\s*=\s*)\[[^\n]*?\]([ \t]*(?:#[^\n]*)?)$"
    result, count = re.subn(pattern, lambda match: match[1] + json.dumps(desired) + match[2], block)
    expected = dict(task, sources=desired)
    if count != 1 or tomllib.loads("[task]\n" + result)["task"] != expected:
        raise ValueError("cache sources need explicit reconciliation: " + name)
    return result
