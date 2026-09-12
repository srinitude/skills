# Write a file against its current governing inputs

Return to the [SKILL.md change-control rules](../SKILL.md) for the governing body, ledger, graph, authority and acceptance requirements.

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

## Authorized prerequisite with pending body validation

Use this branch only when the actual authority explicitly permits a necessary prerequisite before integrated body validation. The ordinary default still rejects an unfinished body review. Select the exception outside request JSON:

```sh
mise run ledger -- <request.json> --write-root <root> --pending-body-review <review-sha256>
```

Bind that exact digest to `initial_body_review` or `body_revision.review`. Keep `initial_contract_validation.state` and `execution_acceptance` equal to `pending`; retain the ordinary source, ledger, candidate, previous-body and reviewer fields. Add `prerequisite` with exactly these keys:

- `change_sha256`: SHA-256 of the complete `change` object encoded as UTF-8 JSON with sorted keys, unescaped Unicode and compact comma/colon separators. In Python, use `json.dumps(change, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()`. Modes and review declarations are part of this binding.
- `reason`: the nonempty necessity and authorized dependency exception.
- `pending_validation`: a nonempty list naming the remaining checks. Do not declare an unfinished review complete.

The caller must establish actual authority and semantic coverage. Neither the selected digest nor these declarations authenticate approval. Preserve all other input, path, overlap, identity, mode, locking and restoration checks. Changed request content needs a renewed review and caller selection. Bootstrap rejects this exception; lineage, catalog, scaffold, standardization and registry consumers retain their existing default gate unless their own reviewed interface explicitly supports it.

