#!/usr/bin/env python3
"""Run deterministic package checks for mobile-first-website-design."""
import json
from pathlib import Path
import prompt_corpus
import validate_packet

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "fail-breakpoint-order": "BLOCKED_BREAKPOINT_ORDER",
    "fail-capability-floor": "BLOCKED_CAPABILITY_FLOOR",
    "fail-flora-routing": "BLOCKED_FLORA_ROUTING",
    "fail-performance": "BLOCKED_PERFORMANCE",
    "fail-prompt-hash": "BLOCKED_PROMPT_HASH",
    "fail-style-in-wireframe": "BLOCKED_STYLE_IN_WIREFRAME",
    "pass-degraded": "PASS_RELEASE_DEGRADED",
    "pass-full": "PASS_RELEASE",
}


def main():
    problems = []
    corpus = prompt_corpus.verify()
    if corpus != {"status": "PASS", "count": 1000, "shards": 201, "errors": []}:
        problems.append("prompt-corpus")
    for name, state in EXPECTED.items():
        path = ROOT / "assets" / "fixtures" / f"{name}.json"
        result = validate_packet.validate(json.loads(path.read_text(encoding="utf-8")))
        if result["status"] != state:
            problems.append(name)
    mapping = json.loads((ROOT / "evals" / "source-mapping.json").read_text(encoding="utf-8"))
    entries = mapping.get("entries", [])
    if len(entries) != 12029 or any(row.get("review_state") != "approved" for row in entries):
        problems.append("source-mapping")
    print(json.dumps({"errors": problems, "status": "PASS" if not problems else "BLOCKED"}, sort_keys=True, separators=(",", ":")))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
