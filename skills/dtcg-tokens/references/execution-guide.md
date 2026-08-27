# Execution guide

Run all 25 steps in order. `assets/execution-io-map.json` names each input and output. `assets/execution-step-contract.json` owns status, evidence, and retries. A step starts only after all named inputs exist and the prior step is `PASS`. A step ends only after its output is saved. One deliverable never completes the pipeline.

## Step fields

- **Purpose:** Why the step exists.
- **Consumes:** Exact records and source material required before work.
- **Action:** What to do and which support files to use.
- **Produces:** The record that the next step receives.
- **PASS when:** The saved evidence that proves the step succeeded.
- **BLOCKED when:** The failed prerequisite or check and its error code. It does not mean merely unfinished.
- **Recovery:** The earliest safe step to resume.

Keep these fields separate in `<name>.run.json`. Use the phase that owns the current step:

| Steps | Guide                            | Scope                                                                   |
| ----- | -------------------------------- | ----------------------------------------------------------------------- |
| 01-08 | `references/execution-intake.md` | Freeze, inventory, vision, observation, thesis, universe, experiments.  |
| 09-17 | `references/execution-build.md`  | Contexts, signatures, tokens, evidence, proof authoring, assembly.      |
| 18-25 | `references/execution-review.md` | Final visual review, defects, invariants, judgment, repair, completion. |
