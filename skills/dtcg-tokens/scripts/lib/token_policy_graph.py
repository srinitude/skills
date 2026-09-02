"""Inspect DTCG Mise task dependencies without executing them."""


def dependencies(task):
    return task.get("depends", []) + task.get("depends_post", [])


def command_strings(task):
    value = task.get("run", "")
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def structure_problems(tasks):
    found, names = [], set(tasks)
    for name, task in tasks.items():
        if not isinstance(task.get("depends"), list):
            found.append(f"DTCG token task {name} lacks explicit dependencies")
            continue
        if not isinstance(task.get("depends_post", []), list):
            found.append(f"DTCG token task {name} has invalid post dependencies")
            continue
        if set(dependencies(task)) - names:
            found.append(f"DTCG token task {name} has an unknown dependency")
        if not task.get("description"):
            found.append(f"DTCG token task {name} lacks a description")
        if any("mise run" in command for command in command_strings(task)):
            found.append(f"DTCG token task {name} nests Mise")
    return found


def visit(tasks, name, states, trail):
    if states.get(name) == 1:
        return trail[trail.index(name):] + [name]
    if states.get(name) == 2:
        return None
    states[name] = 1
    trail.append(name)
    for dependency in dependencies(tasks[name]):
        if dependency in tasks:
            cycle = visit(tasks, dependency, states, trail)
            if cycle:
                return cycle
    trail.pop()
    states[name] = 2
    return None


def find_cycle(tasks):
    states, trail = {}, []
    for name in tasks:
        cycle = visit(tasks, name, states, trail)
        if cycle:
            return cycle
    return None


def reachable(tasks, starts):
    reached, pending = set(), list(starts)
    while pending:
        name = pending.pop()
        if name in reached or name not in tasks:
            continue
        reached.add(name)
        pending.extend(dependencies(tasks[name]))
    return reached


def path_counts(tasks, start):
    active = reachable(tasks, [start])
    incoming = {name: 0 for name in active}
    for name in active:
        for dependency in dependencies(tasks[name]):
            if dependency in incoming:
                incoming[dependency] += 1
    ready, counts = [start], {name: 0 for name in active}
    counts[start] = 1
    while ready:
        name = ready.pop()
        for dependency in dependencies(tasks[name]):
            if dependency not in incoming:
                continue
            counts[dependency] = min(2, counts[dependency] + counts[name])
            incoming[dependency] -= 1
            if incoming[dependency] == 0:
                ready.append(dependency)
    return counts


def route_problems(tasks, starts):
    found, reached = [], set()
    for start in starts:
        if start not in tasks:
            continue
        counts = path_counts(tasks, start)
        reached.update(name for name, count in counts.items() if count)
        for name, count in counts.items():
            if count > 1:
                found.append(f"multiple dependency paths from {start} to {name}")
    if reached != set(tasks):
        found.append("DTCG token task graph has disconnected tasks")
    return found
