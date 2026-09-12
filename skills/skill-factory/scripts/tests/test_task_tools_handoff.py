"""Real persisted Mastra handoffs over individual task tools; no human proof."""
import json
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_task_tools import ROOT, call, task, tool_call

WORKFLOW = """
import {createWorkflow,createStep} from '@mastra/core/workflows';
import {Mastra} from '@mastra/core';
import {z} from 'zod';
import {appendFile} from 'node:fs/promises';
import {openStorage} from './scripts/run_standardization.ts';
const storage=await openStorage(process.env.SKILL_STATE);
try {
  const owner=process.env.SKILL_OWNER, runId='handoff-'+owner;
  const reply=z.object({decision:z.literal('reviewed')});
  const step=createStep({id:'review',inputSchema:z.object({}),outputSchema:z.object({done:z.boolean()}),
    resumeSchema:reply,suspendSchema:z.object({owner:z.string(),instructions:z.string()}),
    execute:async({resumeData,suspend})=>{
      if(!resumeData)return await suspend({owner,instructions:'Review the bound fixture.'});
      await appendFile(process.env.SKILL_STATE+'/effects',owner+'\\n');return {done:true};
    }});
  const workflow=createWorkflow({id:'handoff',inputSchema:z.object({}),outputSchema:z.object({done:z.boolean()})}).then(step).commit();
  const mastra=new Mastra({workflows:{handoff:workflow},storage,logger:false});
  const selected=mastra.getWorkflow('handoff'), saved=await selected.getWorkflowRunById(runId);
  const run=await selected.createRun({runId});
  const result=saved?.status==='success'?saved: saved
    ?await run.resume({step:'review',resumeData:reply.parse(JSON.parse(process.env.SKILL_REPLY))})
    :await run.start({inputData:{}});
  console.log(JSON.stringify({...result,run_id:runId}));
  process.exitCode=result.status==='success'?0:result.status==='suspended'?3:1;
} finally {await storage.close();}
"""

def inspect_run(child, name, env):
    inspected = tool_call(child, name, action="inspect", env=env)["structuredContent"]
    return tool_call(child, name, action="run", env=env, revision=inspected["revision"])

def check_handoffs(child, state):
    base = {"SKILL_STATE": str(state)}
    for owner in ["human", "model"]:
        response = inspect_run(child, "task_handoff", {**base, "SKILL_OWNER": owner})
        assert not response["isError"], response
        data = response["structuredContent"]
        assert data["status"] == "suspended" and data["exit_code"] == 3, data
        assert data["workflow"]["run_id"] == "handoff-" + owner
        assert data["execution_acceptance"] == "pending"
        assert data["workflow"]["suspendPayload"]["review"]["owner"] == owner
    assert not (state / "effects").exists()
    invalid = inspect_run(child, "task_handoff", {**base, "SKILL_OWNER": "model", "SKILL_REPLY": "{}"})
    assert invalid["isError"] and not (state / "effects").exists()
    env = {**base, "SKILL_OWNER": "model", "SKILL_REPLY": '{"decision":"reviewed"}'}
    for _ in range(2):
        response = inspect_run(child, "task_handoff", env)
        assert not response["isError"] and response["structuredContent"]["exit_code"] == 0, response
        assert (state / "effects").read_text() == "model\n"

def check_invalid_pauses(child):
    for name in ["task_bare", "task_unbound"]:
        response = inspect_run(child, name, {})
        assert response["isError"] and response["structuredContent"]["exit_code"] == 3, response

def test_real_workflow_handoff():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        state = root / "state"
        state.mkdir(mode=0o700)
        command = "node --input-type=module -e " + shlex.quote(WORKFLOW)
        config = task("handoff", command) + "dir = " + json.dumps(str(ROOT)) + "\n"
        config += task("bare", "exit 3")
        config += task("unbound", "printf '%s\\n' '{\"status\":\"suspended\"}'; exit 3")
        (root / "mise.toml").write_text(config)
        code = ("import {createTaskTools} from './scripts/task_tools.ts';"
                "import {StdioServerTransport} from '@modelcontextprotocol/server/stdio';"
                "const {server}=await createTaskTools(process.argv[1]);"
                "await server.connect(new StdioServerTransport());")
        env = {**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)}
        with subprocess.Popen(["node", "--input-type=module", "-e", code, str(root)], cwd=ROOT, env=env,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, bufsize=1) as child:
            run_cases(child, state)

def run_cases(child, state):
    try:
        call(child, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "handoff-contract-test", "version": "1"}})
        child.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        child.stdin.flush()
        check_invalid_pauses(child)
        check_handoffs(child, state)
    finally:
        child.terminate()
        child.wait(timeout=10)

def load_tests(loader, tests, pattern):
    return unittest.TestSuite([unittest.FunctionTestCase(test_real_workflow_handoff)])
