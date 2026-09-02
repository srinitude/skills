"""Check design task links without a run."""


def dependencies(task):
    return task.get("depends", []) + task.get("depends_post", [])


def commands(task):
    value = task.get("run", "")
    if isinstance(value, str):
        return [value]
    return value if isinstance(value, list) else []


def structure_problems(tasks):
    found, names = [], set(tasks)
    for name, task in tasks.items():
        if not isinstance(task.get("depends"), list):
            found.append(f"design task {name} lacks a depends list")
            continue
        if not isinstance(task.get("depends_post", []), list):
            found.append(f"design task {name} has bad post links")
        if set(dependencies(task)) - names:
            found.append(f"design task {name} has an unknown link")
        if not task.get("description"):
            found.append(f"design task {name} lacks help text")
        if any("mise run" in command for command in commands(task)):
            found.append(f"design task {name} runs Mise inside Mise")
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
        found += [f"more than one path from {start} to {name}"
                  for name, count in counts.items() if count > 1]
    if reached != set(tasks):
        found.append("some design tasks have no path")
    return found
