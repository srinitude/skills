# Write a file against its current governing inputs

This example removes the guess about creating and updating a reviewed file, requiring the caller's write root, writing before the target body is installed, and installing or replacing the reviewed body. Load it when using `mise run ledger` with `write-file`. The [complete observed run](ledger-write-run.json) contains the user's words, visible reply, every exact command, working directory, stdout, stderr, exit code and complete input/output file contents. Each file value uses base64 to preserve bytes and line endings. The temporary directories identify the recorded run; choose your own authorized canonical root.

The user asked: “Write and update the prepared note, demonstrate writes before the body is installed, then install and replace the reviewed body. Reject missing review inputs and recover with current bindings.” The executor replied: “The note and reviewed body creations and replacements succeeded. Missing root and review inputs were rejected without file changes. Bootstrap read an external body, and the later body transition installed the reviewed candidate.”

The public command is `mise run ledger -- <request.json> --write-root <root>`. The observed commands disable task caching and appear verbatim in the run record. Its isolated runtime was present before these commands; the record identifies its prerequisite files separately from command effects.

| Case | Observed result | File effect |
| --- | --- | --- |
| Create | Exit 0, native workflow success. | Created the prepared note. |
| Omit the write root | Exit 1 before workflow dispatch. | No file changed. |
| Reviewed replacement | Exit 0, native workflow success. | Replaced the note after binding its current digest. |
| Bootstrap creation | Exit 0, native workflow success. | Created the note using the external reviewed body; no target body was installed. |
| Omit the bootstrap review | Exit 1 before workflow dispatch. | No file changed. |
| Bootstrap recovery | Exit 0, native workflow success. | Replaced the note after supplying the required review and current file digest. |
| Body creation | Exit 0, native workflow success. | Installed the exact reviewed candidate as SKILL.md. |
| Omit the body revision review | Exit 1 before workflow dispatch. | No file changed. |
| Reviewed body replacement | Exit 0, native workflow success. | Replaced SKILL.md after binding the retained prior snapshot and reviewed candidate. |

For `mise run ledger`, the request binds the ledger, independently supplied governing documents, original source, frozen inventory, body, prepared file and expected destination digest. Creation uses a null expected digest; replacement uses the actual digest. The caller selects the authorized write root outside request data and supplies one declaration per actual review field. These declarations do not authenticate judgment or confer permission.

Before the target body exists, the optional `bootstrap_body` argument binds the external candidate and its initial-review file. The review binds candidate, ledger and source digests and retains pending execution acceptance. The writer reads those complete inputs before and after each change. An installed body or alias rejects this path. Complete semantic review remains the caller's responsibility. Use `mise run ledger -- --help` for the exact JSON fields, failure conditions, restoration and isolation limits.

For SKILL.md changes through `mise run ledger`, `body_revision` binds a separately retained previous-body snapshot or explicit absence and the initial-review file. The review also binds `previous_sha256`; `new_file` supplies the candidate. Full reads include the actual prior body before replacement and the installed candidate afterward. Body authority cannot exempt a supplied source, snapshot, review or candidate from overlap checks.

These are actual mechanical runs with explicit fixture source rules. They establish the shown effects, rejections and recovery. They do not establish semantic judgment, human review, whole-skill behavior, scaffold or standardization write integration, removals or final acceptance. Complete the separate semantic review and ledger invalidation before accepting a skill change.
