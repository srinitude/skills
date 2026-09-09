"""Create only missing baseline owners for a registry skill."""
import json
from pathlib import Path
from source_coverage import load_json, require
from standardization_mise import normalize_mise


def eval_case(item, index):
    result = dict(item)
    result.setdefault("id", item.get("source_id", f"cases:{index}"))
    if "expected_output" not in result and "decision" in item:
        result["expected_output"] = item["decision"]
    if "assertions" not in result and "required" in item:
        result["assertions"] = item["required"]
    return result


def source_cases(path):
    data = load_json(path) if path.is_file() else {"cases": []}
    require(isinstance(data, dict) and isinstance(data.get("cases"), list),
            "source cases must be an object with a cases array")
    require(all(isinstance(item, dict) for item in data["cases"]), "source case must be an object")
    return data["cases"]


def build_evals(root, profile):
    source = root / "evals/cases.json"
    return {"skill_name": profile["skill"],
            "evals": [eval_case(item, index)
                      for index, item in enumerate(source_cases(source), start=1)]}


def build_triggers(root, profile):
    source = root / "evals/trigger-cases.json"
    return [{**item, "query": item.get("query", item.get("prompt"))}
            for item in source_cases(source)]


def write_json_if_missing(path, data):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def create_missing(root, profile, factory):
    if not (root / "mise.toml").exists():
        (root / "mise.toml").write_text(normalize_mise("", profile), encoding="utf-8")
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
