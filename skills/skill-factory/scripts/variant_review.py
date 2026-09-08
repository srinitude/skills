"""Check adaptation evidence and execute the reviewed candidate's behavior cases."""
import json
import re
import subprocess
import sys
from pathlib import Path

from skill_package import content_files, inventory, real_path, tree_digest
from skill_scope import read_fields
from variant_schema import validate_review
from variant_context import check_project_review

TEXT_FIELDS = ["compatibility", "privacy_review", "independence_review"]
SECRET = re.compile(r"-----BEGIN .*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|/Users/[A-Za-z0-9_.-]+/|/home/[A-Za-z0-9_.-]+/|file://")


def check_review(plan, candidate, review):
    validate_review(review)
    source, target = plan["source"], plan["target"]
    if review.get("source_digest") != source["digest"]:
        raise ValueError("review is not bound to the source digest")
    if review.get("candidate_digest") != tree_digest(inventory(candidate)):
        raise ValueError("review is not bound to the candidate digest")
    coverage = review.get("coverage", {})
    if set(coverage) != set(source["files"]):
        raise ValueError("review must cover the complete source package")
    for item in coverage.values():
        if item.get("disposition") not in {"reviewed", "retained", "adapted", "excluded"} or not item.get("reason"):
            raise ValueError("each source file needs an adaptation disposition and reason")
    for key in TEXT_FIELDS:
        if not isinstance(review.get(key), str) or not review[key].strip():
            raise ValueError(f"review needs {key}")
    for key in ["adaptations", "requirements"]:
        if not isinstance(review.get(key), list) or not review[key] or not all(isinstance(x, str) and x.strip() for x in review[key]):
            raise ValueError(f"review needs material {key}")
    fields = read_fields(candidate)
    if fields["name"] != target["name"] or fields.get("metadata", {}).get("scope") != target["scope"]:
        raise ValueError("candidate identity or scope differs from plan")
    check_privacy(plan, candidate, review)
    check_attribution(plan, candidate)
    check_customizations(plan, candidate, review)
    check_project_review(plan, review)
    check_metadata(plan, candidate, review)


def check_metadata(plan, candidate, review):
    old = read_fields(Path(plan["source"]["root"])).get("metadata", {})
    new = read_fields(candidate).get("metadata", {})
    changed = {key for key in old if key not in {"scope", "version"} and old[key] != new.get(key)}
    if set(review.get("metadata_changes", {})) != changed:
        raise ValueError("preserve other metadata or document each necessary scope adaptation in metadata_changes")
    if "author" in changed:
        raise ValueError("preserve source author attribution in metadata")


def check_privacy(plan, candidate, review):
    forbidden = review.get("forbidden_strings", [])
    if not isinstance(forbidden, list) or not all(isinstance(x, str) and x for x in forbidden):
        raise ValueError("forbidden_strings must be a list of nonempty private markers")
    forbidden = [*forbidden, plan["source"]["root"],
                 plan["source"].get("requested_root", plan["source"]["root"]),
                 "../" + plan["source"]["name"] + "/"]
    for name in inventory(candidate):
        text = (candidate / name).read_bytes().decode("utf-8", errors="replace")
        if Path(name).name == ".env" or SECRET.search(text) or any(x in text or x in name for x in forbidden):
            raise ValueError(f"private data or hidden source dependency in {name}")
    public = json.dumps({key: review.get(key) for key in [*TEXT_FIELDS, "adaptations", "requirements", "metadata_changes"]})
    if SECRET.search(public) or any(x in public for x in forbidden):
        raise ValueError("public adaptation record contains private data")


def check_attribution(plan, candidate):
    source = Path(plan["source"]["root"])
    old, new = read_fields(source), read_fields(candidate)
    for field in ["license", "allowed-tools"]:
        if old.get(field) != new.get(field):
            raise ValueError(f"variant must preserve {field}; resolve any mandatory change first")
    for name in plan["source"]["files"]:
        if Path(name).name.upper().startswith(("LICENSE", "NOTICE", "COPYING")):
            target = candidate / name
            if not target.is_file() or target.read_bytes() != (source / name).read_bytes():
                raise ValueError(f"required license or attribution differs: {name}")


def check_customizations(plan, candidate, review):
    refresh = plan.get("refresh")
    if not refresh:
        return
    resolutions = review.get("resolutions", {})
    if set(resolutions) != set(refresh["conflicts"]) or not all(isinstance(x, str) and x.strip() for x in resolutions.values()):
        raise ValueError("resolve every refresh conflict explicitly before writing")
    current = content_files(candidate)
    for path in set(refresh["customizations"]) - set(refresh["conflicts"]):
        if current.get(path) != refresh["target_files"].get(path):
            raise ValueError(f"refresh would lose an intentional customization: {path}")


def scenario_result(candidate, scenario):
    relative = Path(scenario["script"])
    script = real_path(candidate / relative)
    if relative.is_absolute() or not script.is_relative_to(candidate / "scripts") or not script.is_file():
        raise ValueError("behavior driver must be bundled under scripts")
    project = real_path(scenario["project"])
    if not project.is_dir():
        raise ValueError("behavior project is missing")
    result = subprocess.run([sys.executable, str(script), "--project", str(project)],
                            cwd=candidate, capture_output=True, text=True, timeout=60)
    passed = (result.returncode == scenario["expected_exit"]
              and result.stdout == scenario["expected_stdout"])
    return {"id": scenario["id"], "project": str(project), "difference": scenario["difference"],
            "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
            "status": "PASS" if passed else "FAIL"}


def run_behavior(plan, candidate, review):
    cases = review.get("scenarios", [])
    required = 2 if plan["target"]["scope"] == "user" else 1
    successes = [case for case in cases if case.get("expected_exit") == 0]
    projects = {str(real_path(case["project"])) for case in successes}
    differences = {case.get("difference") for case in successes}
    if len(projects) < required or len(differences) < required or not all(differences):
        raise ValueError("behavior needs successful materially different project scenarios")
    if plan["project"] and projects != {plan["project"]["root"]}:
        raise ValueError("project variant behavior must exercise its declared project")
    results = [scenario_result(candidate, case) for case in cases]
    if any(item["status"] != "PASS" for item in results):
        raise ValueError("adapted behavior failed: " + json.dumps(results))
    return results
