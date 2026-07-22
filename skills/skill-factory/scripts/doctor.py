#!/usr/bin/env python3
"""Environment readiness report for skill building.

Checks the interpreter version, the mise task runner, the git tool,
and the bundled scripts and templates. Prints a JSON report to stdout.

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
           "check_evals.py", "scaffold_skill.py", "doctor.py"]
TEMPLATES = ["skill-template.md", "mise-template.toml",
             "evals-template.json", "trigger-template.json",
             "starter-script.py", "starter-test.py",
             "decisions-template.md", "eval-case-template.json",
             "ci/ci.yml"]


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
        check_command("git", required=False),
        check_files("scripts", SKILL_DIR / "scripts", SCRIPTS),
        check_files("templates", SKILL_DIR / "assets", TEMPLATES),
    ]
    ready = all(c["ok"] for c in checks if c["required"])
    print(json.dumps({"ready": ready, "checks": checks}, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
