"""Measure enumeration resources and reject exceeded budgets before emitting data."""
import json
import math
import time
import tracemalloc

from source_coverage import require

FLAGS = ["max-members", "max-output-bytes", "max-memory-bytes", "max-seconds"]


def arguments(parser):
    parser.add_argument("--enumerate", help="explicitly request every member of one finite selector")
    for flag in FLAGS:
        parser.add_argument("--" + flag, type=float if flag == "max-seconds" else int,
                            help="required enumeration budget; seconds may be fractional")


def start(args):
    limits = {flag: getattr(args, flag.replace("-", "_")) for flag in FLAGS}
    if not args.enumerate:
        require(all(value is None for value in limits.values()), "budgets require explicit enumeration")
        return None
    require(args.operation == "matrix", "enumeration requires a bound matrix")
    require(all(type(limits[flag]) is int and limits[flag] >= (0 if flag == "max-members" else 1)
                for flag in FLAGS[:-1]), "every enumeration budget is required")
    seconds = limits["max-seconds"]
    require(type(seconds) is float and math.isfinite(seconds) and seconds > 0,
            "time budget must be finite positive seconds")
    tracemalloc.start()
    return {"limits": limits, "started": time.monotonic()}


def check(budget):
    if budget is None:
        return
    limits = budget["limits"]
    require(time.monotonic() - budget["started"] <= limits["max-seconds"], "enumeration time budget exceeded")
    peak = tracemalloc.get_traced_memory()[1]
    require(peak + tracemalloc.get_tracemalloc_memory() <= limits["max-memory-bytes"],
            "enumeration memory budget exceeded")


def metrics(budget, pool_bytes):
    check(budget)
    return {"peak_traced_bytes": tracemalloc.get_traced_memory()[1],
            "tracer_bytes": tracemalloc.get_tracemalloc_memory(), "input_pool_bytes": pool_bytes,
            "elapsed_seconds": time.monotonic() - budget["started"],
            "memory_scope": "Python allocations since source resolution plus tracer metadata; not process RSS",
            "enforcement": "preflight and observed budget checks before output; not an operating-system limit"}


def emit(result, budget):
    if budget is not None:
        result["enumeration"]["metrics"] = metrics(budget, result["enumeration"]["metrics"]["input_pool_bytes"])
    output = json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n"
    if budget is not None:
        require(len(output.encode()) <= budget["limits"]["max-output-bytes"], "enumeration output budget exceeded")
        check(budget)
    print(output, end="")
