"""Prove included task rules reach graph and invocation checks through native Mise."""
import json
import os
import shutil
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_task_graph_policy import contract, task_text
from test_invocation_receipt import receipt, task_file

ROOT = Path(__file__).resolve().parents[2]


def grouped(root, text):
    (root / "assets").mkdir()
    (root / "mise.toml").write_text('[task_config]\nincludes = ["rules.toml"]\n')
    (root / "rules.toml").write_text(text.replace("[tasks.", "["))


def invoke(script, root, *args):
    return run(script, root, *args, env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)})


def graph_case(root, text, expected, fragment):
    (root / "rules.toml").write_text(text.replace("[tasks.", "["))
    result = invoke("check_task_graph.py", root)
    assert result.returncode == expected, result.stdout + result.stderr
    assert fragment in result.stdout, result.stdout
    assert "Traceback" not in result.stderr, result.stderr


def test_included_graph_and_recovery():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        grouped(root, task_text())
        (root / "assets/use-case-contract.json").write_text(json.dumps(contract()))
        graph_case(root, task_text(), 0, "0 problems")
        cycle = task_text().replace('depends = []\nrun = "python3 scripts/tests.py"',
                                    'depends = ["ci"]\nrun = "python3 scripts/tests.py"')
        graph_case(root, cycle, 1, "cycle")
        missing = task_text().replace('depends = []\nrun = "python3 scripts/tests.py"',
                                      'run = "python3 scripts/tests.py"')
        graph_case(root, missing, 1, "dependencies must be explicit arrays")
        graph_case(root, task_text(), 0, "0 problems")


def test_included_invocation_omission_and_recovery():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        grouped(root, task_file())
        (root / "assets/use-case-contract.json").write_text('{"domain_terms":["release notes"]}')
        data = receipt()
        data["skill"] = root.name
        path = root / "receipt.json"
        path.write_text(json.dumps(data))
        passed = invoke("check_invocation_receipt.py", root, path)
        assert passed.returncode == 0, passed.stdout + passed.stderr
        data["entries"].pop()
        path.write_text(json.dumps(data))
        failed = invoke("check_invocation_receipt.py", root, path)
        assert failed.returncode == 1 and "missing tasks: info" in failed.stdout, failed.stdout
        data["entries"] = receipt()["entries"]
        path.write_text(json.dumps(data))
        recovered = invoke("check_invocation_receipt.py", root, path)
        assert recovered.returncode == 0, recovered.stdout + recovered.stderr


def test_native_fields_keep_raw_dependency_requirements():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        grouped(root, task_text())
        listed = subprocess.run(["mise", "-C", str(root), "tasks", "ls", "--hidden", "--json"],
                                capture_output=True, text=True, check=True,
                                env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)})
        names = {item["name"] for item in json.loads(listed.stdout)}
        assert set(contract()["task_graph"]["tasks"]) <= names
        (root / "assets/use-case-contract.json").write_text(json.dumps(contract()))
        invalid = task_text().replace('depends = ["test", "decision-policy"]',
                                      'depends = ["test", "decision-policy"]\nwait_for = ["test"]')
        graph_case(root, invalid, 1, "wait_for is not modeled")
        (root / "rules.toml").unlink()
        (root / "rules.toml").symlink_to(root / "missing.toml")
        failed = invoke("check_task_graph.py", root)
        assert failed.returncode == 1 and "Traceback" not in failed.stderr
        (root / "rules.toml").unlink()
        graph_case(root, task_text(), 0, "0 problems")


def test_malformed_or_external_includes_fail_closed():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        grouped(root, task_text())
        (root / "assets/use-case-contract.json").write_text(json.dumps(contract()))
        config = root / "mise.toml"
        valid = config.read_text()
        for bad in ['task_config = "bad"\n', '[task_config]\nincludes = [1]\n',
                    '[task_config]\nincludes = ["../outside.toml"]\n']:
            config.write_text(bad)
            result = invoke("check_task_graph.py", root)
            assert result.returncode == 1, result.stdout + result.stderr
            assert "Traceback" not in result.stderr, result.stderr
        config.write_text(valid)
        graph_case(root, task_text(), 0, "0 problems")



def grouped_factory(root):
    shutil.copytree(ROOT / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "assets").mkdir()
    shutil.copy2(ROOT / "assets/mise-template.toml", root / "assets/mise-template.toml")
    sys.path.insert(0, str(ROOT / "scripts"))
    from standardization_runtime import split_sections, task_header
    preamble, sections = split_sections((ROOT / "mise.toml").read_text())
    selected = lambda name: name == "task-tools" or name.startswith("markdown:")
    normal = [task_header(name) + "\n" + block for name, block in sections if not selected(name)]
    groups = [task_header(name).replace("[tasks.", "[") + "\n" + block
              for name, block in sections if selected(name)]
    preamble = preamble.replace('includes = ["tasks/context.toml"]', 'includes = ["rules.toml"]')
    (root / "mise.toml").write_text(preamble + "\n\n" + "\n\n".join(normal))
    (root / "rules.toml").write_text("\n\n".join(groups))


def test_standardization_keeps_included_factory_instructions():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        grouped_factory(root)
        code = (
            "import json,tomllib; from standardization_mise import normalize_mise,FACTORY_TASKS; "
            "from standardization_seed import base_mise; "
            "from standardization_runtime import MARKDOWN_TASKS; "
            "tasks=tomllib.loads(normalize_mise(base_mise({'primary_term':'release notes'})))['tasks']; "
            "assert len(MARKDOWN_TASKS)==8; "
            "assert tasks['task-tools']['description']==FACTORY_TASKS['task-tools']['description']; "
            "assert all(tasks[n]['description']==t['description'] and "
            "tasks[n]['depends']==t['depends'] for n,t in MARKDOWN_TASKS.items()); "
            "print('included factory instructions preserved')"
        )
        result = subprocess.run([sys.executable, "-c", code], cwd=root / "scripts",
                                capture_output=True, text=True, timeout=30,
                                env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)})
        assert result.returncode == 0, result.stdout + result.stderr
        assert "included factory instructions preserved" in result.stdout


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(test) for test in [
        test_included_graph_and_recovery, test_included_invocation_omission_and_recovery,
        test_native_fields_keep_raw_dependency_requirements, test_malformed_or_external_includes_fail_closed,
        test_standardization_keeps_included_factory_instructions])
