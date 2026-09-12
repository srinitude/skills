"""Add the native checker runtime without overwriting unreviewed target owners."""
from skill_package import sha
import re
import json
import tomllib
from pathlib import Path

SECTION_RE = re.compile(r"(?m)^\[tasks\.([^]]+)\]\s*$")


def section_name(match):
    name, fields = next(iter(tomllib.loads(match.group(0))["tasks"].items()))
    return name if not fields else None


def task_header(name):
    key = name if re.fullmatch(r"[A-Za-z0-9_-]+", name) else json.dumps(name)
    return f"[tasks.{key}]"


def split_task_body(block):
    child = next((match for match in SECTION_RE.finditer(block) if section_name(match) is None), None)
    return (block[:child.start()].rstrip(), block[child.start():].strip()) if child else (block, "")


def split_sections(text):
    matches = [(match, name) for match in SECTION_RE.finditer(text)
               if (name := section_name(match)) is not None]
    preamble = text[:matches[0][0].start()] if matches else text
    sections = []
    for index, (match, name) in enumerate(matches):
        end = matches[index + 1][0].start() if index + 1 < len(matches) else len(text)
        sections.append((name, text[match.end():end].strip("\n")))
    return preamble.rstrip(), sections


ROOT_FILES = ("package.json", "package-lock.json", "tsconfig.json",
              "runtime/standardization/package.json", "runtime/standardization/package-lock.json")
LEDGER_EXAMPLES = ("examples/graph-public-run.json", "examples/ledger-write-run.json", "examples/lineage-public-run.json",
                   "examples/catalog-public-run.json", "examples/registry-public-run.json", "examples/example-ledger-write.md")
LEDGER_FILES = ("render_file_graph.py", "tests/test_render_file_graph.py", "review_ledger_context.py", "review_ledger_source.py", "review_ledger_tasks.py", "review_ledger_derived.py", "review_ledger_candidates.py", "review_ledger_graph.py", "review_ledger_file_graph.py", "review_ledger_body.py", "review_ledger_write.py", "review_ledger.py", "review_ledger_workflow.ts",
                "run_review_ledger.ts", "tests/cli.py", "tests/test_review_ledger_source.py", "tests/test_review_ledger_runtime.py", "tests/test_review_ledger_derived.py", "tests/test_review_ledger_tasks.py", "tests/test_review_ledger_candidates.py", "tests/test_review_ledger_work.py", "tests/test_review_ledger_file_graph.py", "tests/test_review_ledger_write.py", "tests/test_related_owner_write.py", "tests/test_review_ledger_modes.py", "tests/test_package_preservation.py", "tests/test_review_ledger_write_recovery.py", "tests/test_review_ledger_write_boundaries.py", "tests/test_review_ledger_bootstrap.py", "tests/test_review_ledger_body.py", "tests/test_review_ledger_initial.py", "tests/test_catalog_review.py", "tests/test_sync_mise_primitives.py")
LEDGER_FILES += ("native_file_workflow.ts", "tests/test_review_ledger_native.py", "review_ledger_native.py", "markdown_checks.py", "markdown_workflow.ts",
                 "run_markdown.ts", "standardization_workflow.ts", "run_standardization.ts")
TOOLS = {"node": "24.18.0", "npm": "11.16.0", "uv": "0.11.29"}
# The published pre-TypeScript checker is the only automatically migratable baseline.
LEGACY_SCRIPTS = {"check_code_rules.py": "1e86522fe8549ca3ec742c989c023ff2744db167266711537dc79c268a452824",
                  "skill_package.py": "466753d6f604a9433e9b51ace0a58d3f5f34191dc98b0083689aab25dfae7184"}


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


def isolate_python_helpers(block, task):
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
        if not command.startswith(UV_RUN):
            continue
        if command not in block:
            raise ValueError("Python helper command syntax needs explicit reconciliation")
        block = block.replace(command, ISOLATED_UV + command[len(UV_RUN):])
    return block

