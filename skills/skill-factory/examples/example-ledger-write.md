# Write a file against its current governing inputs

This example removes the guess about creating and updating a reviewed file, requiring a current initial-body review and the caller's write root, writing before the target body is installed, and installing or replacing the reviewed body. Load it when using `mise run ledger` with `write-file`. The [complete observed run](ledger-write-run.json) contains the user's words, visible reply, every exact command, working directory, stdout, stderr, exit code and complete input/output file contents. Each file value uses base64 to preserve bytes and line endings. The temporary directories identify the recorded run; choose your own authorized canonical root.

The user asked: “Show the file-write inputs, write and update the prepared note under a current initial-body review, reject malformed or incomplete review bindings, and recover. Also demonstrate reviewed bootstrap writes and body installation or replacement.” The executor replied: “The current help names the required review. Malformed and incomplete ordinary-review bindings, missing write root and missing bootstrap or body-revision reviews were rejected without file changes. Current reviewed inputs enabled the note, bootstrap and body transitions.”

The public command is `mise run ledger -- <request.json> --write-root <root>`. The observed commands disable task caching and appear verbatim in the run record. Its isolated runtime was present before these commands; the record identifies its prerequisite files separately from command effects.

| Case | Observed result | File effect |
| --- | --- | --- |
| Help | Exit 0, current public usage text. | No file changed. |
| Malformed initial-review binding | Exit 1 before workflow dispatch. | No file changed. |
| Create | Exit 0, native workflow success. | Created the prepared note. |
| Omit the write root | Exit 1 before workflow dispatch. | No file changed. |
| Reviewed replacement | Exit 0, native workflow success. | Replaced the note after binding its current digest. |
| Omit the initial-review digest | Exit 1 before workflow dispatch. | No file changed. |
| Current initial-review recovery | Exit 0, native workflow success. | Replaced the note after renewing its current review binding. |
| Bootstrap creation | Exit 0, native workflow success. | Created the note using the external reviewed body; no target body was installed. |
| Omit the bootstrap review | Exit 1 before workflow dispatch. | No file changed. |
| Bootstrap recovery | Exit 0, native workflow success. | Replaced the note after supplying the required review and current file digest. |
| Body creation | Exit 0, native workflow success. | Installed the exact reviewed candidate as SKILL.md. |
| Omit the body revision review | Exit 1 before workflow dispatch. | No file changed. |
| Reviewed body replacement | Exit 0, native workflow success. | Replaced SKILL.md after binding the retained prior snapshot and reviewed candidate. |

For `mise run ledger`, the request binds the ledger, independently supplied governing documents, original source, frozen inventory, body, prepared file and expected destination digest. Creation uses a null expected digest; replacement uses the actual digest. The caller selects the authorized write root outside request data and supplies one declaration per actual review field. These declarations do not authenticate judgment or confer permission.

Ordinary nonbody writes require `initial_body_review`, an absolute path/digest binding to a separate review of the installed body. The record binds the exact current body, ledger and source, declares initial contract validation and retains pending full acceptance. The writer reads and checks the entire review before and after the effect. Missing, stale, overlapping or changed reviews fail; this input cannot accompany `bootstrap_body` or `body_revision`. The shipped cases exercise malformed and incomplete bindings before workflow dispatch; the regression suite separately exercises absent and stale review content, changed review inputs, target overlap and recovery.

Before the target body exists, the optional `bootstrap_body` argument binds the external candidate and its initial-review file. The review binds candidate, ledger and source digests and retains pending execution acceptance. The writer reads those complete inputs before and after each change. An installed body or alias rejects this path. Complete semantic review remains the caller's responsibility. Use `mise run ledger -- --help` for the exact JSON fields, failure conditions, restoration and isolation limits.

For SKILL.md changes through `mise run ledger`, `body_revision` binds a separately retained previous-body snapshot or explicit absence and the initial-review file. The review also binds `previous_sha256`; `new_file` supplies the candidate. Full reads include the actual prior body before replacement and the installed candidate afterward. Body authority cannot exempt a supplied source, snapshot, review or candidate from overlap checks.

These are actual mechanical runs with explicit fixture source rules. They establish the shown effects, rejections and recovery. They do not establish semantic judgment, human review, whole-skill behavior, staged-writer integration, removals or final acceptance. The separate staged-writer regression suite covers creation, standardization and variants. Complete the separate semantic review and ledger invalidation before accepting a skill change.
