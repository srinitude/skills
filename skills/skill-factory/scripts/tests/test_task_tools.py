"""Real MCP task tools; temporary commands prove boundaries, not human judgment."""
import json
import os
import select
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def task(name, command, depends=()):
    body = f"# \x60{name}\x60\n\n"
    for heading, text in [("Why this runs", "Prove the task result."), ("When to run", "Check this task."),
                          ("Inputs", "Use the current request."), ("Work", "Run the named job."),
                          ("Proof", "Read its real output.")]:
        body += f"## {heading}\n\n{text}\n\n"
    return f"\n[tasks.{json.dumps(name)}]\ndescription = {json.dumps(body)}\nrun = {json.dumps(command)}\ndepends = {json.dumps(list(depends))}\n"

def receive(child, identity, timeout):
    while True:
        if not select.select([child.stdout], [], [], timeout)[0]:
            raise AssertionError("MCP response timed out")
        line = child.stdout.readline()
        if not line:
            raise AssertionError(child.stderr.read())
        value = json.loads(line)
        if value.get("id") == identity:
            return value

def call(child, method, params, timeout=15):
    identity = call.sequence
    call.sequence += 1
    child.stdin.write(json.dumps({"jsonrpc": "2.0", "id": identity, "method": method, "params": params}) + "\n")
    child.stdin.flush()
    return receive(child, identity, timeout)["result"]
call.sequence = 1

def tool_call(child, name, **arguments):
    return call(child, "tools/call", {"name": name, "arguments": arguments})

def exercise_environment(child, names, original):
    env = {"SKILL_REQUIRED_TASK": "hidden"}
    inspected = tool_call(child, names["last"], action="inspect", env=env)["structuredContent"]
    assert inspected["task"]["depends"] == ["hidden"], inspected["task"]["depends"]
    stale = tool_call(child, names["last"], action="run", env=env, revision=original["revision"])
    assert stale["isError"]
    ran = tool_call(child, names["last"], action="run", env=env, revision=inspected["revision"])
    assert not ran["isError"], ran
    output = ran["structuredContent"]["stdout"]
    assert output.index("HIDDEN") < output.index("LAST") and "FIRST" not in output

def exercise(child, config):
    tools = call(child, "tools/list", {})["tools"]
    assert {item["title"] for item in tools} == {"first", "last", "fails", "hidden"}
    names = {item["title"]: item["name"] for item in tools}
    inspected = tool_call(child, names["last"], action="inspect")
    proof = inspected["structuredContent"]
    assert proof["task"]["name"] == "last" and proof["task"]["depends"] == ["first"]
    assert "## Work" in proof["task"]["description"]
    denied = tool_call(child, names["last"], action="run", revision=proof["revision"][:-1])
    assert denied["isError"]
    result = tool_call(child, names["last"], action="run", revision=proof["revision"])["structuredContent"]
    assert result["exit_code"] == 0 and result["stdout"].index("FIRST") < result["stdout"].index("LAST")
    wrong = tool_call(child, names["first"], action="run", revision=proof["revision"])
    assert wrong["isError"]
    current = tool_call(child, names["fails"], action="inspect")["structuredContent"]
    failed = tool_call(child, names["fails"], action="run", revision=current["revision"])
    assert failed["isError"] and failed["structuredContent"]["exit_code"] != 0
    exercise_environment(child, names, proof)
    config.write_text(task("last", "echo CHANGED") + task("added", "echo ADDED"))
    stale = tool_call(child, names["last"], action="run", revision=proof["revision"])
    assert stale["isError"]
    listed = call(child, "tools/list", {})["tools"]
    assert {item["title"] for item in listed} == {"last", "added"}
    assert tool_call(child, names["first"], action="inspect").get("isError")
    fresh = tool_call(child, names["last"], action="inspect")["structuredContent"]
    fixed = tool_call(child, names["last"], action="run", revision=fresh["revision"])
    assert "CHANGED" in fixed["structuredContent"]["stdout"]