def check_runtime(files, factory):
    for name in [*ROOT_FILES, *LEDGER_EXAMPLES, *('scripts/' + name for name in LEDGER_FILES)]:
        if name in files and files[name] != (factory / name).read_bytes():
            raise ValueError('runtime owner needs explicit reconciliation: ' + name)
    for name, baseline in LEGACY_SCRIPTS.items():
        path = 'scripts/' + name
        if path in files and sha(files[path]) not in {baseline, sha((factory / path).read_bytes())}:
            raise ValueError('runtime checker has unreviewed target customizations: ' + name)


CATALOG_USAGE = 'flag "--review <path>" required=#true'
CATALOG_RUN = 'python3 scripts/sync_mise_primitives.py . --review "${usage_review?}"'


def catalog_task(block):
    task = tomllib.loads('[task]\n' + block)['task']
    if task.get('usage', CATALOG_USAGE) != CATALOG_USAGE:
        raise ValueError('catalog review usage needs explicit reconciliation')
    changes = {'run': CATALOG_RUN}
    if 'run_windows' in task:
        changes['run_windows'] = CATALOG_RUN.replace('python3 ', 'python ', 1)
    result = block
    for key, command in changes.items():
        legacy = command.split(' --review ')[0]
        if task.get(key) not in (legacy, command):
            raise ValueError('catalog command needs explicit reconciliation: ' + key)
        pattern = rf"""(?m)^({key}\s*=\s*)(?:"(?:[^"\\]|\\.)*"|'[^']*')([ \t]*(?:#[^\n]*)?)$"""
        result, count = re.subn(pattern, lambda match: match[1] + json.dumps(command) + match[2], result)
        if count != 1:
            raise ValueError('catalog command syntax needs explicit reconciliation: ' + key)
    if 'usage' not in task:
        result = 'usage = ' + json.dumps(CATALOG_USAGE) + '\n' + result
    expected = {**task, **changes, 'usage': CATALOG_USAGE}
    if tomllib.loads('[task]\n' + result)['task'] != expected:
        raise ValueError('catalog migration changed an unrelated task field')
    return result


def runtime_dependencies(name, dependencies, names):
    result = list(dependencies)
    provider = {"test": "setup-graph-renderer", "setup-graph-renderer": "lint-code", "lint-code": "check-runtime"}.get(name)
    if provider in names and provider not in result:
        result.append(provider)
    chains = [("test", ("setup-graph-renderer", "lint-code", "setup-runtime", "check-runtime")),
              ("setup-graph-renderer", ("lint-code", "setup-runtime", "check-runtime")),
              ("lint-code", ("setup-runtime", "check-runtime")), ("check-runtime", ("setup-runtime",))]
    for consumer, ancestors in chains:
        if consumer in result and consumer in names:
            return [item for item in result if item not in ancestors]
    return result



def strip_key(block, key):
    lines, output, skipping = block.splitlines(), [], False
    for line in lines:
        if skipping:
            skipping = not line.strip().endswith("]")
            continue
        if re.match(rf"^{re.escape(key)}\s*=", line):
            skipping = "[" in line and not line.strip().endswith("]")
            continue
        output.append(line)
    return "\n".join(output).strip()



def nested_dependencies(block):
    command = tomllib.loads('[task]\n' + block)['task'].get('run')
    command = command[0] if isinstance(command, list) and len(command) == 1 else command
    match = re.fullmatch(r"mise run ([a-z0-9][a-z0-9:-]*)", command.strip()) if isinstance(command, str) else None
    if not match and re.search(r'\bmise\s+run\b', json.dumps(command)):
        raise ValueError('nested CI execution needs explicit reconciliation before standardization')
    return [match.group(1)] if match else []


MARKDOWN_TASKS = {name: task for name, task in tomllib.loads(
    (Path(__file__).resolve().parents[1] / "mise.toml").read_text())["tasks"].items()
    if name.startswith("markdown:")}


def check_runtime_tasks(tasks, policy):
    for name in ["setup-runtime", "check-runtime", *MARKDOWN_TASKS]:
        if name in tasks and (tasks[name].get("run") != policy[name][2]
                              or tasks[name].get("depends") != policy[name][0]):
            raise ValueError("native runtime task needs explicit reconciliation: " + name)
        if name in tasks and name in MARKDOWN_TASKS and tasks[name].get("env") != MARKDOWN_TASKS[name]["env"]:
            raise ValueError("Markdown environment needs explicit reconciliation: " + name)
