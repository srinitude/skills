# Write a file against its current governing inputs

This example removes the guess about creating a file, rejecting a request without the explicit write root and replacing a reviewed revision. Load it when using `mise run ledger` with `write-file`. The [complete observed run](ledger-write-run.json) contains the user's words, visible reply, every exact command, working directory, stdout, stderr, exit code and complete input/output file contents. Each file value uses base64 to preserve its bytes and line endings. The recorded temporary directories describe the actual run; choose your own authorized canonical root when applying the method.

The user asked: “Write the prepared release note, then update it after checking its current revision.” The executor replied: “The note was created. A request without the explicit write root was rejected without changing it. After binding the current revision, the replacement succeeded.”

The public command is `mise run ledger -- <request.json> --write-root <root>`. The observed commands additionally disable task caching and appear verbatim in the run record. The isolated factory runtime was already present before these commands. Its file identities are recorded separately from the files these commands created or changed.

| Case | Observed result | File effect |
| --- | --- | --- |
| Create | Exit 0, native workflow success. | Created `release-note.txt` with the prepared bytes. |
| Omit the write root | Exit 1 before workflow dispatch. | No file changed. A write needs the caller-selected root even though read actions do not. |
| Reviewed replacement | Exit 0, native workflow success. | Replaced the note after binding its actual previous digest and the newly prepared bytes. |

The first note contained `Release note: preserve verified input bindings.` followed by a newline. The replacement contained `Release note: preserve verified bindings and reviewed revisions.` followed by a newline. The run record includes both full byte strings and all other created or changed files; no output has been reconstructed or shortened.

For `mise run ledger`, the request binds the current ledger, independently supplied governing documents, original source, frozen inventory, target body, prepared file and expected destination digest. Creation uses a null expected digest. Replacement uses the actual current digest. The caller supplies the authorized write root outside the request. Every actual review-protocol field needs a supplied declaration. These declarations record the caller's work; they do not authenticate a reviewer or confer permission.

This is an actual mechanical example with explicit fixture source rules. It proves the shown file effects, rejection and recovery. It does not prove semantic judgment, human review, whole-skill behavior or guard integration for other writers. Use the `mise run ledger -- --help` contract for the precise supported paths, full reads, restoration conditions and isolation limits. Complete the separate semantic review and ledger invalidation before accepting the skill change.
