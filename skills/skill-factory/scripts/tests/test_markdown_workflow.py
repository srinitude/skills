"""Public task and model-evidence checks; fixtures are not human approval."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASES = ["inventory", "mechanical", "review-request", "macro-review", "micro-review",
          "line-review", "review-check", "accept"]
PRIMITIVES = ["primitive_what", "primitive_which", "primitive_when", "primitive_how",
              "primitive_why", "primitive_who", "primitive_coverage"]


def binding(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def fixture(base):
    root, state = base / "skill", base / "state"
    root.mkdir()
    state.mkdir(mode=0o700)
    body = root / "SKILL.md"
    body.write_text("# Read this\n\nRead the file. Run the test. Fix the bug.\n")
    source, render = base / "source.txt", base / "render.svg"
    source.write_text("Keep each rule. Use plain words. Check the page.")
    render.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Read this</text></svg>')
    context = [{**binding(source), "role": role} for role in ["source", "ledger", "graph", "policy"]]
    context += [{**binding(body), "role": "body"}, {**binding(render), "role": "render", "subject": str(body)}]
    request = {"run_id": "fixture", "turn": "fixture-turn", "baseline": "fixture-baseline",
               "iteration": 0, "obligation": "WRITE-16/17 fixture", "roots": [str(root)], "context": context}
    path = base / "request.json"
    path.write_text(json.dumps(request))
    env = {**os.environ, "SKILL_MARKDOWN_REQUEST": str(path), "SKILL_MARKDOWN_STATE": str(state),
           "UV_PYTHON": sys.executable}
    return request, env


def invoke(phase, env, public=False, root=ROOT):
    command = ["mise", "run", *([] if public else ["--skip-deps"]), "markdown:" + phase]
    result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True, timeout=180)
    lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
    parsed = json.loads(lines[-1]) if lines else {}
    return result.returncode, parsed, result.stderr


def reply_for(data, phase="review-check"):
    stages = {"macro-review": ["capability_ownership", "task_dependencies", "purpose", "primitive_which", "primitive_why", "primitive_who",
              "primitive_coverage", "action", "first_load", "integration"],
              "micro-review": ["structure", "primitive_what", "primitive_when", "primitive_how", "meaning", "rendering"],
              "line-review": ["language", "exclusions"]}
    answers = {key: {"state": "pass", "reason": "Synthetic validator fixture; not real reader proof.",
                     "citations": []} for key in ["meaning", "action", "language", "rendering",
                                                 "first_load", "integration", "exclusions"] + PRIMITIVES + ["purpose", "structure", "capability_ownership", "task_dependencies"]}
    answers = {k: v for k, v in answers.items() if k in stages.get(phase, answers)}
    file = data["report"]["files"][0]
    cite = {"path": file["path"], "sha256": file["sha256"], "quote": "Read the file."}
    render = next(x for x in data["context"] if x["role"] == "render")
    for key in answers:
        answers[key]["citations"] = [cite] if key != "rendering" else [
            {"path": render["path"], "sha256": render["sha256"]}]
    return {"run_id": data["request"]["run_id"] + ":" + phase,
            "request_sha256": data["request_sha256"], "reviewer": "test fixture",
            "method": "consumer rejection fixture", "files": [
                {"path": file["path"], "sha256": file["sha256"], "answers": answers}]}


def check_review_cases(data):
    valid = reply_for(data)
    cases = []
    for key in ["run", "hash", "missing", "duplicate", "pending", "capability_pending", "dependencies_pending", "cite", "quote", "render"] + PRIMITIVES + ["purpose", "structure", "capability_ownership", "task_dependencies"]:
        bad = json.loads(json.dumps(valid))
        answers = bad["files"][0]["answers"]
        if key == "run": bad["run_id"] = "wrong"
        if key == "hash": bad["request_sha256"] = "0" * 64
        if key == "missing": del answers["meaning"]
        if key in PRIMITIVES + ["purpose", "structure", "capability_ownership", "task_dependencies"]: del answers[key]
        if key == "duplicate": bad["files"].append(bad["files"][0])
        if key in ("pending", "capability_pending", "dependencies_pending"): answers[{"pending": "meaning", "capability_pending": "capability_ownership", "dependencies_pending": "task_dependencies"}[key]]["state"] = "pending"
        if key == "cite": answers["meaning"]["citations"] = []
        if key == "quote": answers["meaning"]["citations"][0]["quote"] = "Not in the file"
        if key == "render": answers["rendering"]["citations"] = answers["meaning"]["citations"]
        cases.append(bad)
    code = ("import {validateReview} from './scripts/markdown_workflow.ts';"
            "let raw='';for await(const part of process.stdin)raw+=part;"
            "const {data,cases}=JSON.parse(raw);"
            "for(const value of cases){let rejected=false;try{validateReview(data,value)}"
            "catch{rejected=true}if(!rejected)throw Error('Bad review passed')}")
    result = subprocess.run(["node", "--input-type=module", "-e", code], cwd=ROOT,
                            input=json.dumps({"data": data, "cases": cases}),
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert set(data["report"]["runtime"]["validator_files"]) >= {
        "markdown_workflow.ts", "run_markdown.ts", "../package-lock.json"}


def test_declared_dependency_chain():
    tasks = tomllib.loads((ROOT / "mise.toml").read_text())["tasks"]
    previous = "check-runtime"
    for phase in PHASES:
        task = tasks["markdown:" + phase]
        assert task["depends"] == [previous]
        assert "mise run" not in task["run"]
        previous = "markdown:" + phase


def test_real_tasks_suspend_resume_and_reject_stale_files():
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary).resolve()
        request, env = fixture(base)
        code, data, error = invoke("review-request", env, public=True)
        assert code == 0, error + str(data)
        check_review_cases(data["result"])
        complete_reviews(base, env, data["result"])
        code, checked, error = invoke("review-check", env)
        assert code == 0, error + str(checked)
        code, accepted, error = invoke("accept", env)
        assert code == 0 and accepted["execution_acceptance"] == "pending", error + str(accepted)
        body = Path(request["roots"][0]) / "SKILL.md"
        body.write_text(body.read_text() + "\nA new rule.\n")
        code, stale, error = invoke("accept", env)
        assert code != 0, str(stale)


def complete_reviews(base, env, data, root=ROOT):
    for phase in ["macro-review", "micro-review", "line-review"]:
        code, waiting, error = invoke(phase, env, root=root)
        assert code == 3 and waiting["status"] == "suspended", error + str(waiting)
        reply = base / (phase + ".json")
        reply.write_text(json.dumps(reply_for(data, phase)))
        env["SKILL_MARKDOWN_REPLY"] = str(reply)
        code, resumed, error = invoke(phase, env, root=root)
        assert code == 0 and resumed["status"] == "success", error + str(resumed)


def test_consumer_rejects_skipped_prerequisite():
    with tempfile.TemporaryDirectory() as temporary:
        _, env = fixture(Path(temporary).resolve())
        code, data, error = invoke("mechanical", env)
        assert code != 0 and data.get("status") == "failed", error + str(data)


def test_generated_and_updated_markdown_owners_are_complete():
    sys.path.insert(0, str(ROOT / "scripts"))
    from scaffold_skill import source_files
    from standardization_mise import normalize_mise
    from standardization_runtime import ROOT_FILES, LEDGER_FILES
    from standardization_seed import base_mise
    required = {"markdown_checks.py", "markdown_workflow.ts", "run_markdown.ts",
                "standardization_workflow.ts", "run_standardization.ts"}
    assert required <= set(LEDGER_FILES)
    files = {destination for destination, _, _ in source_files()}
    assert {"scripts/" + name for name in required} <= files
    assert {"runtime/standardization/package.json", "runtime/standardization/package-lock.json"} <= set(ROOT_FILES)
    configs = [(ROOT / "assets/mise-template.toml").read_text(),
               normalize_mise(base_mise({"primary_term": "note"}))]
    for raw in configs:
        tasks = tomllib.loads(raw)["tasks"]
        previous = "check-runtime"
        for phase in PHASES:
            task = tasks["markdown:" + phase]
            assert task["depends"] == [previous]
            assert task["run"] == "node scripts/run_markdown.ts " + phase
            assert task["env"]["UV_PYTHON"] == "{{tools.python.path}}"
            previous = "markdown:" + phase
        assert "runtime/standardization" in str(tasks["setup-runtime"]["run"])


def test_generated_skill_runs_its_own_markdown_tasks():
    from test_scaffold_skill import scaffold
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary).resolve()
        result = scaffold(base, "markdown-trial", "Use when a Markdown trial is requested.")
        assert result.returncode == 0, result.stderr + result.stdout
        root = base / "markdown-trial"
        review = base / "review"
        review.mkdir()
        _, env = fixture(review)
        env["MISE_TRUSTED_CONFIG_PATHS"] = str(root)
        result = subprocess.run(["mise", "run", "markdown:review-request"], cwd=root, env=env,
                                text=True, capture_output=True, timeout=180)
        assert result.returncode == 0, result.stderr + result.stdout
        data = json.loads([line for line in result.stdout.splitlines() if line.startswith("{")][-1])
        assert data["status"] == "success" and set(PRIMITIVES) <= set(data["questions"])
        assert data["execution_acceptance"] == "pending"
        runtime = data["result"]["report"]["runtime"]["validator_files"]
        assert runtime["markdown_workflow.ts"] == binding(root / "scripts/markdown_workflow.ts")["sha256"]
        complete_reviews(base, env, data["result"], root)
        assert all(invoke(phase, env, root=root)[0] == 0 for phase in ["review-check", "accept"])


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(test) for test in [
        test_declared_dependency_chain, test_real_tasks_suspend_resume_and_reject_stale_files,
        test_consumer_rejects_skipped_prerequisite, test_generated_and_updated_markdown_owners_are_complete,
        test_generated_skill_runs_its_own_markdown_tasks])
