# Example: project-level to user-level

This run removes the guess about preserving an existing project skill while creating a reviewed variant that works in two materially different projects. Load it before the user direction of `mise run variant`.

## Request and actual record

The user requests a separate portable inventory skill derived from the already published Atlas project variant. It must preserve the project skill and read-only counting behavior while using each project's configuration. The [complete run](variant-public-run.json) retains exact source, candidate, project, review and published bytes, every public command, working directory, actual output and exit code, plus the user's words and visible reply. Base64 fields preserve the full bytes and can be decoded with Python's standard-library `base64.b64decode`.

The portable candidate reads the selected project's directory and extension. Atlas supplies Python files in `src`; Boreal supplies JavaScript files in `packages/lib`. These actual fixture inputs and their compatibility limits remain in the record. Project and user scopes express intended availability, independently of the temporary authoring paths.

## Dependency and review order

The `user-` cases show the public scope plan, unaccepted domain-review draft, missing-ledger rejection, complete publication preview and reviewed publication. The domain review covers source preservation, adaptation, privacy, attribution and both behavior scenarios. The separate ledger review covers the initial body and every future file, including derivation lineage. The saved publication and ledger review bind actual current source, candidate, target, factory and governing inputs. Runtime preparation precedes the native checker consumers.

Missing ledger review creates no target. A current complete review permits publication, after which the run checks the source inventory is unchanged and every published file matches its plan. The two public inventory invocations each return one file and two lines. The source and new variant remain independently maintained; reversing scope does not promise restoration of earlier bytes or behavior.

## Rerun, refresh and evidence limits

The separate current variant tests exercise a reviewed no-op rerun and changed-target rejection. A no-op still requires a new publication preview and current ledger review because the destination now exists. A requested refresh compares recorded source and target baselines, rejects unresolved conflicts, and retains independent customizations after an explicitly reconciled candidate passes. Run `mise run test -- -k Variant` for those assertions and the isolated privacy, attribution, scope, failure and recovery cases.

The complete public record establishes the two declared project operations and its finite publication predicates. Review fields are synthetic declarations; they are not actual human participation, proof of every privacy judgment, universal portability or completed goal acceptance. These limits remain explicit in the operation reports.

## Read the complete record

The JSON envelope keeps a readable command index and the complete original record in `record_xz_base64`. Decode it with `json.loads(lzma.decompress(base64.b64decode(envelope["record_xz_base64"])))` using Python's standard-library `json`, `lzma` and `base64` modules. Verify the decompressed bytes against `record_sha256`. Nested base64 fields still retain exact individual file or stream bytes. Compression changes storage only; no command, output, input, file, claim or limit is omitted.