def run_protocol(child, config):
    try:
        call(child, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "skill-contract-test", "version": "1"}})
        child.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        child.stdin.flush()
        exercise(child, config)
    finally:
        child.terminate()
        child.wait(timeout=10)

def test_individual_live_tools():
    with tempfile.TemporaryDirectory() as temporary:
        parent = Path(temporary).resolve()
        (parent / "mise.toml").write_text(task("unrelated", "echo OUTSIDE"))
        root = parent / "skill"
        root.mkdir()
        config = root / "mise.toml"
        config.write_text(task("first", "echo FIRST") + task("last", "echo LAST", ["{{env.SKILL_REQUIRED_TASK | default(value='first')}}"]) + task("fails", "exit 7") + task("hidden", "echo HIDDEN") + "hide = true\n")
        code = ("import {createTaskTools} from './scripts/task_tools.ts';"
                "import {StdioServerTransport} from '@modelcontextprotocol/server/stdio';"
                "const {server}=await createTaskTools(process.argv[1]);"
                "await server.connect(new StdioServerTransport());")
        env = {**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(parent), "MISE_TASK_SKIP_DEPENDS": "1"}
        with subprocess.Popen(["node", "--input-type=module", "-e", code, str(root)], cwd=ROOT, env=env,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, bufsize=1) as child:
            run_protocol(child, config)


def test_grouped_task_contract():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        (root / "mise.toml").write_text('[task_config]\nincludes = ["group.toml"]\n')
        group = root / "group.toml"
        group.write_text(task("first", "echo FIRST").replace("[tasks.", "["))
        code = (
            "import assert from 'node:assert/strict';"
            "import {readFile,writeFile,rename,symlink} from 'node:fs/promises';"
            "import {taskContract} from './scripts/standardization_workflow.ts';"
            "const root=process.argv[1],group=root+'/group.toml',config=root+'/mise.toml';"
            "const inspect=()=>taskContract(root,'first','echo FIRST',[]);"
            "const first=await inspect();assert.equal(first.source,group);"
            "assert.equal(first.description.includes('## Work'),true);"
            "await writeFile(group,(await readFile(group,'utf8'))+'\\n# retained context\\n');"
            "const next=await inspect();assert.notEqual(next.revision,first.revision);"
            "assert.notEqual(next.sha256,first.sha256);"
            "await writeFile(config,(await readFile(config,'utf8'))+'\\n[env]\\nSKILL_REVIEW = \"current\"\\n');"
            "const changed=await inspect();assert.notEqual(changed.revision,next.revision);"
            "assert.equal(changed.sha256,next.sha256);"
            "await rename(group,root+'/outside.toml');await symlink('outside.toml',group);"
            "await assert.rejects(inspect,/regular bound input/);"
        )
        result = subprocess.run(["node", "--input-type=module", "-e", code, str(root)], cwd=ROOT,
                                env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)},
                                text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr

def close_entry(child):
    child.stdin.close()
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        child.terminate()
        child.wait(timeout=10)


def test_public_task_entry():
    env = {**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(ROOT)}
    with subprocess.Popen(["mise", "run", "task-tools"], cwd=ROOT, env=env,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, bufsize=1) as child:
        try:
            call(child, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                      "clientInfo": {"name": "public-entry-test", "version": "1"}}, timeout=180)
            child.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
            child.stdin.flush()
            listed = call(child, "tools/list", {})["tools"]
            names = {item["title"]: item["name"] for item in listed}
            assert "task-tools" in names and "check-runtime" in names
            inspected = tool_call(child, names["task-tools"], action="inspect")["structuredContent"]
            assert "## Work" in inspected["task"]["description"]
            denied = tool_call(child, names["task-tools"], action="run", revision=inspected["revision"])
            assert denied["isError"] and "nested tool connection" in denied["structuredContent"]["message"]
        finally:
            close_entry(child)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(test) for test in [
        test_individual_live_tools, test_grouped_task_contract, test_public_task_entry])
