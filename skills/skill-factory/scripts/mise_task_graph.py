"""Explicit task-reference policy; native runtime validation remains separate."""
import graphlib
import re
import shlex


def reference(item):
    optional = False
    if isinstance(item, dict):
        if set(item) - {"task", "args", "env", "optional"}:
            raise ValueError("unknown dependency fields")
        args, env = item.get("args", []), item.get("env", {})
        optional = item.get("optional", False)
        if not isinstance(args, list) or not all(isinstance(v, str) for v in args):
            raise ValueError("dependency args must be text array")
        if not isinstance(env, dict) or not all(isinstance(v, str) for v in env.values()):
            raise ValueError("dependency env must contain text values")
        if type(optional) is not bool:
            raise ValueError("dependency optional must be Boolean")
        item = [item.get("task"), *args]
    if isinstance(item, str):
        item = shlex.split(item)
        while item and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", item[0]):
            item = item[1:]
    if not isinstance(item, list) or not item or not all(isinstance(v, str) for v in item):
        raise ValueError("dependency must name a task with text arguments")
    return item[0], optional


def run_entries(task, fields=("run", "run_windows")):
    commands, refs = [], []
    for field in fields:
        entries = task.get(field, [])
        entries = [entries] if isinstance(entries, str) else entries
        if not isinstance(entries, list):
            raise ValueError(f"{field} must be text or an ordered array")
        for item in entries:
            command, references = run_entry(item)
            commands.extend(command)
            refs.extend(references)
    return commands, refs


def run_entry(item):
    if isinstance(item, str):
        return [item], []
    if isinstance(item, dict) and set(item) == {"tasks"} and isinstance(item["tasks"], list):
        return [], item["tasks"]
    if isinstance(item, dict) and "task" in item and not set(item) - {"task", "args", "env"}:
        return [], [item]
    raise ValueError("invalid run entry")


def resolve(items, tasks):
    result = []
    for item in items:
        name, optional = reference(item)
        if name in tasks:
            result.append(name)
        elif not optional:
            raise ValueError(f"unknown dependencies: {name}; resolve dynamic references with native Mise before acceptance")
    return result


def graphs(tasks, windows=False):
    calls, order, posts = {}, {}, {}
    for name, task in tasks.items():
        fields = ("run_windows",) if windows and "run_windows" in task else ("run",)
        _, runs = run_entries(task, fields)
        pre = resolve(task["depends"], tasks)
        post = resolve(task.get("depends_post", []), tasks)
        calls[name] = pre + post + resolve(runs, tasks)
        order[name] = pre + resolve(runs, tasks) + resolve(task.get("wait_for", []), tasks)
        posts[name] = post
    for parent, children in posts.items():
        for child in children:
            order[child].append(parent)
    return calls, order


def cycle(graph):
    try:
        graphlib.TopologicalSorter(graph).prepare()
    except graphlib.CycleError as error:
        return error.args[1]
    return None


def structure_problems(tasks):
    found = []
    for name, task in tasks.items():
        try:
            check_task(name, task, tasks)
        except (ValueError, TypeError) as error:
            found.append(f"tasks.{name}: {error}")
    return found


def check_task(name, task, tasks):
    if not isinstance(task, dict):
        raise ValueError("task must be an object")
    for field in ("depends", "depends_post", "wait_for"):
        if not isinstance(task.get(field, [] if field != "depends" else None), list):
            raise ValueError(f"{field} must be an explicit array")
        resolve(task.get(field, []), tasks)
    if not task.get("description"):
        raise ValueError("description is required")
    commands, runs = run_entries(task)
    resolve(runs, tasks)
    if any(re.search(r"\bmise\s+(?:run|r)\b", command) for command in commands):
        raise ValueError("run must not invoke Mise")
