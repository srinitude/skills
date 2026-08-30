#!/usr/bin/env python3
"""Build or check examples from real commands.

Exit codes:
  0  files match or were written
  1  one or more files do not match
  2  usage is bad

Example:
  python3 scripts/build_examples.py --check
"""
import argparse, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "scripts" / "run_pipeline.py"
INTAKE = ROOT / "evals" / "files" / "valid-intake.json"
MISSING = ROOT / "evals" / "files" / "missing-proof.json"
VALID_CONTEXT = ROOT / "evals" / "files" / "valid-context-record.json"
MISSING_CONTEXT = ROOT / "evals" / "files" / "missing-context-record.json"


def command(*args):
    env = {**os.environ, "COLUMNS": "80", "LC_ALL": "C",
           "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, str(PIPELINE), *map(str, args)],
                          capture_output=True, text=True, timeout=120,
                          env=env)


def file_block(path, text):
    return f"`run/{path}`\n\n```text\n{text.rstrip()}\n```\n"


def run_data():
    with tempfile.TemporaryDirectory() as temp:
        first = command("start", "--intake", INTAKE, "--run-dir", temp)
        second = command("packet", "--run-dir", temp,
                         "--action", "source_meaning")
        root = Path(temp)
        files = [(str(path.relative_to(root)), path.read_text(encoding="utf-8"))
                 for path in sorted(root.rglob("*")) if path.is_file()]
    return first, second, files


def run_example():
    first, second, files = run_data()
    parts = ["# Run example\n",
             "Guess removed: A run may hide the rich scaffold or its files.\n",
             "## Request\n", "> Build a clear setup flow for new account owners. It must work on wide and narrow web views.\n",
             "## Visible reply\n", "I will start the fixed run and make the first model packet.\n",
             "## Commands\n", "```sh\npython3 scripts/run_pipeline.py start --intake evals/files/valid-intake.json --run-dir run\npython3 scripts/run_pipeline.py packet --run-dir run --action source_meaning\n```\n",
             "## Real output\n", f"```text\n{first.stdout}{second.stdout}```\n",
             f"The first command exits with code `{first.returncode}`. The second command exits with code `{second.returncode}`.\n",
             "## Every created file\n"]
    parts.extend(file_block(path, text) for path, text in files)
    parts.append("No value was guessed. Open lists stay ready for current proof.\n")
    return "\n".join(parts)


def help_example():
    result = command("--help")
    return "\n".join([
        "# Help example\n",
        "Guess removed: Help starts no run and writes no file.\n",
        "## Request\n", "> Show me the skill commands.\n",
        "## Command\n", "```sh\npython3 scripts/run_pipeline.py --help\n```\n",
        "## Real output\n", f"```text\n{result.stdout.rstrip()}\n```\n",
        f"The command exits with code `{result.returncode}`. It creates no files.\n",
    ])


def failure_example():
    with tempfile.TemporaryDirectory() as temp:
        result = command("start", "--intake", MISSING, "--run-dir", temp)
        made = list(Path(temp).rglob("*"))
    return "\n".join([
        "# Missing proof example\n",
        "Guess removed: A missing proof bar must stop the run without files.\n",
        "## Request\n", "> Start this run now. I have not set the proof bar.\n",
        "## Command\n", "```sh\npython3 scripts/run_pipeline.py start --intake evals/files/missing-proof.json --run-dir run\n```\n",
        "## Real output\n", f"```text\n{result.stderr.rstrip()}\n```\n",
        f"The command exits with code `{result.returncode}`. It creates `{len(made)}` files.\n",
        "## Visible reply\n", "The run is blocked. Add a clear proof bar to the intake.\n",
    ])


def context_data():
    with tempfile.TemporaryDirectory() as temp:
        first = command("start", "--intake", INTAKE, "--run-dir", temp)
        second = command("packet", "--run-dir", temp,
                         "--action", "source_meaning")
        packet = (Path(temp) / "packets" /
                  "source_meaning.json").read_text(encoding="utf-8")
    return first, second, packet


