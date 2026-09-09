# Example: user-level to project-level

This run removes the guess about source preservation and which reviews must precede a project variant publication. Load it before the project direction of `mise run variant`.

## Request and actual record

The user asks for a separate Atlas project variant of a user-scope inventory skill, preserving the source and its read-only file and line count. Atlas is a Python project using `src`; its authoritative fixture configuration and instructions are retained in the [complete run](variant-public-run.json).

That record contains the user's words, visible reply, exact commands and working directories, full actual stdout/stderr, exit codes, all supplied review files, initial source/candidate/project bytes and final published package bytes. Fields ending in `_base64` encode complete bytes. Decode individual values with Python's standard-library `base64.b64decode`; they are not summaries. Temporary paths identify the actual isolated fixture run and are not installation locations.

## Dependency and review order

The public task first prepares and type-checks its declared runtime. `plan` freezes source, destination and project context. `review` creates an unaccepted domain-review draft. The fixture supplies its declared source/project review, then attempts publication without a ledger review; the command rejects it and creates no target. `accept --preview` exposes the complete future publication, including lineage. The executor supplies a separate initial-body and every-file ledger review bound to those exact bytes. Only then does `accept --plan-file ... --ledger-review ...` publish the reviewed package.

The `project-` cases in the complete record retain every actual command and output for that sequence. The scope plan and the domain review remain separate from the publication plan and its ledger review. A filled review schema alone does not establish the truth of its judgments.

## Observed result and limits

The run verifies that the user-scope source remains byte-exact and the project package matches every planned file. Its actual public `inventory` task returns one file and two lines for Atlas. Package, attribution, scope and declared behavior checks retain their separate results in the publication output. Execution acceptance remains pending because this finite synthetic run does not establish full source meaning, actual human review or the complete factory goal.

The executable variant tests separately exercise changed source/project inputs, missing attribution, privacy checks, incomplete review, permission drift, independent source drift during promotion, withdrawal and recovery, explicit in-place adaptation and requested refresh with preserved customizations. Run `mise run test -- -k Variant` for the current assertions. These tests do not promise correctness for every future skill or project.

## Read the complete record

The JSON envelope keeps a readable command index and the complete original record in `record_xz_base64`. Decode it with `json.loads(lzma.decompress(base64.b64decode(envelope["record_xz_base64"])))` using Python's standard-library `json`, `lzma` and `base64` modules. Verify the decompressed bytes against `record_sha256`. Nested base64 fields still retain exact individual file or stream bytes. Compression changes storage only; no command, output, input, file, claim or limit is omitted.
