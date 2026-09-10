# Example: reviewed standardization

This example removes the guess that a profile, unchanged rerun or successful promotion alone establishes an accepted skill. Load the full [run record](standardization-run.json) through `mise run standardize-target` before using this route.

## User says

```text
Standardize this clock skill with the current ledger body. Reject missing review and permission drift, preserve Git and local state, prove a reviewed rerun changes nothing, then run the clock, validate eval shape and reject unfinished eval seeds.
```

## Executor replies

```text
The plan and rejected requests left the target unchanged. Reviewed recovery preserved Git, runtime state and the domain operation. The body received the current ledger policy blocks, and a separately reviewed rerun changed no files. The clock returned an observed timestamp. Eval schema validation passed, and the placeholder gate rejected the unfinished domain cases. Full output and goal acceptance remain pending.
```

## Observed run

After decoding the lossless run record, its `stdout` and `stderr` fields contain the complete actual streams, including discovery diagnostics. Commands, exit codes, inputs and historical runtime identities are unchanged.

The full record contains nine actual public invocations, their working directories, commands, stdout, stderr and exit codes. It preserves complete profile, plan, ledger/review and target bytes with base64, plus file changes and the checked runtime identity. The configured factory runtime preexists these invocations. The target's clock code, metadata, Git files and local runtime state survive the reviewed update.

Use `mise run --output interleave standardize-target -- <path> --profile <profile> --scope <scope>` to obtain the plan. Save its final complete JSON report after prerequisite diagnostics. The review contains `plan_sha256`, `context`, `body_review` and exactly one entry per planned file under `files`; load the body's ledger rules through `mise run ledger` before preparing those declarations. Repeat the same inputs with `--apply --plan-file <plan.json> --review <review.json>`. Missing or stale reviews require renewed source review, not an edited digest alone.

The eval schema check passes, while the placeholder check rejects 16 unfinished seed fields. The example's seeded policy and body declarations remain unaccepted. One clock execution and preserved bytes do not prove full ledger meaning, source coverage, native domain-workflow granularity, authentic human evidence or whole-goal acceptance. Current archive and integration checks must bind the delivered package separately from this historical run.

Standardization places the current initial-loading, reusable ledger, full relationship table, dependency, traversal, per-file review and efficiency policies before domain actions. It retains the existing domain body and frontmatter. Different or duplicate owned policies require an explicit reviewed migration before effect; preserve all applicable domain rules during reconciliation. Descriptive owner links retain their public Mise routes without becoming new executable tasks. The updated body also names the shipped generation contract and file-review example with their load conditions. Standardization connects missing baseline CI checks through existing task owners and retains domain tasks. Generated CI checks bind the complete normalized CI task. Exact factory-generated checks are refreshed; customized checks retain their contents for explicit review. Existing custom CI commands and task settings are retained. Nested calls with arguments or shell work require explicit reconciliation before standardization. It preserves authored eval cases and trigger labels; incomplete domain content remains marked for rejection. The observed reviewed rerun changed no files. Propagation and package checks do not establish faster accepted outcomes.

## Read the complete record

The JSON envelope keeps a readable command index and the complete original record in `record_xz_base64`. Decode it with `json.loads(lzma.decompress(base64.b64decode(envelope["record_xz_base64"])))` using Python's standard-library `json`, `lzma` and `base64` modules. Verify the decompressed bytes against `record_sha256`. Nested base64 fields still retain exact individual file or stream bytes. Compression changes storage only; no command, output, input, file, claim or limit is omitted.
