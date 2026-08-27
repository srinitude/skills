"""State transitions for the deterministic 25-step execution pipeline."""
import pathlib

from lib.pipeline_io import PipelineError, file_hash, group_record, load_json, save_json


SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
IO_MAP_PATH = SKILL_DIR / "assets" / "execution-io-map.json"
STEP_CONTRACT_PATH = SKILL_DIR / "assets" / "execution-step-contract.json"


def contracts() -> tuple[dict, dict]:
    io_map = load_json(IO_MAP_PATH)
    step_contract = load_json(STEP_CONTRACT_PATH)
    steps = io_map.get("steps")
    if not isinstance(steps, list) or len(steps) != step_contract.get("step_count"):
        raise PipelineError("execution contracts disagree on step count")
    return io_map, step_contract


def new_step(spec: dict) -> dict:
    return {
        "id": spec["id"], "step_id": spec["id"],
        "title": spec.get("title", spec["id"]), "status": "PENDING",
        "consumes": list(spec["consumes"]), "produces": list(spec["produces"]),
        "primary_output": spec["primary_output"],
        "decision_owner": spec.get("decision_owner", "agent"),
        "input_paths": [], "support_files": list(spec.get("support_files", [])),
        "actions": [], "output_paths": [], "checks": [],
        "evidence_locators": [], "error_code": None, "reason": None,
        "recovery": None, "retry_count": 0,
    }


def checked_anchor(path: str) -> dict:
    anchor = load_json(pathlib.Path(path))
    fields = ["captured_at", "date", "weekday", "timezone", "utc_offset", "source"]
    for field in fields:
        if not anchor.get(field):
            raise PipelineError(f"anchor is missing required field: {field}")
    return anchor


def command_init(args) -> dict:
    io_map, _ = contracts()
    run_path = pathlib.Path(args.run)
    if run_path.exists() and not args.force:
        raise PipelineError(f"run file already exists: {run_path}; use --force to replace it")
    record = {
        "schema_version": "1.0", "contract": "dtcg-tokens/run-pipeline",
        "run_id": args.run_id, "name": args.name,
        "anchor": checked_anchor(args.anchor),
        "contract_files": {
            "execution_io_map": str(IO_MAP_PATH.relative_to(SKILL_DIR)),
            "execution_step_contract": str(STEP_CONTRACT_PATH.relative_to(SKILL_DIR)),
        },
        "artifacts": {
            "request.packet": group_record([pathlib.Path(args.request)]),
            "source.payload": group_record([pathlib.Path(path) for path in args.source]),
        },
        "steps": [new_step(spec) for spec in io_map["steps"]],
    }
    save_json(run_path, record)
    return {"valid": True, "command": "init", "run": str(run_path), "step_count": len(record["steps"])}


def load_run(path_text: str) -> tuple[pathlib.Path, dict, dict]:
    run_path = pathlib.Path(path_text)
    record = load_json(run_path)
    _, step_contract = contracts()
    steps = record.get("steps")
    if not isinstance(steps, list) or len(steps) != step_contract["step_count"]:
        raise PipelineError("run record does not contain the required step set")
    return run_path, record, step_contract


def find_step(record: dict, step_id: str) -> tuple[int, dict]:
    for index, step in enumerate(record["steps"]):
        if step.get("id") == step_id:
            return index, step
    raise PipelineError(f"unknown step: {step_id}")


def require_inputs(record: dict, step: dict) -> list[dict]:
    missing = [name for name in step["consumes"] if name not in record["artifacts"]]
    if missing:
        raise PipelineError(f"{step['id']} is missing named inputs: {', '.join(missing)}")
    return [record["artifacts"][name] for name in step["consumes"]]


def reset_step(step: dict, inputs: list[dict]) -> None:
    if step["status"] in {"PASS", "BLOCKED"}:
        step["retry_count"] += 1
    step.update({
        "status": "RUNNING", "input_paths": inputs, "actions": [],
        "output_paths": [], "checks": [], "evidence_locators": [],
        "error_code": None, "reason": None, "recovery": None,
    })


