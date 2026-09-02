"""Check Figma skill factory policy records."""
import datetime
import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlparse

from lib.factory_graph import graph

ASPECTS = {"actors", "objects", "actions", "states", "invariants", "variants",
           "interfaces", "authorities", "failures", "recoveries", "evidence",
           "time", "resources", "quality", "terminology", "exclusions"}
PRIMITIVES = {"skill_body", "references", "assets", "scripts", "tests",
              "mise_tasks", "examples", "evals", "policies", "schemas", "records"}
PHASES = {"discover", "research", "experiment", "decide", "create", "inspect",
          "update", "validate", "accept", "restore", "deprecate", "retire"}
OWNERS = {"deterministic": "mise", "model_owned": "model", "human_owned": "human"}


def read_json(root, name):
    return json.loads((root / "assets" / f"{name}.json").read_text())


def load(root):
    names = ["use-case-contract", "primitive-lifecycle", "decision-records",
             "mise-primitives-catalog", "mise-primitives", "improvement-contract"]
    values = [read_json(root, name) for name in names]
    with (root / "mise.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tasks"]
    return (*values, tasks)


def words(value):
    return re.findall(r"[a-z0-9]+", str(value).casefold())


def has_term(value, terms):
    source = words(value)
    for term in terms:
        part = words(term)
        if part and any(source[i:i + len(part)] == part
                        for i in range(len(source) - len(part) + 1)):
            return True
    return False


def text_fields(item, fields, terms, label):
    found, seen = [], []
    for field in fields:
        value = item.get(field) if isinstance(item, dict) else None
        if not isinstance(value, str) or not has_term(value, terms):
            found.append(f"{label}.{field} needs a Figma domain term")
        elif " ".join(words(value)) in seen:
            found.append(f"{label} fields repeat one claim")
        else:
            seen.append(" ".join(words(value)))
    return found


def research_time_problem(value, now):
    try:
        checked = datetime.datetime.fromisoformat(value)
        if checked.tzinfo is None:
            return "needs a time zone"
        current = checked.astimezone(datetime.timezone.utc)
        if now - current > datetime.timedelta(days=31):
            return "is not current"
        if current > now + datetime.timedelta(minutes=5):
            return "is in the future"
    except (TypeError, ValueError):
        return "needs a time zone"
    return None


def research(data, *_):
    found, sources, covered = [], [], set()
    now = datetime.datetime.now(datetime.timezone.utc)
    for index, item in enumerate(data.get("research_receipts", [])):
        label = f"research_receipts.{index}"
        source = item.get("source", "") if isinstance(item, dict) else ""
        if not urlparse(source).netloc:
            found.append(f"{label}.source needs a web URL")
        sources.append(source)
        covered.update(item.get("dimensions", []))
        time_problem = research_time_problem(item.get("checked_at"), now)
        if time_problem:
            found.append(f"{label}.checked_at {time_problem}")
    if len(sources) < 4 or len(sources) != len(set(sources)):
        found.append("Figma research needs four unique sources")
    if covered != ASPECTS:
        found.append("Figma research must cover each domain part")
    return found


def use_case(data, *_):
    found, terms = [], data.get("domain_terms", [])
    if data.get("skill") != "figma-code-connect-design-system":
        found.append("Figma skill name is wrong")
    if set(data.get("domain_dimensions", {})) != ASPECTS:
        found.append("Figma domain parts are not full")
    if set(data.get("primitive_roles", {})) != PRIMITIVES:
        found.append("Figma file parts are not full")
    fields = {"role", "outcome", "motivation", "value", "failure_prevented", "proof"}
    for name, item in data.get("primitive_roles", {}).items():
        found += text_fields(item, fields, terms, f"primitive.{name}")
        if not has_term(" ".join(map(str, item.values())), [name.replace("_", " ")]):
            found.append(f"primitive.{name} must name its Figma file part")
    return found


def actual_mise(root, catalog):
    with (root / "mise.toml").open("rb") as handle:
        config = tomllib.load(handle)
    groups = {"config": set(config) & set(catalog["groups"]["config"])}
    groups["task"] = {key for task in config["tasks"].values()
                      for key in task if key in catalog["groups"]["task"]}
    groups["task_config"] = set(config.get("task_config", {}))
    groups["tool"] = {"version"} if config.get("tools") else set()
    return groups


def mise(data, _, __, catalog, use, *___, root=None):
    found, actual = [], actual_mise(root, catalog)
    if use.get("catalog_version") != catalog.get("version"):
        found.append("Figma Mise list is old")
    for group, names in catalog["groups"].items():
        item = use.get("groups", {}).get(group, {})
        used, skipped = set(item.get("used", [])), set(item.get("not_applicable", []))
        if used | skipped != set(names) or used & skipped:
            found.append(f"Figma Mise group {group} is not full")
        if used != actual[group]:
            found.append(f"Figma Mise group {group} does not match mise.toml")
    return found


def lifecycle(data, life, _, __, ___, ____, tasks, root=None):
    found = []
    if set(life.get("required_phases", [])) != PHASES:
        found.append("Figma life steps are not full")
    if set(life.get("aspects", {})) != ASPECTS:
        found.append("Figma life parts are not full")
    if set(life.get("primitives", {})) != PRIMITIVES:
        found.append("Figma file life parts are not full")
    for name, profile in life.get("profiles", {}).items():
        if set(profile) != PHASES or not set(profile.values()) <= set(tasks):
            found.append(f"Figma life path {name} is not valid")
    return found


def decisions(data, _, records, *___):
    found, ids, terms = [], [], data.get("domain_terms", [])
    fields = {"outcome", "motivation", "why_this_path", "expected_effect",
              "proof", "falsifier", "failure_branch"}
    for index, item in enumerate(records.get("records", [])):
        ids.append(item.get("id"))
        if item.get("owner") != OWNERS.get(item.get("kind")):
            found.append(f"Figma choice {index} has the wrong owner")
        found += text_fields(item, fields, terms, f"choice.{index}")
    for field in fields:
        values = [" ".join(words(item.get(field, "")))
                  for item in records.get("records", [])]
        if len(values) != len(set(values)):
            found.append(f"Figma choice records repeat {field}")
    if len(ids) != len(set(ids)):
        found.append("Figma choice ids must not repeat")
    return found


def improvement(data, _, __, ___, ____, policy, *_____):
    found = []
    expected = {"mode": "optional_final_step", "cli_owner": "mise",
                "acceptance": "pareto_non_regression",
                "failure": "restore_last_accepted_version"}
    for key, value in expected.items():
        if policy.get(key) != value:
            found.append(f"Figma change rule {key} is wrong")
    if policy.get("trial", {}).get("change") != "one_named_dimension":
        found.append("Figma change trial must name one part")
    return found


CHECKS = {"research": research, "use-case": use_case, "mise": mise,
          "lifecycle": lifecycle, "graph": graph, "decisions": decisions,
          "improvement": improvement}
