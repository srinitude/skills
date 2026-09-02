"""Check the Figma skill Mise task graph."""


def dependencies(task):
    return task.get("depends", []) + task.get("depends_post", [])


def visit(tasks, name, state, trail):
    if state.get(name) == 1:
        return trail[trail.index(name):] + [name]
    if state.get(name) == 2:
        return None
    state[name] = 1
    for link in dependencies(tasks[name]):
        cycle = visit(tasks, link, state, trail + [name])
        if cycle:
            return cycle
    state[name] = 2
    return None


def find_cycle(tasks):
    for name in tasks:
        cycle = visit(tasks, name, {}, [])
        if cycle:
            return cycle
    return None


def path_counts(tasks, start):
    counts, pending = {start: 1}, [start]
    while pending:
        name = pending.pop(0)
        for link in dependencies(tasks[name]):
            before = counts.get(link, 0)
            counts[link] = min(2, before + counts[name])
            if not before:
                pending.append(link)
    return counts


def structure(tasks):
    found, names = [], set(tasks)
    for name, task in tasks.items():
        if not isinstance(task.get("depends"), list):
            found.append(f"Figma task {name} lacks a depends list")
        if set(dependencies(task)) - names:
            found.append(f"Figma task {name} has an unknown link")
        commands = task.get("run", [])
        commands = [commands] if isinstance(commands, str) else commands
        if any("mise run" in command for command in commands):
            found.append(f"Figma task {name} runs Mise inside Mise")
    return found


def graph(data, _, __, ___, ____, _____, tasks, root=None):
    found, reached = structure(tasks), set()
    if any("unknown link" in item for item in found):
        return found
    if find_cycle(tasks):
        return found + ["Figma task graph has a loop"]
    starts = [data["task_graph"]["ci_task"]]
    starts += [item["task"] for item in data["task_graph"]["public_operations"]]
    for start in starts:
        counts = path_counts(tasks, start)
        reached |= set(counts)
        if any(value > 1 for value in counts.values()):
            found.append(f"Figma task path from {start} is not unique")
    if reached != set(tasks):
        found.append("Some Figma tasks have no public path")
    return found