def command_start(args) -> dict:
    run_path, record, _ = load_run(args.run)
    index, step = find_step(record, args.step)
    if index and record["steps"][index - 1]["status"] != "PASS":
        prior = record["steps"][index - 1]["id"]
        raise PipelineError(f"{args.step} cannot start before {prior} is PASS")
    inputs = require_inputs(record, step)
    if step["status"] not in {"PENDING", "PASS", "BLOCKED"}:
        raise PipelineError(f"{args.step} cannot start from {step['status']}")
    reset_step(step, inputs)
    save_json(run_path, record)
    return {"valid": True, "command": "start", "run": str(run_path), "step": args.step, "status": "RUNNING"}


def parse_outputs(values: list[str]) -> dict[str, pathlib.Path]:
    outputs = {}
    for value in values:
        if "=" not in value:
            raise PipelineError(f"output must use NAME=PATH: {value}")
        name, raw_path = value.split("=", 1)
        if not name or not raw_path or name in outputs:
            raise PipelineError(f"invalid or repeated output: {value}")
        outputs[name] = pathlib.Path(raw_path)
    return outputs


def record_outputs(record: dict, step: dict, outputs: dict) -> list[dict]:
    output_records = []
    for name in step["produces"]:
        path = outputs[name]
        artifact = {"path": str(path), "sha256": file_hash(path)}
        record["artifacts"][name] = artifact
        output_records.append({"name": name, **artifact})
    return output_records


def command_pass(args) -> dict:
    run_path, record, _ = load_run(args.run)
    _, step = find_step(record, args.step)
    if step["status"] != "RUNNING":
        raise PipelineError(f"{args.step} must be RUNNING before PASS")
    outputs = parse_outputs(args.output)
    required = set(step["produces"])
    if set(outputs) != required:
        missing = sorted(required - set(outputs))
        extra = sorted(set(outputs) - required)
        raise PipelineError(f"output names must match the contract; missing={missing}; extra={extra}")
    step["output_paths"] = record_outputs(record, step, outputs)
    step["checks"], step["evidence_locators"] = list(args.check), list(args.evidence)
    step["status"] = "PASS"
    save_json(run_path, record)
    return {"valid": True, "command": "pass", "run": str(run_path), "step": args.step, "status": "PASS"}


def command_block(args) -> dict:
    run_path, record, step_contract = load_run(args.run)
    _, step = find_step(record, args.step)
    if step["status"] != "RUNNING":
        raise PipelineError(f"{args.step} must be RUNNING before BLOCKED")
    if args.code not in step_contract["error_codes"]:
        raise PipelineError(f"unsupported error code: {args.code}")
    step.update({
        "status": "BLOCKED", "error_code": args.code,
        "reason": args.reason, "recovery": args.recovery,
        "checks": list(args.check), "evidence_locators": list(args.evidence),
    })
    save_json(run_path, record)
    return {"valid": True, "command": "block", "run": str(run_path), "step": args.step, "status": "BLOCKED"}


def command_packet(args) -> dict:
    _, record, _ = load_run(args.run)
    _, step = find_step(record, args.step)
    available = {name: record["artifacts"][name] for name in step["consumes"] if name in record["artifacts"]}
    packet = {
        "schema_version": "1.0", "contract": "dtcg-tokens/step-packet",
        "run_id": record["run_id"], "step_id": step["id"],
        "decision_owner": step["decision_owner"], "consumes": step["consumes"],
        "produces": step["produces"], "support_files": step["support_files"],
        "available_inputs": available,
        "missing_inputs": [name for name in step["consumes"] if name not in available],
        "output_rule": "Save every named output as a file before marking the step PASS.",
    }
    save_json(pathlib.Path(args.output), packet)
    return {"valid": True, "command": "packet", "output": args.output, "step": args.step}


def command_status(args) -> dict:
    run_path, record, _ = load_run(args.run)
    counts = {status: 0 for status in ["PENDING", "RUNNING", "PASS", "BLOCKED"]}
    for step in record["steps"]:
        if step["status"] not in counts:
            raise PipelineError(f"unsupported status in {step['id']}: {step['status']}")
        counts[step["status"]] += 1
    return {
        "valid": True, "command": "status", "run": str(run_path),
        "counts": counts, "complete": counts["PASS"] == len(record["steps"]),
    }
