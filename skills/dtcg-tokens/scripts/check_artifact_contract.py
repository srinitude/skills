#!/usr/bin/env python3
"""Check that artifact design stays with the strong vision executor."""
import argparse
import json
import sys
from pathlib import Path

FORBIDDEN = [
    "scripts/lib/artifact.py", "scripts/lib/artifact_css.py",
    "scripts/lib/artifact_sections.py", "scripts/lib/artifact_theme.py",
    "scripts/render_proof.py",
    "assets/proof-template.html", "assets/example-identity-board.svg",
]
REQUIRED_CATALOGS = [
    "assets/visual-defect-catalog.json",
    "assets/judgment-review-catalog.json",
    "assets/perceptual-motor-invariant-catalog.json",
    "assets/exploration-strategy-catalog.json",
]


def check(root):
    errors = [f"forbidden automatic design resource: {name}" for name in FORBIDDEN if (root / name).exists()]
    errors += [f"missing review catalog: {name}" for name in REQUIRED_CATALOGS if not (root / name).is_file()]
    negative = root / "evals" / "files" / "rejected-visual-precedents.json"
    if not negative.is_file():
        return errors + ["missing rejected visual precedent evals"]
    cases = json.loads(negative.read_text(encoding="utf-8")).get("cases", [])
    if len(cases) < 2 or any(item.get("expected_verdict") != "fail" for item in cases):
        errors.append("rejected visual precedent evals must contain only failures")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="skill root")
    args = parser.parse_args(argv)
    root = Path(args.target)
    if not root.is_dir():
        print("error: target must be a skill directory", file=sys.stderr)
        return 2
    errors = check(root)
    for error in errors:
        print(error)
    print(f"artifact contract: {'fail' if errors else 'pass'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
