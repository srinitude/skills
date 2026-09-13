"""Read literal task fields; use native Mise to resolve included TOML owners."""
import json
import subprocess
import tomllib
from pathlib import Path


def source_bytes(root, path):
    path = Path(path).absolute()
    if not path.is_relative_to(root) or not path.resolve().is_relative_to(root):
        raise ValueError("task source escapes this skill")
    if any(part.is_symlink() for part in [path, *path.parents] if part.is_relative_to(root)):
        raise ValueError("task source must not be a symlink")
    if not path.is_file():
        raise ValueError("task source must be a regular file: " + str(path))
    return path.read_bytes()


def included_sources(root, config):
    settings = config.get("task_config", {})
    if not isinstance(settings, dict):
        raise ValueError("task_config must be a table")
    includes = settings.get("includes", [])
    if not isinstance(includes, list) or any(not isinstance(item, str) for item in includes):
        raise ValueError("task includes must be an explicit array of local TOML files")
    paths = [root / item for item in includes]
    if any(path.suffix != ".toml" or any(char in str(path) for char in "*?{[") for path in paths):
        raise ValueError("nonliteral or non-TOML task includes need explicit reconciliation")
    return paths


def native_tasks(root):
    try:
        result = subprocess.run(["mise", "-C", str(root), "tasks", "ls", "--hidden", "--json"],
                                text=True, capture_output=True, timeout=30, check=True)
        tasks = json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise ValueError("native Mise task discovery failed: " + str(error)) from error
    if not isinstance(tasks, list) or any(not isinstance(task, dict) for task in tasks):
        raise ValueError("native Mise task list must be an array of objects")
    return [task for task in tasks if Path(task["source"]).is_relative_to(root)]


def grouped_tasks(root, sources):
    before = native_tasks(root)
    parsed = {path: tomllib.loads(raw.decode("utf-8")) for path, raw in sources.items()}
    tasks = {}
    for task in before:
        source = Path(task["source"])
        if source not in sources or any(Path(path) != source for path in task.get("config_sources", [])):
            raise ValueError("native task has an unreviewed source: " + task["name"])
        data = parsed[source]
        definitions = data.get("tasks", {}) if source == root / "mise.toml" else data
        if task["name"] not in definitions:
            raise ValueError("native task has no exact TOML owner: " + task["name"])
        tasks[task["name"]] = definitions[task["name"]]
    if before != native_tasks(root):
        raise ValueError("native tasks changed during discovery")
    return tasks


def load_tasks(root):
    root = Path(root).resolve()
    path = root / "mise.toml"
    sources = {path: source_bytes(root, path)}
    config = tomllib.loads(sources[path].decode("utf-8"))
    tasks = config.get("tasks", {})
    if not isinstance(tasks, dict):
        raise ValueError("tasks must be a table")
    included = included_sources(root, config)
    for source in included:
        sources[source.absolute()] = source_bytes(root, source)
    if included:
        tasks = grouped_tasks(root, sources)
    for source, raw in sources.items():
        if source_bytes(root, source) != raw:
            raise ValueError("task source changed during discovery")
    return tasks
