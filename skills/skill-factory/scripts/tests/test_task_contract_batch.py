"""Real native batch discovery retains each task's command and source checks."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_task_tools import ROOT, task


CODE = """
import assert from 'node:assert/strict';
import {writeFile,readFile,rename,symlink} from 'node:fs/promises';
import {taskContracts,taskContract} from './scripts/standardization_workflow.ts';
const root=process.argv[1], config=root+'/mise.toml';
const requests=['first','next'].map(name=>({name,command:'echo '+name,depends:name==='next'?['first']:[]}));
const both=await taskContracts(root,requests);
assert.equal(both.length,2);assert.equal(both[0].revision,both[1].revision);
assert.deepEqual(both[1],await taskContract(root,'next','echo next',['first']));
await assert.rejects(()=>taskContracts(root,[{...requests[1],command:'echo forged'}]),/does not match/);
await assert.rejects(()=>taskContracts(root,[{...requests[1],depends:[]}]),/does not match/);
await writeFile(config,(await readFile(config,'utf8'))+'\\n# reviewed source change\\n');
assert.notEqual((await taskContracts(root,requests))[0].revision,both[0].revision);
await rename(config,root+'/saved.toml');await symlink('saved.toml',config);
await assert.rejects(()=>taskContracts(root,requests),/regular bound input/);
console.log(JSON.stringify({status:'PASS',claims:'native batch bindings and rejection only'}));
"""


def test_batch_contracts():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        (root / "mise.toml").write_text(task("first", "echo first") + task("next", "echo next", ["first"]))
        result = subprocess.run(["node", "--input-type=module", "-e", CODE, str(root)], cwd=ROOT,
                                env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)},
                                text=True, capture_output=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout)["status"] == "PASS"


def load_tests(loader, tests, pattern):
    return unittest.TestSuite([unittest.FunctionTestCase(test_batch_contracts)])
