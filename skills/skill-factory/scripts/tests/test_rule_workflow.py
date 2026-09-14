"""Real Mise/Mastra model-task handoff, input drift and dependency recovery."""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def task(name, dependencies):
    body = (f"# `{name}`\n\n## Why this runs\n\nRead the fixture source.\n\n"
            "## When to run\n\nRun this fixture case.\n\n## Inputs\n\nThe bound source.\n\n"
            "## Work\n\nRead the source and give a reason with real evidence.\n\n"
            "## Proof\n\nKeep the source binding; human acceptance stays pending.\n")
    return (f"[tasks.{json.dumps(name)}]\n"
            f"description = {json.dumps(body)}\n"
            f"depends = {json.dumps(dependencies)}\n"
            f"run = {json.dumps('node scripts/run_rule.ts ' + name)}\n")


def runtime_tasks():
    config = tomllib.loads((ROOT / "mise.toml").read_text())
    result = "[tools]\n" + "".join(f"{key} = {json.dumps(value)}\n" for key, value in config["tools"].items())
    for name in ["setup-runtime", "check-runtime"]:
        fields = config["tasks"][name]
        result += f"\n[tasks.{name}]\n"
        for key in ["description", "depends", "run"]:
            result += f"{key} = {json.dumps(fields[key])}\n"
    return result


def stop_tree(process):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       capture_output=True, check=True)


def run_bounded(args, *, cwd, env, timeout):
    with subprocess.Popen(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, start_new_session=os.name == "posix") as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as error:
            stop_tree(process)
            stdout, stderr = process.communicate()
            sys.stderr.write(stdout + stderr)
            raise subprocess.TimeoutExpired(args, timeout, stdout, stderr) from error
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def fixture(parent):
    root, state = parent / "skill", parent / "state"
    root.mkdir()
    state.mkdir(mode=0o700)
    shutil.copytree(ROOT / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "runtime/standardization", root / "runtime/standardization",
                    ignore=shutil.ignore_patterns("node_modules"))
    for name in ["package.json", "package-lock.json", "tsconfig.json"]:
        shutil.copy2(ROOT / name, root / name)
    (root / "SKILL.md").write_text("# Fixture\n\nRead this actual source.\n")
    (root / "mise.toml").write_text(runtime_tasks() + task("rule:read", ["check-runtime"]) + task("rule:next", ["rule:read"]))
    request = {"run_id": "fixture", "turn": "fixture-turn", "obligation": "read fixture",
               "context": [{"path": str(root / "SKILL.md"), "role": "body", "format": "text",
                            "sha256": hashlib.sha256((root / "SKILL.md").read_bytes()).hexdigest()}]}
    (parent / "request.json").write_text(json.dumps(request))
    installed = run_bounded(["mise", "run", "setup-runtime"], cwd=root,
                            env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)}, timeout=120)
    assert installed.returncode == 0, installed.stdout + installed.stderr
    return root, state


def invoke(root, state, name, reply=None, skip=False):
    env = {**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root), "UV_PYTHON": sys.executable,
           "SKILL_RULE_REQUEST": str(root.parent / "request.json"), "SKILL_RULE_STATE": str(state)}
    env.pop("SKILL_RULE_REPLY", None)
    if reply:
        env["SKILL_RULE_REPLY"] = str(reply)
    args = ["mise", "run", *(["--skip-deps"] if skip else []), name]
    result = run_bounded(args, cwd=root, env=env, timeout=60)
    lines = result.stdout.strip().splitlines()
    value = json.loads(lines[-1]) if lines else {}
    return result, value


