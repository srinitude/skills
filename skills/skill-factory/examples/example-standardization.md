# Example: reviewed standardization

This example removes the guess that a profile, unchanged rerun or successful promotion alone establishes an accepted skill. Load the full [run record](standardization-run.json) through `mise run standardize-target` before using this route.

## User says

```text
Standardize this clock skill from a reviewed plan. Show missing-review and permission-drift rejection, preserve its Git and local runtime state, then run its clock operation.
```

## Executor replies

```text
The plan did not change the target. Missing review and stale permissions were rejected. Reviewed recovery preserved source customizations, Git and runtime state, and the clock operation returned an observed timestamp. Full domain and source acceptance remain pending.
```

## Observed run

After decoding the lossless run record, its `stdout` and `stderr` fields contain the complete actual streams, including discovery diagnostics. Commands, exit codes, inputs and historical runtime identities are unchanged.

The full record contains five actual public invocations, their working directories, commands, stdout, stderr and exit codes. It preserves complete profile, plan, ledger/review and target bytes with base64, plus file changes and the checked runtime identity. The configured factory runtime preexists these invocations. The target's clock code, metadata, Git files and local runtime state survive the reviewed update.

Use `mise run --output interleave standardize-target -- <path> --profile <profile> --scope <scope>` to obtain the plan. Save its final complete JSON report after prerequisite diagnostics. The review contains `plan_sha256`, `context`, `body_review` and exactly one entry per planned file under `files`; load the body's ledger rules through `mise run ledger` before preparing those declarations. Repeat the same inputs with `--apply --plan-file <plan.json> --review <review.json>`. Missing or stale reviews require renewed source review, not an edited digest alone.

The example's seeded policy and body declarations remain unaccepted. One clock execution and preserved bytes do not prove full ledger meaning, source coverage, native domain-workflow granularity, authentic human evidence or whole-goal acceptance. Current archive and integration checks must bind the delivered package separately from this historical run.

Standardization includes the current canonical efficiency paragraph in the resulting body. An existing different paragraph requires an explicit reviewed profile migration before effect; preserve its applicable domain rules when reconciling it. Current canonical wording is kept once. Propagation and package checks do not establish faster accepted outcomes.

## Read the complete record

The JSON envelope keeps a readable command index and the complete original record in `record_xz_base64`. Decode it with `json.loads(lzma.decompress(base64.b64decode(envelope["record_xz_base64"])))` using Python's standard-library `json`, `lzma` and `base64` modules. Verify the decompressed bytes against `record_sha256`. Nested base64 fields still retain exact individual file or stream bytes. Compression changes storage only; no command, output, input, file, claim or limit is omitted.
