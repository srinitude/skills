"""Add the native checker runtime without overwriting unreviewed target owners."""
import hashlib
import re
import shutil
import tomllib

ROOT_FILES = ("package.json", "package-lock.json", "tsconfig.json")
LEDGER_FILES = ("review_ledger_context.py", "review_ledger_source.py", "review_ledger_tasks.py", "review_ledger_derived.py", "review_ledger_candidates.py", "review_ledger_graph.py", "review_ledger.py", "review_ledger_workflow.ts",
                "run_review_ledger.ts", "tests/test_review_ledger_source.py", "tests/test_review_ledger_runtime.py", "tests/test_review_ledger_derived.py", "tests/test_review_ledger_tasks.py", "tests/test_review_ledger_candidates.py")
TOOLS = {"node": "24.18.0", "npm": "11.16.0", "uv": "0.11.29"}
# The published pre-TypeScript checker is the only automatically migratable baseline.
LEGACY_SCRIPTS = {"check_code_rules.py": "1e86522fe8549ca3ec742c989c023ff2744db167266711537dc79c268a452824",
                  "skill_package.py": "466753d6f604a9433e9b51ace0a58d3f5f34191dc98b0083689aab25dfae7184"}


def copy_runtime(factory, root):
    for name in LEDGER_FILES:
        target = root / "scripts" / name
        if target.exists() and target.read_bytes() != (factory / "scripts" / name).read_bytes():
            raise ValueError("ledger runtime owner needs explicit reconciliation: " + name)
    for name in ROOT_FILES:
        target = root / name
        if target.exists() and target.read_bytes() != (factory / name).read_bytes():
            raise ValueError(f"runtime owner needs explicit reconciliation: {name}")
    for name, baseline in LEGACY_SCRIPTS.items():
        checker = root / "scripts" / name
        if not checker.exists():
            continue
        current = hashlib.sha256(checker.read_bytes()).hexdigest()
        wanted = hashlib.sha256((factory / "scripts" / name).read_bytes()).hexdigest()
        if current not in {baseline, wanted}:
            raise ValueError("runtime checker has unreviewed target customizations: " + name)
    for name in ROOT_FILES:
        target = root / name
        if not target.exists():
            shutil.copyfile(factory / name, target)


def runtime_preamble(preamble):
    tools = tomllib.loads(preamble).get("tools", {})
    if tools.get("uv") == "latest":
        pattern = r"(?m)^uv\s*=\s*[\"']latest[\"'](?=\s*(?:#.*)?$)"
        preamble, count = re.subn(pattern, 'uv = "0.11.29"', preamble)
        if count != 1:
            raise ValueError("runtime uv version needs explicit syntax reconciliation")
        tools = tomllib.loads(preamble).get("tools", {})
    missing = []
    for name, version in TOOLS.items():
        value = tools.get(name)
        value = value.get("version") if isinstance(value, dict) else value
        if value is None:
            missing.append(f'{name} = "{version}"')
        elif value != version:
            raise ValueError(f"runtime {name} version needs explicit compatibility reconciliation")
    if "python" not in tools:
        missing.append('python = "3.11.15"')
    if not missing:
        return preamble
    match = re.search(r"(?m)^\[tools\][ \t]*$", preamble)
    if match:
        return preamble[:match.end()] + "\n" + "\n".join(missing) + preamble[match.end():]
    if tools:
        raise ValueError("runtime tool table needs explicit syntax reconciliation")
    return preamble.rstrip() + "\n\n[tools]\n" + "\n".join(missing)


UV_RUN = "uv run --with PyYAML==6.0.3 "
ISOLATED_UV = "uv run --no-project --isolated --no-python-downloads --with PyYAML==6.0.3 "
SHARED_PYTHON = ("scripts/validate_skill.py", "scripts/check_lineage.py",
                 "scripts/scaffold_skill.py", "scripts/check_target.py",
                 "scripts/standardize_registry_skill.py", "scripts/resolve_scope.py",
                 "scripts/skill_variant.py", "python -m unittest discover")


def isolate_python_helpers(block):
    task = tomllib.loads("[task]\n" + block)["task"]
    helpers = [command for field in ["run", "run_windows"]
               if isinstance(command := task.get(field), str)
               and any(command.startswith(prefix + owner + " ") or command == prefix + owner
                       for prefix in [UV_RUN, ISOLATED_UV] for owner in SHARED_PYTHON)]
    if not helpers:
        return block
    environment = task.get("env")
    if environment is None:
        block = 'env = { UV_PYTHON = "{{tools.python.path}}" }\n' + block
    elif not isinstance(environment, dict) or environment.get("UV_PYTHON") != "{{tools.python.path}}":
        raise ValueError("Python helper environment needs explicit reconciliation")
    for command in dict.fromkeys(helpers):
        if command.startswith(UV_RUN):
            if command not in block:
                raise ValueError("Python helper command syntax needs explicit reconciliation")
            block = block.replace(command, ISOLATED_UV + command[len(UV_RUN):])
    return block