The regression suite exercises real writes, missing caller selection, request-data injection, a mismatched digest, changed permissions, body replacement and post-write review drift with restoration and recovery. These cases do not prove complete semantic review, independent protection or final acceptance. Keep the whole-file and dependent integration checks pending until their actual evidence passes. Return to the [body's review rules](../SKILL.md#review-and-change-through-the-ledger) for the required before/after capture, affected semantic review and valid reuse conditions.

## Refresh derived lineage from the same review

The following commands belong to the factory's standalone lineage interface; use them only in a skill that owns that interface. Lineage uses the ordinary review above because its metadata changes a skill file. Start with `mise run lineage -- --plan` and save the returned `content_utf8` unchanged as the prepared file, including its two-space JSON indentation and final newline. Supply `initial_body_review`, the complete governing input bindings and a `change` targeting `evals/source-lineage.json`. Then use `mise run refresh-lineage -- --review <absolute-request.json>`. Mise requires that argument before starting the prerequisite checks; the writer validates its contents again at the effect. Every declared refresh prerequisite must pass.

The [exact portable lineage run](lineage-public-run.json) records eight real CLI cases, complete input/output bytes, commands, working directories, standard output/error and exit codes. Its isolated factory copy uses Mise to select Python and PyYAML. It exercises the standalone Python owner directly; it does not run the full factory refresh prerequisite chain. The separate full native refresh proof belongs to the current factory update and retains its private governing inputs outside this portable example.

| Case | Observed result | File effect |
| --- | --- | --- |
| Help | Exit 0, current lineage usage and review contract. | None. |
| Plan | Exit 0, exact prepared JSON text. | None. |
| Missing review | Exit 1, required review rejected. | None. |
| Reviewed creation | Exit 0, current derived metadata accepted by the file predicate. | Created lineage. |
| Stale package | Exit 1 after an owned file changed. | None. |
| Edited metadata | Exit 1 despite a matching prepared-file digest. | None. |
| Current review recovery | Exit 0 after replanning current package bytes. | Replaced lineage. |
| Check | Exit 0, recorded lineage matches the current package. | None. |

The derivation predicate must return exactly `True` before and after installation under the cooperating package lock. Changed package files or request bytes, `False`, `None`, and exceptions cannot become success. A failed post-check restores this writer's prior lineage bytes and mode only while its installed bytes still own that destination, preserving independent edits. Regression cases separately exercise the lock, source/request interference and restoration; those cases do not prove hostile-writer isolation.

These outcomes cover the standalone lineage owner. A parent maintenance command still needs current reviews for each of its own effects and must provide the appropriate lineage request. A post-dependency can run after parent failure and does not supply permission, accepted parent output or final acceptance. Successful parent catalog maintenance and complete registry acceptance remain separate obligations.

## Plan and review catalog maintenance

This section owns the detailed catalog procedure routed from the [generation contract](../references/generation-contract.md); load it through `mise run mise-primitives-plan` before catalog review and final maintenance.

Run `mise run mise-primitives-plan` to read the official schema for the selected Mise version and receive its exact catalog in `content_utf8`. Save those bytes unchanged. The ordinary review above targets `assets/mise-primitives-catalog.json`, binds its current digest, and supplies the current initial-body review and all governing inputs. The declared timezone-aware `checked_at` records the planning observation; it does not authenticate a clock or human judgment. The catalog writer checks the selected version, schema and exact request/prepared bytes at both sides of its effect and preserves disposition files.

The [complete catalog record](catalog-public-run.json) contains ten actual runs: help, the native plan, missing parent arguments, missing writer review, reviewed replacement, stale review, edited metadata, changed schema, current-review recovery and the final catalog check. The plan read the actual selected-release schema. The standalone effect commands used that real version and the explicitly captured official schema file. Rejections changed no package file; successful effects preserved mode `0640` and disposition bytes. The record retains exact commands, streams, exit codes and all 240 before/after file values. Its historical runtime file identities are prerequisites of those observations.

The record uses the same lossless XZ/base64 envelope as the other complete factory examples. With Python's standard-library `json`, `lzma`, `base64` and `hashlib`, decode `raw = lzma.decompress(base64.b64decode(envelope["record_xz_base64"]))`, verify `hashlib.sha256(raw).hexdigest() == envelope["record_sha256"]`, then read `json.loads(raw)`. No input, output, file content or limit is omitted. This is storage reduction, not a measured execution speed gain.

After outcome and acceptance work, the factory's final maintenance command is `mise run mise-primitives-update -- --catalog-review <absolute-catalog-request.json> --lineage-review <absolute-lineage-request.json>`. The lineage request must describe the resulting package, including the exact prospective catalog bytes. An independent generated skill without owned lineage instead requires `--review <absolute-catalog-request.json>`. An output that owns lineage must declare its own independent current-review handoff. Preserve values, order and repetitions through native dependency arguments.

Argument presence gates entry before self-update; it does not validate review contents or confer permission. A changed selected version or schema invalidates a prepared catalog, requiring a new read-only plan and current reviews. The full final-phase self-update, catalog effect and successful lineage post-task did not run in this example because outcome work was still underway. A post-task may run after a started parent fails. These observed predicates and explicit fixture declarations leave authentic semantic/human review, the full parent success path and final acceptance pending.


## Review registry files under their actual owners

Load this section when the factory owns `refresh-registry-lineage`. Start with `mise run refresh-registry-lineage -- <skill...> --plan`. It calculates native formatted bytes and derived lineage/manifest records without bulk file writes. Reject missing review input before formatter execution on the write route. `plan.changes` contains complete `content_base64`, current and prepared digests, ordinary modes, the skill and the actual owner for every changed file. All selected body changes precede source changes, lineage and repository manifests. This known maintenance order does not replace the ledger's full semantic dependency review.

Decode and save the first change's complete prepared bytes, then supply its current `write-file` request to `mise run refresh-registry-lineage -- <skill...> --review <request.json>`. A body change requires its separate `body_revision`; other files require the installed body's current `initial_body_review`. The command applies at most the next file, preserves its planned mode and rechecks request, runtime, sources, target bytes/directories and formatter inputs around the effect. Replan and review the next change. Earlier successful writes remain in place; a failed current effect uses the shared conditional-restoration rules. An empty final plan still needs full source, domain and recipient validation.

A repository-owned manifest uses its repository-relative `evidence/ports/<skill>/source-manifest.json` path. The trusted registry consumer chooses that exact related target; the installed skill body supplies its review context. Request data cannot broaden filesystem authority, and related targets reject bootstrap and body-revision modes. Archived native identity, repository-baseline identity and target-scaffolding attribution retain their distinct rules.

The [complete registry run](registry-public-run.json) records actual public native help, missing/stale review rejection, individually reviewed source formatting, lineage and related-manifest effects, plus complete read-only plans and the final empty plan. Source mode `0640` and manifest mode `0600` survive. Its read-only plan commands use temporary aliases to the selected executable bytes; native effects use the unmodified public task and independently rederive current bytes. Decode its lossless XZ/base64 envelope using the catalog section's instructions. Every command, stream, exit code and fixture input/output file is retained; these explicit fixture reviews do not authenticate semantic judgment or prove whole-goal acceptance.

Native formatting uses file-info and stdin output with selected Node permission controls. The tested incidental configuration write is denied; ignored/unsupported parser content remains unchanged. A configured but unavailable formatter blocks its consumer, and unbound `NODE_OPTIONS` injection is rejected. Record the exact formatter command and each consumer's ancestor configuration candidates, including nested configurations; recheck them at use. These controls are not hostile-code isolation or complete dynamic-plugin/environment dependency capture. Separate real regression cases cover body revision, changed source after an actual write, conditional manifest restoration, preserved earlier lineage and recovery.

## Capture and render the recorded file graph

This example removes the guess about preserving repeated connectors, rejecting invalid input and choosing a new output directory. Load it when using the ledger's `file-graph` action or `mise run render-file-graph`. The [complete graph run](graph-public-run.json) retains eight actual standalone CLI runs, their commands, streams, exit codes and complete fixture input/output bytes in the lossless envelope described above.

First supply a `file-graph` request with the current ledger path, its exact `ledger_sha256` and a positive incidence `budget`. Capture the native result unchanged. The graph retains individual file nodes, typed relationship records, endpoint order, repetitions, projection gaps and the task/file-set ownership index needed to reconstruct the projection. The recorded snapshot does not prove current live files or accepted relationship meaning.

The public task sequence is:

```sh
mise run ledger -- <request.json> > <native-result.json>
mise run render-file-graph -- <native-result.json> <new-output-directory> --sha256 <native-result-sha256> --timeout <positive-seconds>
```

The renderer's parent task installs the browser selected by the locked runtime after its prerequisites pass. The destination must be new, outside the skill, with an existing parent. It retains the native result, Mermaid source, renderer configurations, actual output streams, SVG and topology proof. Promote a required owned artifact only through its reviewed file-write route. Renderer failure can leave diagnostic output; inspect it and use a new destination for recovery.

The worked record uses the standalone owners through `mise exec` with an already installed locked runtime. It does not run or claim the complete parent prerequisite chain. Its two-file fixture rejects an insufficient incidence budget, recovers with a sufficient budget, rejects non-object JSON and a wrong digest without creating output, renders successfully, rejects an existing output directory and reproduces identical SVG bytes in a second directory. Both parallel connector identities survive.

Verify the exact bound input, every rendered file node and connector, and retained projection meaning. Then inspect rendered geometry and pixels for readability. The example proves its recorded mechanical results only; complete live inventory, semantic and human review, full parent execution, independent output acceptance and final skill acceptance remain separate obligations.
