"""Behavior tests for deterministic scaffolding around all 25 execution steps."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "run_pipeline.py"


class TestRunPipeline(unittest.TestCase):
    def run_script(self, *args, expected=0):
        self.assertTrue(SCRIPT.is_file(), "missing scripts/run_pipeline.py")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=SKILL_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return result

    def init_run(self, root):
        request = root / "request.json"
        request.write_text('{"request":"make tokens"}\n', encoding="utf-8")
        source = root / "source.txt"
        source.write_text("source bytes\n", encoding="utf-8")
        anchor = root / "anchor.json"
        anchor.write_text(
            '{"captured_at":"2026-08-27T14:51:45-04:00","date":"2026-08-27",'
            '"weekday":"Thursday","timezone":"EDT","utc_offset":"-04:00","source":"system-local"}\n',
            encoding="utf-8",
        )
        run = root / "demo.run.json"
        self.run_script(
            "init",
            "--run",
            str(run),
            "--run-id",
            "run-demo",
            "--name",
            "demo",
            "--request",
            str(request),
            "--source",
            str(source),
            "--anchor",
            str(anchor),
        )
        return run

    def block_step(self, run, code, expected=0):
        return self.run_script(
            "block", "--run", str(run), "--step", "S01",
            "--code", code, "--reason", "missing input",
            "--recovery", "supply input", expected=expected,
        )

    def test_init_creates_all_step_records_and_hashed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            run = self.init_run(pathlib.Path(directory))
            record = json.loads(run.read_text(encoding="utf-8"))
            self.assertEqual(record["run_id"], "run-demo")
            self.assertEqual(len(record["steps"]), 25)
            self.assertTrue(all(step["status"] == "PENDING" for step in record["steps"]))
            self.assertEqual(set(record["artifacts"]), {"request.packet", "source.payload"})
            for artifact in record["artifacts"].values():
                self.assertRegex(artifact["sha256"], r"^[a-f0-9]{64}$")

    def test_predecessor_and_named_output_gates_control_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            run = self.init_run(root)
            self.run_script("start", "--run", str(run), "--step", "S02", expected=1)
            self.run_script("start", "--run", str(run), "--step", "S01")
            self.run_script("pass", "--run", str(run), "--step", "S01", expected=1)
            contract = root / "run.contract.json"
            contract.write_text('{"frozen":true}\n', encoding="utf-8")
            self.run_script(
                "pass",
                "--run",
                str(run),
                "--step",
                "S01",
                "--output",
                f"run.contract={contract}",
            )
            self.run_script("start", "--run", str(run), "--step", "S02")
            record = json.loads(run.read_text(encoding="utf-8"))
            self.assertEqual(record["steps"][0]["status"], "PASS")
            self.assertEqual(record["steps"][1]["status"], "RUNNING")
            self.assertRegex(record["artifacts"]["run.contract"]["sha256"], r"^[a-f0-9]{64}$")

    def test_packet_lists_exact_inputs_outputs_and_support_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            run = self.init_run(root)
            packet = root / "S03.packet.json"
            self.run_script(
                "packet",
                "--run",
                str(run),
                "--step",
                "S03",
                "--output",
                str(packet),
            )
            payload = json.loads(packet.read_text(encoding="utf-8"))
            self.assertEqual(payload["step_id"], "S03")
            self.assertEqual(payload["produces"], ["vision.execution"])
            self.assertIn("references/vision-execution.md", payload["support_files"])
            self.assertIn("assets/vision-probe-manifest.json", payload["support_files"])
            self.assertEqual(payload["decision_owner"], "strong vision executor")

    def test_block_requires_an_allowed_code_and_records_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            run = self.init_run(root)
            self.run_script("start", "--run", str(run), "--step", "S01")
            self.block_step(run, "E_UNKNOWN", expected=1)
            self.block_step(run, "E_INPUT")
            record = json.loads(run.read_text(encoding="utf-8"))
            step = record["steps"][0]
            self.assertEqual(step["status"], "BLOCKED")
            self.assertEqual(step["error_code"], "E_INPUT")
            self.assertEqual(step["recovery"], "supply input")


class TestProgrammaticScaffoldingContract(unittest.TestCase):
    def test_every_step_routes_state_and_packet_work_through_the_runner(self):
        io_map = json.loads(
            (SKILL_DIR / "assets" / "execution-io-map.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(io_map["steps"]), 25)
        for step in io_map["steps"]:
            self.assertTrue(step.get("decision_owner"), f"{step['id']} needs a decision owner")
            self.assertIn(
                "scripts/run_pipeline.py",
                step.get("support_files", []),
                f"{step['id']} must use deterministic run scaffolding",
            )

    def test_entrypoint_keeps_mechanical_work_in_scripts_without_automating_judgment(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Push every mechanical action into `scripts/`", skill)
        self.assertIn("Scripts scaffold judgment; they never make the judgment", skill)
        execution = skill.split("## Execution\n", 1)[1].split("\n## ", 1)[0]
        rows = [line for line in execution.splitlines() if line.startswith("| ")]
        step_rows = [line for line in rows if line.split("|")[1].strip().isdigit()]
        self.assertEqual(len(step_rows), 25)
        for row in step_rows:
            self.assertIn("scripts/run_pipeline.py", row)


if __name__ == "__main__":
    unittest.main()
