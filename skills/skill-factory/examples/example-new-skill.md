# Create a scaffold from its reviewed file plan

This example removes the guess about inspecting every planned byte, supplying current ledger reviews before creation, rejecting stale work and preserving the unfinished seed boundary. Load it for `mise run new`. The [complete observed run](new-skill-run.json) contains the example request, executor reply, every exact command, working directory, stdout, stderr, exit code, governing input file and complete created file. The lossless record retains exact bytes and line endings; its decoded `stdout` and `stderr` fields contain the complete actual streams. Runtime prerequisites are identified separately from command effects.

The example request was: “Prepare a user-scope scaffold from a reviewed plan. Demonstrate missing and stale review rejection, then create the exact reviewed files.” The executor replied: “The plan produced no package files. Missing and stale reviews were rejected. The current review produced the exact planned scaffold; domain implementation and acceptance remain pending.”

Use `mise run new -- --name <name> --description "<description>" --scope <user-or-project> --dest <parent> --plan` first. The plan contains the full current factory body, owned-file identities, source bindings, exact rendered/copy bytes, construction phases and observed local Python imports. The authoring destination does not determine scope or authorize installation. The record preserves the actual readiness report followed by the command result.

| Actual run | Observed result |
| --- | --- |
| Plan | Exit 0; complete plan returned and no package files created. |
| Omit review | Exit 1; authoring destination unchanged. |
| Supply stale plan review | Exit 1; authoring destination unchanged. |
| Restore current review and create | Exit 0; every created byte matches the plan, construction order is recorded and execution acceptance remains pending. |

After reviewing the actual plan, repeat the same flags with `--review <review.json>` in place of `--plan`. The review object has exactly `plan_sha256`, `context`, `body_review` and `files`. The plan digest uses sorted-key JSON, compact comma/colon separators, default ASCII escaping and no trailing newline. Context supplies the exact ledger, ledger digest, expected documents, original source and frozen inventory name required by `mise run ledger`. Each planned path needs a reviewer and every actual ledger review field. Use `mise run new -- --help` for the precise interface.

The initial body review binds its path, digest, candidate bytes, source and ledger; `previous_sha256` is explicitly null for creation. It declares initial review with execution acceptance pending. The builder reads the full governing inputs around every file write. Before the body is installed it uses the reviewed candidate; canonical body creation uses `body_revision`; later writes read the installed body. All file reviews are checked before staging starts. Current factory inputs are checked around each write, and exact package bytes are checked before the existing guarded promotion.

The source fixture and review text are explicit non-independent declarations. They prove the recorded mechanical paths, not authenticated human judgment, complete source meaning, domain-workflow granularity, all update routes or accepted domain behavior. Construction order and observed imports do not prove complete runtime or reading dependencies. Seeds remain blocked until their actual domain implementation, resources, examples, evaluations and acceptance are finished. Use `mise run test` for current scaffold and copied-runtime regression checks.

The created body includes the current efficiency policy: complete ready functional paths, justify supporting work, preserve all required reads and proof, and distinguish implementation, validation and acceptance. This recorded inheritance is not a measured speed improvement.

## Read the complete record

The JSON envelope keeps a readable command index and the complete original record in `record_xz_base64`. Decode it with `json.loads(lzma.decompress(base64.b64decode(envelope["record_xz_base64"])))` using Python's standard-library `json`, `lzma` and `base64` modules. Verify the decompressed bytes against `record_sha256`. Nested base64 fields still retain exact individual file or stream bytes. Compression changes storage only; no command, output, input, file, claim or limit is omitted.
