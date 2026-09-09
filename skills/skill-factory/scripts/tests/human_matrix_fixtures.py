"""Concrete matrix inputs for mechanical tests, with no human-outcome claim."""
import hashlib
import json
from pathlib import Path


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(base):
    evidence = base / "domain.json"
    digest = save(evidence, {"brief": "Explore repeated practice with explanations and writing.",
                            "counterevidence": "This fixture is not a study or a human observation."})
    record = {"path": str(evidence), "sha256": digest, "pointer": ["brief"]}
    occurrences = [{"id": name, "concept": concept, "role": role, "conditions": []} for name, concept, role in [
        ("psychology", "oecd-ford-2015/5.1", "study"), ("education", "oecd-ford-2015/5.3", "study"),
        ("practice-1", "icatus-2016/741", "activity"), ("practice-2", "icatus-2016/741", "activity"),
        ("write", "nist-ai-200-1-2024/content-creation", "activity")]]
    groups = [{"id": "study", "semantics": "unordered", "members": ["psychology", "education"]},
              {"id": "practice", "semantics": "ordered", "members": ["practice-1", "practice-2"]},
              {"id": "work", "semantics": "ordered", "members": ["practice", "write"]}]
    interaction = {"id": "practice-and-create", "study": ["study"], "work": ["work"],
                   "people": [], "context": ["brief"], "outcomes": [], "choices": [], "evidence": [],
                   "constraints": [], "judgments": [], "dependencies": [], "state": "unknown"}
    return {"version": 1, "comparator": "unicode-codepoint", "locale": "und", "extensions": [],
            "correspondences": [], "occurrences": occurrences, "groups": groups,
            "records": {"brief": record}, "interactions": [interaction], "selectors": []}


def selector(operator, length=2, ids=None):
    ids = ids if ids is not None else ["oecd-ford-2015/5.3", "oecd-ford-2015/5.1", "oecd-ford-2015/5.4"]
    return {"id": "space", "operator": operator, "pools": [{"ids": ids}], "length": length,
            "conditions": [], "role": "candidate", "semantics": "ordered" if operator in
            {"product", "permutations"} else "unordered"}


def query(base, document, bindings, extra=(), root=None):
    from test_human_catalogs import matrix
    resources, request = Path(base) / "resources.json", Path(base) / "matrix.json"
    save(resources, bindings)
    digest = save(request, document)
    arguments = ["--resources", resources, "--matrix", request, "--matrix-sha256", digest, *extra]
    return matrix(arguments, root) if root else matrix(arguments)
