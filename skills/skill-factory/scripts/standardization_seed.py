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


def eval_case(item, index, profile):
    required = item.get("required") or item.get("assertions") or []
    expected = item.get("expected_output") or item.get("decision")
    if not expected:
        expected = f"A correct {profile['primary_term']} result for this case."
    return {"id": index, "prompt": item.get("prompt", profile["outcome"]),
            "expected_output": str(expected),
            "assertions": required or [profile["outcome"]]}


def build_evals(root, profile):
    source = root / "evals/cases.json"
    data = json.loads(source.read_text()) if source.is_file() else {}
    items = data.get("cases", [])[:4]
    while len(items) < 4:
        items.append({"prompt": f"Apply {profile['primary_term']} case {len(items) + 1}."})
    return {"skill_name": profile["skill"],
            "evals": [eval_case(item, index, profile)
                      for index, item in enumerate(items, start=1)]}


def build_triggers(root, profile):
    source = root / "evals/trigger-cases.json"
    data = json.loads(source.read_text()) if source.is_file() else {}
    items = data.get("cases", [])[:8]
    queries = [{"query": item.get("prompt", ""),
                "should_trigger": bool(item.get("should_trigger"))} for item in items]
    if not any(item["should_trigger"] for item in queries):
        queries.append({"query": f"Use {profile['primary_term']} now.", "should_trigger": True})
    if not any(not item["should_trigger"] for item in queries):
        queries.append({"query": f"Explain {profile['primary_term']} history.", "should_trigger": False})
    return queries


def json_bytes(value):
    return (json.dumps(value, indent=2) + '\n').encode('utf-8')

def seeds(root, files, profile, factory):
    files.setdefault('mise.toml', base_mise(profile).encode())
    files.setdefault('evals/evals.json', json_bytes(build_evals(root, profile)))
    files.setdefault('evals/trigger-queries.json', json_bytes(build_triggers(root, profile)))
    files.setdefault('.github/workflows/ci.yml', (factory / 'assets/ci/ci.yml').read_bytes())
    files.setdefault('references/decisions.md', (
        f"# {profile['primary_term']} decisions\n\n"
        'Record accepted choices through `mise run decision-policy`. '
        'Return a failed claim to its smallest owner.\n').encode())
