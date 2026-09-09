"""Executable file-inventory packages for scope adaptation tests."""
import json
import shutil
import sys
from pathlib import Path

from cli import SKILL_DIR, SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from check_lineage import report
from skill_package import inventory, tree_digest
from standardize_registry_skill import apply
SOURCES = [
    {"source": "https://docs.python.org/3/library/pathlib.html", "source_class": "first_party",
     "claim": "Path resolution and recursive discovery support file inventory boundaries.", "limitations": "The skill must enforce its own project boundary."},
    {"source": "https://docs.python.org/3/library/json.html", "source_class": "first_party",
     "claim": "JSON carries explicit project configuration.", "limitations": "Parsing does not prove configuration intent."},
    {"source": "https://docs.python.org/3/library/hashlib.html", "source_class": "first_party",
     "claim": "SHA-256 binds the inventory to file bytes.", "limitations": "Digests do not prove semantic adaptation."},
    {"source": "https://www.rfc-editor.org/rfc/rfc8259", "source_class": "standard",
     "claim": "JSON objects and arrays carry structured inventory results.", "limitations": "The schema and behavior remain skill-owned."},
]

PROGRAM = '''"""Count configured source files without writing project data."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--project", required=True)
args = parser.parse_args()
project = Path(args.project).resolve()
config = json.loads((project / "inventory.json").read_text())
FIXED_CONFIGURATION
relative = Path(config["directory"])
if relative.is_absolute() or ".." in relative.parts:
    raise SystemExit("directory must stay inside the project")
root = (project / relative).resolve()
if not root.is_relative_to(project) or not root.is_dir():
    raise SystemExit("source directory is missing or outside the project")
files = sorted(root.rglob("*" + config["extension"]))
if any(p.is_symlink() for p in root.rglob("*")):
    raise SystemExit("source symlinks are not supported")
print(json.dumps({"files": len(files), "lines": sum(len(p.read_text().splitlines()) for p in files)}))
'''


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def project(root, identifier="repo:atlas", directory="src", extension=".py"):
    root.mkdir(parents=True)
    (root / directory).mkdir(parents=True)
    (root / directory / ("main" + extension)).write_text("first line\nsecond line\n")
    (root / "AGENTS.md").write_text("Count only configured source files. Never write project files.\n")
    write_json(root / "inventory.json", {"identity": identifier, "directory": directory,
                                         "extension": extension})
    return root


def package(root, scope, project_id="repo:atlas"):
    root.mkdir(parents=True)
    for name in ["references", "assets", "examples", "scripts/tests", "evals"]:
        (root / name).mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(header(root.name, scope) + body(scope, project_id))
    fixed = ('if config["identity"] != ' + repr(project_id) + ':\n    raise SystemExit("wrong project")\n'
             'if config["directory"] != "src" or config["extension"] != ".py":\n'
             '    raise SystemExit("project configuration changed")') if scope == "project" else ""
    (root / "scripts/inventory.py").write_text(PROGRAM.replace("FIXED_CONFIGURATION", fixed))
    (root / "references/behavior.md").write_text("# File inventory\n\nCount configured source files and lines without writes. Reject paths outside the project.\n")
    (root / "examples/run.md").write_text("# File inventory example\n\nRun `mise run inventory -- --project <project>`. One two-line source returns two lines and one file.\n")
    (root / "LICENSE").write_bytes((SKILL_DIR / "LICENSE").read_bytes())
    (root / "NOTICE").write_text("File inventory example. Kiren Srinivasan.\n")
    seed_evals(root)
    data = {"skill": root.name, "primary_term": "file inventory", "outcome": "Count configured source files and lines without writes.",
            "audience": {"primary": "agent"},
            "domain_terms": ["file inventory", "source files", "project configuration"], "main_task": "inventory",
            "main_run": "python3 scripts/inventory.py", "sources": SOURCES}
    research = json.loads(Path(__file__).with_name("file_inventory_research.json").read_text())
    data.update({key: research[key] for key in ["research_receipts", "disconfirmation"]})
    apply(root, data)
    return root


def header(name, scope):
    return (f'---\nname: {name}\ndescription: "Use when configured source files need a file inventory."\n'
            f'license: MIT\nmetadata:\n  author: Kiren Srinivasan\n  version: "0.1.0"\n  scope: "{scope}"\n---\n\n')


def body(scope, project_id):
    applicability = (f"Apply only to project {project_id}, with Python files under src. "
                     "Reject another identity or changed configuration.") if scope == "project" else (
                     "Read each project's inventory.json for directory and extension. Support UTF-8 source trees in Python or JavaScript projects.")
    return ("# File inventory\n\nCount configured source files and lines without changing files.\n\n"
            + applicability + "\n\n## Commands\n\nRun `mise run inventory -- --project <project>`. "
            "Read references/behavior.md and examples/run.md through `mise run validate` before first use. "
            "Validate assets/ and evals/ through `mise run ci`.\n")


def seed_evals(root):
    cases = [{"source_id": f"FI-{i}", "prompt": prompt, "expected_output": "A file inventory or a specific input error.",
              "required": ["Count configured source files without writes."]}
             for i, prompt in enumerate(["Count Python files under src.", "Count JavaScript files under lib.",
                                         "Reject a missing source directory.", "Reject a path outside the project."], 1)]
    write_json(root / "evals/cases.json", {"cases": cases})
    write_json(root / "evals/trigger-queries.json", [{"query": q, "should_trigger": b} for q, b in [
        ("Count configured source files", True), ("Report file inventory", True),
        ("Delete source files", False), ("Explain the weather", False)]])


def review(source, candidate, projects):
    files = inventory(source)
    result = {"source_digest": tree_digest(files), "candidate_digest": tree_digest(inventory(candidate)),
            "coverage": {p: {"disposition": "reviewed", "reason": "Retain applicable file inventory requirements; adapt scope and project inputs."} for p in files},
            "adaptations": ["Bind the project variant to its declared identity and source layout; discover user variant configuration per project."],
            "requirements": ["Read-only source counts; reject traversal and symlinks; preserve license and attribution."],
            "compatibility": "Python 3.11 or newer and UTF-8 source files with explicit inventory.json configuration.",
            "privacy_review": "No credentials, private source content, or installation dependencies retained.",
            "independence_review": "All runtime code is bundled; only the declared target project configuration is needed.",
            "forbidden_strings": ["/Users/private", "PRIVATE_CUSTOMER_DATA"], "resolutions": {},
            "scenarios": [{"id": str(i), "project": str(p), "difference": d,
                           "script": "scripts/inventory.py", "expected_exit": 0,
                           "expected_stdout": '{"files": 1, "lines": 2}\n'} for i, (p, d) in enumerate(projects)]}


    if 'scope: "project"' in (candidate / "SKILL.md").read_text() and projects:
        context = inventory(projects[0][0])
        result["project_review"] = {"digest": tree_digest(context),
            "coverage": {p: {"disposition": "reviewed", "reason": "Read authoritative project context for inventory adaptation."} for p in context},
            "facts": {"instructions": "AGENTS.md requires read-only configured counts.",
                      "structure": "Python source under src.", "tools": "Python standard library.",
                      "commands": "Mise inventory task receives explicit project input.",
                      "configuration": "inventory.json binds identity, directory, and extension.",
                      "constraints": "Reject other identities, changed layout, traversal, and symlinks."}}
    return result


def export_packages(base):
    import os
    destination = os.environ.get("SCOPE_EVAL_OUTPUT")
    if destination:
        target = Path(destination).resolve()
        if target.exists():
            raise ValueError("scope eval output already exists")
        shutil.copytree(base, target)
