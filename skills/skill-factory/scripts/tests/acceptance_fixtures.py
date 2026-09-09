"""Disposable, explicitly mechanical evidence for acceptance boundary tests."""
import json
import subprocess
import time
import sys
from pathlib import Path

from cli import SCRIPTS, run
sys.path.insert(0, str(SCRIPTS))
from skill_package import inventory, tree_digest
from test_acceptance_bindings import digest
from test_invocation_receipt import receipt, write_case

SOURCE = b"# Release notes\nCount exactly two lines. Preserve files.\n"


def coverage(source=SOURCE, clauses=(b"Count exactly two lines.", b"Preserve files.")):
    records, offset = [], 0
    for number, line in enumerate(source.splitlines(keepends=True), 1):
        records.append({"id": f"ROW-{number}", "kind": "obligation" if number == 2 else "context:heading",
                        "line_start": number, "line_end": number, "byte_start": offset,
                        "byte_end_exclusive": offset + len(line), "quote": line.decode(),
                        "source_sha256": digest(source)})
        offset += len(line)
    records[1]["clauses"] = [{"id": f"ROW-2-C{i}", "byte_start": source.index(quote),
                              "byte_end_exclusive": source.index(quote) + len(quote), "quote": quote.decode()}
                             for i, quote in enumerate(clauses, 1)]
    return {"source_sha256": digest(source), "source_bytes": len(source), "source_lines": 2, "records": records}


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")
    return digest(path.read_bytes())


def package(base):
    root = base / "release-notes"
    root.mkdir()
    data = receipt()
    write_case(root, data).unlink()
    (root / "SKILL.md").write_text('---\nname: release-notes\ndescription: "Use when release notes need review."\n'
                                 'metadata:\n  scope: "user"\n  version: "0.1.0"\n---\n\n# Release notes\n')
    path = root / "assets/use-case-contract.json"
    use_case = json.loads(path.read_text())
    use_case["audience"] = {"primary": "agent"}
    write_json(path, use_case)
    (root / "scripts").mkdir()
    (root / "notes.txt").write_text("First change.\nSecond change.\n")
    (root / "scripts/info.py").write_text('import json\nfrom pathlib import Path\n'
                                        'print(json.dumps({"lines": len(Path("notes.txt").read_text().splitlines())}))\n')
    return root, data


def context(base, root, command):
    (base / "source.md").write_bytes(SOURCE)
    coverage_digest = write_json(base / "coverage.json", coverage())
    spec = {"components": ["ROW-2-C1", "ROW-2-C2"], "applicability": "applicable",
            "producer": {"id": "local-mechanical-test", "kind": "mechanical"},
            "criteria": [{"path": ["result", "lines"], "equals": 2},
                         {"path": ["preserved"], "equals": True}],
            "command": command, "process_exit": 0}
    return {"version": 1, "source": {"path": str(base / "source.md"), "sha256": digest(SOURCE)},
            "coverage": {"path": str(base / "coverage.json"), "sha256": coverage_digest},
            "subject": {"skill": root.name, "scope": "user", "audience": "agent",
                        "revision": "disposable-candidate-1", "sha256": tree_digest(inventory(root))},
            "operation": "update release notes", "requirements": {"ROW-2": spec},
            "dependencies": {"graph": {"path": str(root / "mise.toml"),
                                       "sha256": digest((root / "mise.toml").read_bytes())}},
            "evidence_root": str(base / "evidence"),
            "validity": {"not_before": int(time.time()) - 60, "expires_at": int(time.time()) + 3600}}


def setup(base):
    root, data = package(base)
    command = ["mise", "run", "--force", "--task-cache", "off", "info"]
    before = inventory(root)
    executed = subprocess.run(command, cwd=root, capture_output=True, text=True)
    if executed.returncode:
        raise RuntimeError(executed.stdout + executed.stderr)
    spec = context(base, root, command)
    context_sha = write_json(base / "context.json", spec)
    (base / "evidence").mkdir()
    evidence = {"context_sha256": context_sha, "requirement": "ROW-2",
                "components": spec["requirements"]["ROW-2"]["components"],
                "producer": spec["requirements"]["ROW-2"]["producer"],
                "run_id": "disposable-mechanical-run", "state": "passed",
                "execution": {"argv": command, "exit_code": executed.returncode,
                              "stdout": executed.stdout, "stderr": executed.stderr},
                "result": json.loads(executed.stdout),
                "preserved": inventory(root) == before,
                "judgment": {"basis": "The actual notes file has two lines and owned files remain unchanged.",
                             "limits": "Mechanical fixture only; no semantic or human acceptance."}}
    artifact_sha = write_json(base / "evidence/row-2.json", evidence)
    data["acceptance"] = {"context_sha256": context_sha, "subject": spec["subject"],
                          "claims": {"ROW-2": {"path": "row-2.json", "sha256": artifact_sha}}}
    receipt_sha = write_json(base / "receipt.json", data)
    return root, spec, data, context_sha, receipt_sha


def invoke(base, context_sha, receipt_sha):
    return run("check_invocation_receipt.py", base / "release-notes", base / "receipt.json",
               "--acceptance-context", base / "context.json", "--context-sha256", context_sha,
               "--receipt-sha256", receipt_sha)
