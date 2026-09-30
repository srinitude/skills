"""Check declared required-read cycles and file reachability."""


def visit_path(start, graph, state, found):
    path = [start]
    state[start] = 1
    pending = [(start, iter(graph[start]))]
    while pending:
        node, targets = pending[-1]
        try:
            target = next(targets)
        except StopIteration:
            pending.pop()
            path.pop()
            state[node] = 2
            continue
        if state.get(target) == 1:
            found.append(path[path.index(target):] + [target])
        elif state.get(target) != 2:
            state[target] = 1
            path.append(target)
            pending.append((target, iter(graph[target])))


def required_cycles(edges):
    """Only the current active path is a cycle; completed reads can recur."""
    graph = {}
    for source, target in edges:
        graph.setdefault(source, []).append(target)
        graph.setdefault(target, [])
    state, found = {}, []
    for node in graph:
        if node not in state:
            visit_path(node, graph, state, found)
    return found


def check_reachability(starts, actual, reading_routes, result):
    if not starts:
        result["needs_review"].append("No entrypoints supplied; file reachability was not checked")
        return
    routes = {}
    for source, target in reading_routes:
        routes.setdefault(source, set()).add(target)
    reached, pending = set(), list(starts)
    while pending:
        node = pending.pop()
        if node not in reached:
            reached.add(node)
            pending.extend(routes.get(node, set()) - reached)
    result["errors"].extend(
        f"Markdown file is unreachable from entrypoints: {p}" for p in sorted(actual - reached))
