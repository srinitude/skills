"""Reusable clock-anchor fixtures for bounded standardization checks.

These declare an agent consumer and caller-bound inputs, not goal acceptance.
"""
SOURCES = [
    {"source": "https://www.rfc-editor.org/rfc/rfc3339", "source_class": "standard",
     "claim": "A clock anchor needs an offset.", "limitations": "No timezone choice."},
    {"source": "https://data.iana.org/time-zones/theory.html", "source_class": "first_party",
     "claim": "Timezone rules change.", "limitations": "No request interpretation."},
    {"source": "https://docs.python.org/3/library/datetime.html", "source_class": "first_party",
     "claim": "Aware times carry offsets.", "limitations": "No freshness proof."},
    {"source": "https://www.w3.org/TR/NOTE-datetime", "source_class": "standard",
     "claim": "Dates need a profile.", "limitations": "No current civil time."},
]
MISE_TEXT = (
    "[tasks.anchor]\ndescription = \"Read the clock anchor\"\n"
    "run = \"python3 scripts/anchor.py\"\n\n[tasks.ci]\n"
    "description = \"Check the clock anchor\"\nrun = [\"mise run anchor\"]\n\n"
    "[tasks.inspect-anchor]\ndescription = \"Old inspector\"\n"
    "run = \"python3 scripts/inspect.py\"\n"
)


def profile():
    return {
        "skill": "clock-anchor",
        "primary_term": "clock anchor",
        "audience": {"primary": "agent"},
        "initial_context": [{"id": "governing-ledger", "role": "ledger", "binding": "invocation", "depends_on": []},
                            {"id": "study-work-matrix", "role": "resource", "binding": "invocation", "depends_on": ["governing-ledger"]}],
        "domain_terms": ["clock anchor", "timezone offset", "relative date"],
        "outcome": "Return one fresh clock anchor for each direct turn.",
        "main_task": "anchor",
        "main_run": "python3 scripts/anchor.py",
        "public_tasks": ["inspect-anchor"],
        "script_tasks": {
            "inspect-anchor": {
                "script": "inspect.py",
                "description": "Inspect one clock anchor receipt",
                "args": "--format json",
                "runner": "uv run python"
            }
        },
        "text_rewrites": {
            "scripts/domain_check.py": [
                {"old": "LEGACY_ASSERTION", "new": "FACTORY_ASSERTION"}
            ]
        },
        "sources": SOURCES,
    }


def write_target(root):
    root.mkdir()
    (root / "SKILL.md").write_text(
        "---\nname: clock-anchor\ndescription: 'Use when time matters.'\n"
        "license: MIT\nmetadata:\n  author: Kiren Srinivasan\n"
        "  version: '0.1.0'\n---\n\n# Clock anchor\n\n"
        "Run `python3 scripts/anchor.py` once.\n\n"
        "Package maintainers inspect `scripts/` after a failed task.\n",
        encoding="utf-8")
    (root / "mise.toml").write_text(MISE_TEXT, encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts" / "anchor.py").write_text("print('clock anchor')\n")
    (root / "scripts" / "inspect.py").write_text("print('anchor receipt')\n")
    (root / "scripts" / "domain_check.py").write_text("LEGACY_ASSERTION\n")
    (root / "scripts" / "report_clock.py").write_text("print('report')\n")
    (root / "scripts" / "validate_skill.py").write_text(
        "def check_layout(skill, body, problems):\n"
        "    for name in REQUIRED_DIRS + [\"scripts/tests\"]:\n"
        "        if not (skill / name).is_dir():\n"
        "            problems.append(f\"missing required directory: {name}/\")\n"
        "        elif body and f\"{name}/\" not in body:\n"
        "            problems.append(f\"body never references {name}/\")\n",
        encoding="utf-8")
    (root / "references").mkdir()
    (root / "references" / "contract.md").write_text(
        "# Contract\n\nRun `python3 scripts/anchor.py`.\n\n"
        "Run `python3 scripts/report_clock.py`.\n\n"
        "Run [the receipt inspector](scripts/inspect.py).\n\nRead assets/state.json.\n\n"
        "Read ../SKILL.md and ../evals/cases.json.\n",
        encoding="utf-8")
