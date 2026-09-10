# Example: reviewed standardization

This example shows how a declared profile becomes a reviewed native domain workflow, then a changed skill and observed domain output. Load the full [run record](standardization-run.json) before using `mise run standardize-target`. A profile, unchanged rerun or successful promotion alone does not establish an accepted skill.

## Load the record and prerequisites

The JSON envelope keeps a readable command index and the complete original record in `record_xz_base64`. Decode it with `json.loads(lzma.decompress(base64.b64decode(envelope["record_xz_base64"])))` using Python's standard-library `json`, `lzma` and `base64` modules. Verify the decompressed bytes against `record_sha256`. Nested base64 fields retain exact individual file or stream bytes. Compression changes storage only; no command, output, input, file, claim or limit is omitted.

The declared isolated factory copy and pinned tools preexist the public invocations. Public prerequisites check the tools, source corpus and TypeScript runtime. Setup installs the shared root packages first, then factory-only persistent storage against their declared peers. The record identifies all 242 copied factory files. It records complete actual stdout and stderr, including discovery diagnostics, working directories, commands, exit codes, profile, plan, ledger/review, target bytes and changed workflow-state files.

Read the current body and its governing ledger through `mise run ledger` before making review declarations. The default workflow uses temporary state removed at exit. An explicitly selected `--workflow-state <absolute-directory>` supports process-separated review in a caller-owned private POSIX directory outside the factory and target. The workflow does not infer permission from directory selection or review text. Its storage implementation stays in the factory; standardization does not add it to generated skills.

## Check the current argument interface

Before planning with `mise run standardize-target`, load the current [interface record](help-run.json) through `mise run standardization-usage`. Native Python owns the arguments; the recorded Usage projection supplies help, completion and interface documentation. The public workflow rejects a missing or stale projection or disagreeing bindings before creating workflow state. Literal arguments keep their boundaries through native Mise `raw_args`; the owning code still validates domain constraints.

After changing the argument definition, run `mise run --output interleave standardization-usage` and retain its exact stdout as the proposed replacement. Review and install that asset through the existing individual-file ledger route, then rerun parsing, forwarding, spec lint/diff and actual workflow checks. The read-only export does not install the asset. The interface record contains real export, lint and current-definition comparison results; the larger domain record below remains a historical workflow trace, with its own identified runtime and proof limits.

## User says

```text
Standardize this clock skill with the current ledger body. Suspend a saved domain run, reject it, refuse replay, then recover with current review. Reject missing review and permission drift, preserve Git and local state, prove a reviewed rerun changes nothing, then run the clock and its eval gates.
```

## Executor replies

```text
The plan, explicit rejection and refused replays left the target unchanged. A fresh reviewed domain run resumed in a separate process and preserved Git, runtime state and the domain operation. The body received the current ledger policy blocks, and a separately reviewed rerun changed no files. The clock returned an observed timestamp. Eval schema validation passed, and the placeholder gate rejected the unfinished domain cases. Full output and goal acceptance remain pending.
```

## Plan, review and recover

Use `mise run --output interleave standardize-target -- <path> --profile <profile> --scope <scope>` to obtain a plan. For a persisted run, also supply `--workflow-state <absolute-directory>` and save its returned `workflow.run_id`. Save the final complete JSON report after prerequisite diagnostics. Planning prepares the native inputs, then suspends before the guarded effect.

Planning checks source mappings against the exact rendered and formatted files before returning a usable plan. Existing entry mappings retain their text and semantic bindings. The inspected native clause format retains its source-lineage identities, case IDs, clause references, line ranges, actions and current target files. Mapping bytes are preserved. Unsupported formats require their owning validator; schema and binding checks do not establish complete clause coverage or semantic acceptance. Candidate validation repeats the checks before promotion.

A review contains `plan_sha256`, `context`, `body_review` and exactly one entry per planned file under `files`. Repeat the same inputs with `--apply --plan-file <plan.json> --review <review.json>`. Add the same `--workflow-state` and `--workflow-run <run-id>` to resume that suspended run from another process. Without a run selector, a saved plan supports a newly started reviewed workflow. Missing or stale review requires renewed source review, not an edited digest alone.

To reject a selected persisted run, use the same inputs with `--workflow-state`, `--workflow-run` and `--workflow-reject`, without `--apply`. Rejection closes that run before application. A completed or rejected run refuses replay without starting another native command. Changed inputs require a new plan and review; legitimate recovery uses a fresh reviewed run. After approval declarations, the existing native leaf still owns validation and guarded writes. The workflow verifies actual resulting bytes and executable modes against the selected plan.

Standardization places the current initial-loading, reusable ledger, full relationship table, dependency, traversal, per-file review and efficiency policies before domain actions. It retains the existing domain body and frontmatter. Different or duplicate owned policies require an explicit reviewed migration before effect; preserve all applicable domain rules during reconciliation. Descriptive owner links retain their public Mise routes without becoming new executable tasks. The updated body also names the shipped generation contract and file-review example with their load conditions. Standardization connects missing baseline CI checks through existing task owners and retains domain tasks. Generated CI checks bind the complete normalized CI task. Exact factory-generated checks are refreshed; customized checks retain their contents for explicit review. Existing custom CI commands and task settings are retained. Nested calls with arguments or shell work require explicit reconciliation before standardization. It preserves authored eval cases and trigger labels; incomplete domain content remains marked for rejection. The observed reviewed rerun changed no files. Propagation and package checks do not establish faster accepted outcomes.

## Observed result and limits

The record contains 13 actual public invocations: saved planning, explicit rejection, rejected-run replay refusal, fresh recovery planning, missing-review rejection, mode-drift rejection, reviewed recovery, completed-run replay refusal, a fresh rerun plan, reviewed no-op, clock execution, eval schema validation and unfinished-seed rejection. Reviewed recovery resumes the selected run in a separate process. The separately reviewed rerun changes no files. The target's clock code, metadata, Git bytes and inode, and local runtime state survive the update.

The clock returns an observed local ISO timestamp with its UTC offset. The eval schema check reports zero problems. The placeholder gate rejects 16 unfinished seed fields and creates one recorded Python bytecode cache file. It changes no preexisting file; cache bytes are retained as an actual runtime effect rather than omitted from the record.

This proves the named finite mechanical outcomes under the recorded private POSIX state and pinned runtime. The seeded review and body declarations are non-independent fixtures, not authentic human approval. Full source/body/ledger meaning, source coverage, human evidence, all workflow and runtime conditions, and whole-goal acceptance remain pending. These invocations do not prove hostile-writer isolation, crash safety, cross-platform equivalence or faster accepted outcomes. Current archive and integration checks must bind the delivered package separately from this historical run.
