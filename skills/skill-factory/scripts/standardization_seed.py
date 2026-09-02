"""Create only missing baseline owners for a registry skill."""
import json
from pathlib import Path

BASE_MISE = '''[tools]
python = "3.12"

[tasks.test]
description = "Run {term} contract tests"
depends = []
run = "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v"

[tasks.validate]
description = "Validate the {term} package"
depends = []
run = "uv run --with PyYAML==6.0.3 scripts/validate_skill.py ."

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


def write_json_if_missing(path, data):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def create_missing(root, profile, factory):
    if not (root / "mise.toml").exists():
        (root / "mise.toml").write_text(base_mise(profile), encoding="utf-8")
    write_json_if_missing(root / "evals/evals.json", build_evals(root, profile))
    write_json_if_missing(root / "evals/trigger-queries.json", build_triggers(root, profile))
    workflow = root / ".github/workflows/ci.yml"
    if not workflow.exists():
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_bytes((factory / "assets/ci/ci.yml").read_bytes())
    decisions = root / "references/decisions.md"
    if not decisions.exists():
        decisions.parent.mkdir(parents=True, exist_ok=True)
        decisions.write_text(f"# {profile['primary_term']} decisions\n\n"
            "Record accepted choices through `mise run decision-policy`. "
            "Return a failed claim to its smallest owner.\n", encoding="utf-8")
