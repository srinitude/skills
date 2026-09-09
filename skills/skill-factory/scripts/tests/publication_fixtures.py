"""Real task-listing evidence for disposable consumer tests, not skill acceptance."""
import json
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path

from acceptance_fixtures import coverage, write_json
from cli import run
from skill_package import inventory, tree_digest
from skill_scope import read_fields
from test_acceptance_bindings import digest

CLAUSES = (b"List declared tasks.", b"Preserve package files.")
SOURCE = b"# Mechanical test only\n" + b" ".join(CLAUSES) + b"\n"


def inspect(root):
    before = inventory(root)
    expected = set(tomllib.loads((root / "mise.toml").read_text())["tasks"])
    argv = ["mise", "tasks", "--json"]
    result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    names = {task["name"] for task in json.loads(result.stdout)}
    return {"execution": {"argv": argv, "exit_code": result.returncode,
                          "stdout": result.stdout, "stderr": result.stderr},
            "declared_tasks_found": expected <= names, "preserved": inventory(root) == before}


def context(base, root, expected, result):
    (base / "source.md").write_bytes(SOURCE)
    source = {"path": str(base / "source.md"), "sha256": digest(SOURCE)}
    coverage_sha = write_json(base / "coverage.json", coverage(SOURCE, CLAUSES))
    metadata = read_fields(root)["metadata"]
    audience = json.loads((root / "assets/use-case-contract.json").read_text())["audience"]["primary"]
    rule = {"components": ["ROW-2-C1", "ROW-2-C2"], "applicability": "applicable",
            "producer": {"kind": "mechanical", "id": "disposable-task-listing"},
            "command": result["execution"]["argv"], "process_exit": 0,
            "criteria": [{"path": ["declared_tasks_found"], "equals": True},
                         {"path": ["preserved"], "equals": True}]}
    return {"version": 1, "source": source, "coverage": {"path": str(base / "coverage.json"), "sha256": coverage_sha},
            "subject": {"skill": root.name, "scope": metadata["scope"], "audience": audience,
                        "revision": "disposable-consumer-test", "sha256": tree_digest(inventory(root))},
            "operation": "inspect declared task listing", "consumer": expected,
            "dependencies": {"graph": {"path": str(root / "mise.toml"), "sha256": digest((root / "mise.toml").read_bytes())}},
            "requirements": {"ROW-2": rule}, "evidence_root": str(base),
            "validity": {"not_before": int(time.time()) - 60, "expires_at": int(time.time()) + 3600}}


def evidence(base, root, expected):
    result = inspect(root)
    spec = context(base, root, expected, result)
    context_sha = write_json(base / "context.json", spec)
    artifact = {**result, "context_sha256": context_sha, "requirement": "ROW-2",
                "components": spec["requirements"]["ROW-2"]["components"],
                "producer": spec["requirements"]["ROW-2"]["producer"],
                "run_id": "disposable-task-listing", "state": "passed",
                "judgment": {"basis": "Native task listing contains the declared tasks; owned package files are unchanged.",
                             "limits": "Mechanical bootstrap fixture only. No domain, semantic, human or whole-goal acceptance."}}
    artifact_sha = write_json(base / "evidence.json", artifact)
    receipt = {"skill": root.name, "operation": spec["operation"], "entries": [],
               "acceptance": {"context_sha256": context_sha, "subject": spec["subject"],
                              "claims": {"ROW-2": {"path": "evidence.json", "sha256": artifact_sha}}}}
    receipt_sha = write_json(base / "receipt.json", receipt)
    return ["--acceptance-context", base / "context.json", "--context-sha256", context_sha,
            "--receipt", base / "receipt.json", "--receipt-sha256", receipt_sha]


def standardize(*args, **kwargs):
    if "--apply" not in args:
        return run("standardize_registry_skill.py", *args, **kwargs)
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp).resolve()
        root = Path(args[0]).resolve()
        prepared = base / "candidate" / root.name
        prepare_args = [arg for arg in args if arg != "--apply"]
        result = run("standardize_registry_skill.py", *prepare_args, "--prepare", prepared, **kwargs)
        if result.returncode:
            return result
        expected = {"route": "standardize-target", "target": str(root),
                    "inputs": json.loads(result.stdout)["consumer_inputs"]}
        flags = evidence(base, prepared, expected)
        apply_args = [arg for arg in args if arg != "--rebase-tracked-text"]
        return run("standardize_registry_skill.py", *apply_args, "--candidate", prepared, *flags, **kwargs)


def variant(*args, **kwargs):
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp).resolve()
        plan = json.loads(Path(args[args.index("--plan") + 1]).read_text())
        review = json.loads(Path(args[args.index("--review") + 1]).read_text())
        prepared = base / "candidate" / plan["target"]["name"]
        result = run("skill_variant.py", "accept", *args, "--prepare", prepared, **kwargs)
        if result.returncode:
            return result
        prepared = Path(json.loads(result.stdout)["prepared"])
        expected = {"route": "variant", "target": str(Path(plan["target"]["path"]).resolve()),
                    "inputs": {"plan": tree_digest(plan), "review": tree_digest(review)}}
        flags = evidence(base, prepared, expected)
        return run("skill_variant.py", "accept", *args, *flags, **kwargs)
