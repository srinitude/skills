#!/usr/bin/env python3
"""Environment readiness report for skill building.

Checks the interpreter version, the required mise task runner, the git
tool, and the bundled scripts and templates. Prints JSON to stdout.

Exit codes:
  0  every required check passed
  1  a required check failed
  2  usage error

Example:
  python3 scripts/doctor.py
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = ["lint_writing.py", "validate_skill.py", "check_code_rules.py",
           "check_evals.py", "check_placeholders.py",
           "check_improvement_contract.py", "check_lineage.py",
           "check_source_corpus.py", "check_target.py", "plan_standardize.py",
           "check_task_graph.py", "check_invocation_receipt.py",
           "check_mise_primitives.py", "check_primitive_lifecycle.py",
           "sync_mise_primitives.py", "domain_text.py",
           "scaffold_skill.py", "doctor.py"]
TEMPLATES = ["skill-template.md", "mise-template.toml", "example-template.md",
             "evals-template.json", "trigger-template.json",
             "starter-script.py", "starter-test.py", "starter-ci-test.py",
             "decisions-template.md", "eval-case-template.json",
             "improvement-contract.json", "use-case-contract.json",
             "use-case-contract-template.json", "source-shape-corpus.json",
             "decision-records.json", "decision-records-template.json",
             "invocation-receipt-template.json",
             "mise-primitives-catalog.json", "mise-primitives.json",
             "mise-primitives-template.json", "primitive-lifecycle.json",
             "primitive-lifecycle-template.json",
             "ci/ci.yml"]
REFERENCES = ["generation-contract.md", "resource-and-experiment-design.md",
              "use-case-specificity.md",
              "writing-rules.md"]


def check_python():
    ok = sys.version_info >= (3, 11)
    detail = "%d.%d.%d" % sys.version_info[:3]
    return {"name": "python", "required": True, "ok": ok,
            "detail": f"found {detail}, need 3.11 or newer"}


def check_command(name, required):
    path = shutil.which(name)
    return {"name": name, "required": required, "ok": path is not None,
            "detail": path or f"{name} not on PATH"}


def check_files(name, base, names):
    missing = [n for n in names if not (base / n).is_file()]
    detail = "all present" if not missing else "missing: " + ", ".join(missing)
    return {"name": name, "required": True, "ok": not missing,
            "detail": detail}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    checks = [
        check_python(),
        check_command("mise", required=True),
        check_command("uv", required=True),
        check_command("git", required=False),
        check_files("scripts", SKILL_DIR / "scripts", SCRIPTS),
        check_files("templates", SKILL_DIR / "assets", TEMPLATES),
        check_files("references", SKILL_DIR / "references", REFERENCES),
    ]
    ready = all(c["ok"] for c in checks if c["required"])
    report = {"ready": ready, "mode": "mise", "checks": checks}
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
