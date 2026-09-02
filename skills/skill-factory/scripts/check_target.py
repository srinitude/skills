#!/usr/bin/env python3
"""Run the factory's checks against one existing skill.

Usage:
  python3 scripts/check_target.py validate SKILL_ROOT
  python3 scripts/check_target.py eval SKILL_ROOT

Exit codes:
  0  every selected check passed
  1  at least one selected check failed
  2  bad usage

Example:
  python3 scripts/check_target.py validate ../example-skill
"""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKS = {
    "validate": [
        "validate_skill.py",
        "lint_writing.py",
        "check_code_rules.py",
        "check_placeholders.py",
        "check_improvement_contract.py",
        "check_domain_research.py",
        "check_use_case_contract.py",
        "check_mise_primitives.py",
        "check_primitive_lifecycle.py",
        "check_task_graph.py",
        "check_decision_records.py",
    ],
    "eval": ["check_evals.py"],
}


def run_check(script, target):
    command = [sys.executable, str(SCRIPT_DIR / script), str(target)]
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"[{Path(script).stem}]")
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def run_mode(mode, target):
    codes = [run_check(script, target) for script in CHECKS[mode]]
    return 1 if any(codes) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=sorted(CHECKS))
    parser.add_argument("skill_root")
    args = parser.parse_args(argv)
    candidate = Path(args.skill_root)
    if candidate.is_symlink():
        print(f"FAIL target skill root is a symlink: {candidate}")
        return 1
    target = candidate.resolve()
    if not (target / "SKILL.md").is_file():
        print(f"FAIL not a skill directory: {target}")
        return 1
    return run_mode(args.mode, target)


if __name__ == "__main__":
    sys.exit(main())
