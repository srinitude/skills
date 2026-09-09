"""Add the native checker runtime without overwriting unreviewed target owners."""
import hashlib
import re
import shutil
import tomllib

ROOT_FILES = ("package.json", "package-lock.json", "tsconfig.json")
TOOLS = {"node": "24.18.0", "npm": "11.16.0"}
# The published pre-TypeScript checker is the only automatically migratable baseline.
LEGACY_SCRIPTS = {"check_code_rules.py": "1e86522fe8549ca3ec742c989c023ff2744db167266711537dc79c268a452824",
                  "skill_package.py": "466753d6f604a9433e9b51ace0a58d3f5f34191dc98b0083689aab25dfae7184"}


def copy_runtime(factory, root):
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
    missing = []
    for name, version in TOOLS.items():
        value = tools.get(name)
        value = value.get("version") if isinstance(value, dict) else value
        if value is None:
            missing.append(f'{name} = "{version}"')
        elif value != version:
            raise ValueError(f"runtime {name} version needs explicit compatibility reconciliation")
    if not missing:
        return preamble
    match = re.search(r"(?m)^\[tools\][ \t]*$", preamble)
    if match:
        return preamble[:match.end()] + "\n" + "\n".join(missing) + preamble[match.end():]
    if tools:
        raise ValueError("runtime tool table needs explicit syntax reconciliation")
    return preamble.rstrip() + "\n\n[tools]\n" + "\n".join(missing)
