# Write a file against its current governing inputs

This example removes the guess about creating and updating a reviewed file, requiring the caller's write root, and writing before the target body is installed. Load it when using `mise run ledger` with `write-file`. The [complete observed run](ledger-write-run.json) contains the user's words, visible reply, every exact command, working directory, stdout, stderr, exit code and complete input/output file contents. Each file value uses base64 to preserve bytes and line endings. The temporary directories identify the recorded run; choose your own authorized canonical root.

The user asked: “Write and update the prepared note. Also demonstrate creation before the skill body is installed, reject a missing candidate review, and recover from a current review.” The executor replied: “Both note creations and reviewed updates succeeded. Missing write-root and missing initial-review requests were rejected without file changes. The bootstrap runs read the external candidate and left SKILL.md uninstalled.”

The public command is `mise run ledger -- <request.json> --write-root <root>`. The observed commands disable task caching and appear verbatim in the run record. Its isolated runtime was present before these commands; the record identifies its prerequisite files separately from command effects.

| Case | Observed result | File effect |
| --- | --- | --- |
| Create | Exit 0, native workflow success. | Created the prepared note. |
| Omit the write root | Exit 1 before workflow dispatch. | No file changed. |
| Reviewed replacement | Exit 0, native workflow success. | Replaced the note after binding its current digest. |
| Bootstrap creation | Exit 0, native workflow success. | Created the note using the external reviewed body; no target body was installed. |
| Omit the bootstrap review | Exit 1 before workflow dispatch. | No file changed. |
| Bootstrap recovery | Exit 0, native workflow success. | Replaced the note after supplying the required review and current file digest. |

For `mise run ledger`, the request binds the ledger, independently supplied governing documents, original source, frozen inventory, body, prepared file and expected destination digest. Creation uses a null expected digest; replacement uses the actual digest. The caller selects the authorized write root outside request data and supplies one declaration per actual review field. These declarations do not authenticate judgment or confer permission.

Before the target body exists, the optional `bootstrap_body` argument binds the external candidate and its initial-review file. The review binds candidate, ledger and source digests and retains pending execution acceptance. The writer reads those complete inputs before and after each change. An installed body or alias rejects this path. Complete semantic review remains the caller's responsibility. Use `mise run ledger -- --help` for the exact JSON fields, failure conditions, restoration and isolation limits.

These are actual mechanical runs with explicit fixture source rules. They establish the shown effects, rejections and recovery. They do not establish semantic judgment, human review, whole-skill behavior, scaffold or standardization write integration, body installation or final acceptance. Complete the separate semantic review and ledger invalidation before accepting a skill change.