def reply_for(parent, name, pending):
    source = parent / "skill/SKILL.md"
    record = {"task": name, "input_sha256": pending["input_sha256"], "reviewer": "fixture-only",
              "summary": "Read the fixture source; this is not real human or goal acceptance.",
              "evidence": [{"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}
    path = parent / (name.replace(":", "-") + ".json")
    path.write_text(json.dumps(record))
    return path


def check_body_binding(parent, root, state):
    path = parent / "request.json"
    original = json.loads(path.read_text())
    body = original["context"][0]
    other = {**body, "path": str(root / "package.json"),
             "sha256": hashlib.sha256((root / "package.json").read_bytes()).hexdigest()}
    cases = [[other], [{**body, "role": "reference"}],
             [{**body, "format": "bytes"}], [body, body]]
    try:
        for context in cases:
            path.write_text(json.dumps({**original, "context": context}))
            rejected, result = invoke(root, state, "rule:read")
            assert rejected.returncode == 1, rejected.stdout + rejected.stderr
            assert result.get("status") != "suspended", result
            assert "canonical SKILL.md" in rejected.stderr, rejected.stderr
    finally:
        path.write_text(json.dumps(original))


def check_parent(parent, root, state):
    missing, _ = invoke(root, state, "rule:next", skip=True)
    assert missing.returncode == 1 and "prerequisite" in missing.stderr.lower(), missing.stderr
    first, data = invoke(root, state, "rule:read")
    assert first.returncode == 3 and data["status"] == "suspended", first.stdout + first.stderr
    pending = data["suspendPayload"]["judgment"]
    assert "Read the source and give a reason" in pending["task"]["description"]
    assert pending["context"][0]["text"] == (root / "SKILL.md").read_text()
    repeated, waiting = invoke(root, state, "rule:read")
    assert repeated.returncode == 3 and waiting["suspended"] == [["judgment"]], waiting
    assert waiting["suspendPayload"]["judgment"] == pending
    reply = reply_for(parent, "rule:read", pending)
    broken = json.loads(reply.read_text())
    broken["input_sha256"] = "0" * 64
    reply.write_text(json.dumps(broken))
    rejected, _ = invoke(root, state, "rule:read", reply)
    assert rejected.returncode == 1, rejected.stdout + rejected.stderr
    reply = reply_for(parent, "rule:read", pending)
    valid, result = invoke(root, state, "rule:read", reply)
    assert valid.returncode == 0 and result["execution_acceptance"] == "pending", valid.stderr
    reused, result = invoke(root, state, "rule:read", reply)
    assert reused.returncode == 0 and result["reused"] is True, reused.stderr


def check_child(parent, root, state):
    started, data = invoke(root, state, "rule:next")
    assert started.returncode == 3, started.stdout + started.stderr
    pending = data["suspendPayload"]["judgment"]
    reply = reply_for(parent, "rule:next", pending)
    source = root / "SKILL.md"
    before = source.read_bytes()
    source.write_text("# Changed source\n")
    stale, _ = invoke(root, state, "rule:next", reply)
    assert stale.returncode == 1, stale.stdout + stale.stderr
    source.write_bytes(before)
    recovered, result = invoke(root, state, "rule:next", reply)
    assert recovered.returncode == 0 and result["execution_acceptance"] == "pending", recovered.stderr


def test_model_task_sequence_and_recovery():
    with tempfile.TemporaryDirectory() as temporary:
        parent = Path(temporary).resolve()
        root, state = fixture(parent)
        check_body_binding(parent, root, state)
        check_parent(parent, root, state)
        check_child(parent, root, state)


def test_timeout_stops_descendants_and_keeps_output():
    with tempfile.TemporaryDirectory() as temporary:
        parent = Path(temporary)
        child = "import time,pathlib; print('child-started',flush=True); time.sleep(2); pathlib.Path('late').touch()"
        program = ("import subprocess,sys,time; "
                   "subprocess.Popen([sys.executable,'-c',sys.argv[1]]); "
                   "print('parent-error',file=sys.stderr,flush=True); time.sleep(10)")
        with unittest.TestCase().assertRaises(subprocess.TimeoutExpired) as caught:
            run_bounded([sys.executable, "-c", program, child], cwd=parent, env=os.environ, timeout=1)
        assert "child-started" in caught.exception.output
        assert "parent-error" in caught.exception.stderr
        time.sleep(2)
        assert not (parent / "late").exists(), "A descendant kept writing after timeout"
        completed = run_bounded([sys.executable, "-c", "print('recovered')"],
                                cwd=parent, env=os.environ, timeout=5)
        assert completed.returncode == 0 and completed.stdout.strip() == "recovered"


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(map(unittest.FunctionTestCase, [test_timeout_stops_descendants_and_keeps_output,
                                                            test_model_task_sequence_and_recovery]))
