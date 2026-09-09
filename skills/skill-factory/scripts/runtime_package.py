"""Copy the canonical native lock and compiler config into an unaccepted package."""
import json
import shutil
from source_coverage import load_json, require

FILES = ["package.json", "package-lock.json", "tsconfig.json", ".npmrc"]
NATIVE_PROBES = ["workflow-engine.test.ts", "workflow-schemas.test.ts",
                 "workflow-storage.test.ts", "workflow-storage.fixture.ts"]
HUMAN_SUPPORT = ["human_catalogs.py", "human_catalog_sources.py", "human_pdf_catalogs.py",
                 "human-matrix-workflow.ts", "human_matrix.py", "human_matrix_records.py",
                 "human_combinations.py", "human_matrix_budget.py"]


def compatible_manifest(factory, target):
    expected = load_json(factory / "package.json")
    actual = load_json(target / "package.json")
    require(isinstance(actual, dict), "runtime manifest must be an object")
    for group in ["dependencies", "devDependencies", "engines"]:
        declared = actual.get(group)
        require(isinstance(declared, dict) and all(declared.get(name) == version
                for name, version in expected[group].items()),
                f"runtime {group} differ from the tested native baseline; reconcile explicitly")
    require(actual.get("packageManager") == expected["packageManager"],
            "runtime package manager differs; preserve it and reconcile an explicit compatible integration")
    lock = load_json(target / "package-lock.json")
    require(isinstance(lock, dict) and lock.get("lockfileVersion") == 3
            and isinstance(lock.get("packages"), dict), "runtime lock must contain native package records")
    root = lock["packages"].get("")
    require(isinstance(root, dict) and all(root.get(key) == actual.get(key)
            for key in ["name", "dependencies", "devDependencies", "engines"]),
            "runtime manifest and lock root disagree; reconcile without replacing unrelated dependencies")


def copy_runtime(factory, target):
    present = [name for name in FILES if (target / name).exists()]
    if present:
        require(len(present) == len(FILES),
                "partial native runtime needs explicit reconciliation before support copying")
        compatible_manifest(factory, target)
        return
    for name in FILES:
        destination = target / name
        if not destination.exists():
            shutil.copyfile(factory / name, destination)
    for name in ["package.json", "package-lock.json"]:
        path = target / name
        data = json.loads(path.read_text())
        data["name"] = target.name + "-workflows"
        if "packages" in data:
            data["packages"][""]["name"] = data["name"]
        path.write_text(json.dumps(data, indent=2) + "\n")