def context_example():
    first, second, packet = context_data()
    valid = VALID_CONTEXT.read_text(encoding="utf-8")
    blocked = MISSING_CONTEXT.read_text(encoding="utf-8")
    return "\n".join([
        "# Context packet example\n",
        "Guess removed: A short action may omit needed judgment context.\n",
        "## Request\n", "> Prepare the source meaning packet before any product judgment.\n",
        "## Commands\n", "```sh\npython3 scripts/run_pipeline.py start --intake evals/files/valid-intake.json --run-dir run\npython3 scripts/run_pipeline.py packet --run-dir run --action source_meaning\n```\n",
        "## Real output\n", f"```text\n{first.stdout}{second.stdout}```\n",
        f"The commands exit with codes `{first.returncode}` and `{second.returncode}`. The second creates one packet file.\n",
        file_block("packets/source_meaning.json", packet),
        "## Passing context record\n", file_block("../evals/files/valid-context-record.json", valid),
        "## Blocked context record\n", file_block("../evals/files/missing-context-record.json", blocked),
        "The model reads each named path. Missing required context keeps the affected claim blocked.\n",
        "The script checks that accounting. It does not judge the control.\n",
    ])


def product_state_data():
    with tempfile.TemporaryDirectory() as temp:
        first = command("start", "--intake", INTAKE, "--run-dir", temp)
        second = command("packet", "--run-dir", temp,
                         "--action", "source_meaning")
        third = command("record", "--run-dir", temp,
                        "--result", VALID_CONTEXT)
        fourth = command("packet", "--run-dir", temp,
                         "--action", "state_judgment")
        root = Path(temp)
        matrix = (root / "state-matrix.json").read_text(encoding="utf-8")
        packet = (root / "packets" /
                  "state_judgment.json").read_text(encoding="utf-8")
    return first, second, third, fourth, matrix, packet


def product_state_example():
    first, second, third, fourth, matrix, packet = product_state_data()
    return "\n".join([
        "# Product state example\n",
        "Guess removed: Common state names are a closed product state list.\n",
        "## Request\n", "> Find the account setup states before choosing a response.\n",
        "## Commands\n", "```sh\npython3 scripts/run_pipeline.py start --intake evals/files/valid-intake.json --run-dir run\npython3 scripts/run_pipeline.py packet --run-dir run --action source_meaning\npython3 scripts/run_pipeline.py record --run-dir run --result evals/files/valid-context-record.json\npython3 scripts/run_pipeline.py packet --run-dir run --action state_judgment\n```\n",
        "## Real output\n", f"```text\n{first.stdout}{second.stdout}{third.stdout}{fourth.stdout}```\n",
        f"The commands exit with codes `{first.returncode}`, `{second.returncode}`, `{third.returncode}`, and `{fourth.returncode}`.\n",
        "## Open state scaffold\n", file_block("state-matrix.json", matrix),
        "## Full model packet\n", file_block("packets/state_judgment.json", packet),
        "The listed states are prompts. The model may find overlapping, mixed, brief, or person-specific states.\n",
        "For each found state, the model records causes, change, proof, options, tradeoffs, vetoes, choice, and doubt.\n",
        "The source fixture proves only ordered packet mechanics. It does not prove a product source or design choice.\n",
    ])


def documents():
    return {ROOT / "examples" / "run.md": run_example(),
            ROOT / "examples" / "help.md": help_example(),
            ROOT / "examples" / "failure-missing-proof.md": failure_example(),
            ROOT / "examples" / "context-packets.md": context_example(),
            ROOT / "examples" / "product-states.md": product_state_example()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    changed = []
    for path, text in documents().items():
        text = text.rstrip() + "\n"
        if args.write:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                path.write_text(text, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != text:
            changed.append(path.name)
    if changed:
        print("examples differ: " + ", ".join(changed), file=sys.stderr)
        return 1
    print("examples written" if args.write else "examples match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
