# Execution guide

Run all 25 steps in order. `assets/execution-io-map.json` names each input, output, support file, and decision owner. `assets/execution-step-contract.json` owns status, evidence, and retries. `scripts/run_pipeline.py` creates the run scaffold, prepares step packets, checks prerequisites, hashes outputs, and records state. A step starts only after all named inputs exist and the prior step is `PASS`. A step ends only after every named output is saved. One deliverable never completes the pipeline.

## Runner commands

| Command | Use |
| --- | --- |
| `python3 scripts/run_pipeline.py init --run <run.json> --run-id <id> --name <name> --request <request-file> --source <source-file> --anchor <anchor.json>` | Create 25 `PENDING` records and hash the frozen request and sources. Repeat `--source` for more inputs. |
| `python3 scripts/run_pipeline.py packet --run <run.json> --step SNN --output <packet.json>` | Save the exact inputs, outputs, support files, missing inputs, and decision owner for one step. |
| `python3 scripts/run_pipeline.py start --run <run.json> --step SNN` | Verify all named inputs and predecessor state, then set the step to `RUNNING`. |
| `python3 scripts/run_pipeline.py pass --run <run.json> --step SNN --output <name>=<path>` | Hash every named output and set the step to `PASS`. Repeat `--output`, `--check`, and `--evidence` as needed. |
| `python3 scripts/run_pipeline.py block --run <run.json> --step SNN --code <code> --reason <text> --recovery <text>` | Save one allowed error, failed check, evidence locator, and exact recovery need. |
| `python3 scripts/run_pipeline.py status --run <run.json>` | Report state counts and whether all 25 steps are `PASS`. |

## Step fields

- **Input:** Exact records and source material required before work.
- **Action:** What the decision owner does and which named files it reads or runs.
- **Save:** The named output file that the runner hashes and registers.
- **Pass:** The saved evidence that proves the step succeeded.
- **Blocked:** The failed prerequisite or check, one allowed error code, and the exact recovery need. It never means merely unfinished.
- **Feeds:** The next step and the output name it consumes.

Keep these fields separate in `<name>.run.json`. Use the phase that owns the current step:

| Steps | Guide                            | Scope                                                                   |
| ----- | -------------------------------- | ----------------------------------------------------------------------- |
| 01-08 | `references/execution-intake.md` | Freeze, inventory, vision, observation, thesis, universe, experiments.  |
| 09-17 | `references/execution-build.md`  | Contexts, signatures, tokens, evidence, proof authoring, assembly.      |
| 18-25 | `references/execution-review.md` | Final visual review, defects, invariants, judgment, repair, completion. |
