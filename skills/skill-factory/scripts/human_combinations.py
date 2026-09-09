"""Resolve finite symbolic spaces using the standard combinatorial vocabulary."""
import hashlib
import itertools
import json
import math
import sys

from human_matrix_records import identifiers, index, references, shape, text
from human_matrix_budget import check, metrics
from source_coverage import require

OPERATORS = {"product", "permutations", "combinations", "combinations_with_replacement"}


def pool(value, concepts, catalogs):
    require(isinstance(value, dict) and set(value) in [{"ids"}, {"catalog"}], "invalid selector pool")
    if "ids" in value:
        values = identifiers(value["ids"], "selector pool")
        references(values, concepts, "selector concept")
        return values
    name = value["catalog"]
    require(isinstance(name, str) and name in catalogs, "unknown selector catalog")
    return sorted(identifier for identifier in concepts if identifier.startswith(name + "/"))


def spaces(values, concepts, catalogs, resolved):
    result = []
    for item in index(values, "selector").values():
        shape(item, {"id", "operator", "pools", "length", "conditions", "role", "semantics"}, "selector")
        operator = item["operator"]
        require(operator in OPERATORS, "unsupported finite selector operator")
        require(type(item["length"]) is int and item["length"] >= 0, "selector length must be a finite nonnegative integer")
        require(isinstance(item["pools"], list) and bool(item["pools"]), "selector needs finite input pools")
        require(operator == "product" or len(item["pools"]) == 1, "this selector requires one pool")
        semantics = "ordered" if operator in {"product", "permutations"} else "unordered"
        require(item["semantics"] == semantics, "selector grouping semantics differ from operator")
        text(item["role"], "selector role")
        references(item["conditions"], resolved, "selector condition")
        item["conditions"].sort()
        pools = [pool(value, concepts, catalogs) for value in item["pools"]]
        digest = hashlib.sha256(json.dumps(pools, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        result.append({"id": item["id"], "pool_sizes": list(map(len, pools)), "pool_sha256": digest,
                       "pools": pools, "rule": item, "state": "symbolic", "identity": "input-position"})
    return sorted(result, key=lambda item: item["id"])


def choose_count(n, r, maximum):
    if r > n:
        return 0
    require(min(r, n - r) <= maximum.bit_length(), "enumeration member budget exceeded")
    return math.comb(n, r)


def cardinality(space, limits):
    sizes, rule = space["pool_sizes"], space["rule"]
    n, length, operator = sizes[0], rule["length"], rule["operator"]
    maximum = limits["max-members"]
    if length == 0:
        return 1
    if not n or operator == "product" and 0 in sizes:
        return 0
    if operator in {"permutations", "combinations"} and length > n:
        return 0
    width = length * (len(sizes) if operator == "product" else 1)
    require(width * 8 <= limits["max-memory-bytes"] and width * 2 <= limits["max-output-bytes"],
            "enumeration member width exceeds budget")
    if operator == "product":
        size = math.prod(sizes)
        require((size.bit_length() - 1) * length <= maximum.bit_length(), "enumeration member budget exceeded")
        return pow(size, length)
    if operator == "permutations":
        require(length - 1 <= maximum.bit_length(), "enumeration member budget exceeded")
        return math.perm(n, length)
    return choose_count(n if operator == "combinations" else n + length - 1, length, maximum)


def positions(space):
    pools = [list(range(len(pool))) for pool in space["pools"]]
    rule = space["rule"]
    if rule["operator"] == "product":
        for member in itertools.product(*pools, repeat=rule["length"]):
            yield [(number % len(pools), index) for number, index in enumerate(member)]
    else:
        for member in getattr(itertools, rule["operator"])(pools[0], rule["length"]):
            yield [(0, index) for index in member]


def member_record(space, rank, positions, matrix_sha):
    rule = space["rule"]
    group_id = rule["id"] + "/member-" + str(rank)
    ids = [group_id + "/occurrence-" + str(number) for number in range(len(positions))]
    instances = [{"id": identifier, "concept": space["pools"][pool][index],
                  "role": rule["role"], "conditions": rule["conditions"]}
                 for identifier, (pool, index) in zip(ids, positions)]
    group = {"id": group_id, "semantics": rule["semantics"],
             "members": sorted(ids) if rule["semantics"] == "unordered" else ids}
    return {"address": {"selector": rule["id"], "rank": str(rank), "matrix_sha256": matrix_sha,
                        "pool_sha256": space["pool_sha256"]}, "occurrences": instances, "groups": [group],
            "positions": [{"occurrence": identifier, "pool": pool, "index": index}
                          for identifier, (pool, index) in zip(ids, positions)]}


def input_pool_bytes(pools):
    objects = [pools, *pools, *(value for pool in pools for value in pool)]
    seen, total = set(), 0
    for value in objects:
        if id(value) not in seen:
            total += sys.getsizeof(value)
            seen.add(id(value))
    return total


def enumerate_space(result, identifier, budget):
    selected = [space for space in result["spaces"] if space["id"] == identifier]
    require(len(selected) == 1, "unknown enumeration selector")
    space = selected[0]
    count = cardinality(space, budget["limits"])
    require(count <= budget["limits"]["max-members"], "enumeration member budget exceeded")
    check(budget)
    members, size = [], 0
    for rank, positions_value in enumerate(positions(space) if count else ()):
        record = member_record(space, rank, positions_value, result["canonical_sha256"])
        size += len(json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode())
        require(size <= budget["limits"]["max-output-bytes"], "enumeration output budget exceeded")
        members.append(record)
        check(budget)
    require(len(members) == count, "enumeration cardinality differs from the complete result")
    return {"state": "complete", "selector": identifier, "count": str(count), "members": members,
            "budgets": budget["limits"], "metrics": metrics(budget, input_pool_bytes(space["pools"])),
            "runtime": {"python": sys.version.split()[0], "platform": sys.platform, "iterator": "itertools"},
            "scope": "enumeration only; no activity performed, evidence accepted or human outcome observed"}
