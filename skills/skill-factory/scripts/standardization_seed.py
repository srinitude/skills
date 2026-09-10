"""Create only missing baseline owners for a registry skill."""
import json
from pathlib import Path

BASE_MISE = '''[tools]
python = "3.11.15"
uv = "0.11.29"

[tasks.test]
description = "Run {term} contract tests"
depends = []
run = "uv run --with PyYAML==6.0.3 python -m unittest discover -s scripts/tests -p 'test_*.py' -v"

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
