# Write a file against its current governing inputs

Return to the [SKILL.md change-control rules](../SKILL.md) for the governing body, ledger, graph, authority and acceptance requirements.

Load this procedure before a manual native effect or reviewed `write-file` output. It covers create/update, current initial-body review, caller-selected root, bootstrap and body install/replace. The [observed run](ledger-write-run.json) keeps the exact user/reply text, commands, working directories, stdout, stderr, exit codes and all input/output files. Base64 preserves bytes and line endings. Recorded temporary paths are evidence; choose your own authorized canonical root.

The user asked: “Show the file-write inputs, write and update the prepared note under a current initial-body review, reject malformed or incomplete review bindings, and recover. Also demonstrate reviewed bootstrap writes and body installation or replacement.” The executor replied: “The current help names the required review. Malformed and incomplete ordinary-review bindings, missing write root and missing bootstrap or body-revision reviews were rejected without file changes. Current reviewed inputs enabled the note, bootstrap and body transitions.”

Use `mise run ledger -- <request.json> --write-root <root>`. The record keeps verbatim commands with task caching disabled. It separates the preinstalled isolated runtime and its prerequisite files from effects.

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

Bind the ledger, independently supplied governing documents, original source, frozen inventory, body, prepared file and expected target digest. Use null for creation and the actual digest for replacement. Select the authorized root outside request data. Supply each actual review field. Declarations prove neither judgment nor permission.

For ordinary nonbody writes, bind `initial_body_review` by absolute path and digest. It is a separate review of the exact installed body, ledger and source. Declare initial contract validation; keep full acceptance pending. Read and check the whole review before and after. Reject absent, stale, overlapping or changed reviews. Do not combine it with `bootstrap_body` or `body_revision`. Shipped cases reject malformed/incomplete bindings before dispatch. Separate tests cover absent/stale content, changed inputs, target overlap and recovery.

Use `bootstrap_body` only before the target body exists. Bind the external candidate and initial review, including candidate, ledger and source digests. Keep execution acceptance pending. Read all inputs before and after each change. An installed body or alias rejects bootstrap. The caller must review meaning. Run `mise run ledger -- --help` for exact JSON fields, rejection, restoration and isolation limits.

For SKILL.md changes, `body_revision` binds a retained prior-body snapshot or explicit absence, plus the initial review. Bind `previous_sha256`; use `new_file` for the candidate. Read the real prior body before replacement and installed candidate afterward. Body authority exempts no source, snapshot, review or candidate from overlap checks.

These real fixture runs prove the shown effects, rejections and recovery. They prove no semantic/human review, whole-skill behavior, staged integration, removal or final acceptance. Separate staged-writer tests cover creation, standardization and variants. Finish semantic review and ledger invalidation before accepting a change.

## Use the model's native file tool

Load this section before every manual file effect. Also read the review branch that fits the change. Keep the required ledger, source, body and graph checks.

1. Check the current model's native tool schema. An alias is not a callable tool. A host bridge may call it. Do not substitute a shell writer, another model or new API.
2. Bind exact inputs and one change in a `native-file` request with `phase: before`. Wrap it in `run_id`, `turn`, `baseline`, `iteration` and `request`. Caller-owned run records grant no authority.
3. Use canonical absolute paths and private, caller-owned state outside the skill. Run the command below. Exit 3 means saved and awaiting the native effect, not failed or accepted.
4. Read the returned operation and bound inputs. At READY, make only that authorized native change. Missing host handoff support keeps affected work pending.
5. Record the observed reply: `run_id`, `request_sha256`, `tool`, `status`, `result`. Status is `success`, `error` or `interrupted`. Resume the same envelope/state with `--reply`. Never repeat the effect to resume.
6. Read back bytes, mode or absence. Exit 0 proves this readback passed; skill acceptance stays pending. A tool reply alone proves no effect.

```sh
mise run ledger -- --native-loop /path/request.json --write-root /path/skill --state /path/state
mise run ledger -- --native-loop /path/request.json --write-root /path/skill --state /path/state --reply /path/reply.json
```

A `native-file` change has `operation`, `path`, `expected_sha256`, `new_file`, `body_sha256`, `reviewer`, `review` and `mode`. Choose `add`, `update` or `delete`. Add requires an absent target and null expected digest. Delete requires null `new_file` and cannot remove SKILL.md. Add/update bind exact UTF-8 candidate bytes.

### Bind permissions and check failure

In `change.mode`, bind integer `expected` and `new` bits from 0 to 511 (`0o777`). Add uses null expected; delete uses null new. Updates bind both, including mode-only changes. Reject stale modes, privileged bits, aliases and overlap.

The separate `write-file` writer defaults to the old mode or `0o644` for creation. Its optional mode field permits no deletion. Use it only for explicitly authorized generator, formatter, binary or other required output contracts. Preserve callers and checks.

Reject collisions, path escape, symlinks, hard-link aliases and unsupported removal. Before deletion, verify recovery and preserve or transfer required behavior. Then verify absence and surviving dependencies. A failed call may have changed files. Inspect disk before retrying; retain failure and partial effects. Recovery needs existing authority.

The saved workflow protects each call, not the gap around the model's native effect. It supplies no cross-call isolation or automatic rollback; never claim those controls. Reviews grant no permission or semantic/human acceptance.

## Authorized prerequisite with pending body validation

Use this branch only when actual authority explicitly permits a necessary prerequisite before integrated body validation. Otherwise, unfinished body review fails. Select the exception outside request JSON:

```sh
mise run ledger -- <request.json> --write-root <root> --pending-body-review <review-sha256>
```

Bind the exact digest to `initial_body_review` or `body_revision.review`. Keep `initial_contract_validation.state` and `execution_acceptance` as `pending`. Retain source, ledger, candidate, prior-body and reviewer fields. Add `prerequisite` with exactly these keys:

- `change_sha256`: SHA-256 of the complete `change` object encoded as UTF-8 JSON with sorted keys, unescaped Unicode and compact comma/colon separators. In Python, use `json.dumps(change, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()`. Modes and review declarations are part of this binding.
- `reason`: the nonempty necessity and authorized dependency exception.
- `pending_validation`: a nonempty list naming the remaining checks. Do not declare an unfinished review complete.

The caller must prove authority and semantic coverage; digests and declarations do not authenticate approval. Keep all input, path, overlap, identity, mode, lock and restoration checks. Changed request content needs fresh review and caller selection. Bootstrap rejects this exception. Lineage, catalog, scaffold, standardization and registry stay strict unless their own reviewed interface explicitly supports it.

Real regression tests cover writes, missing caller selection, request injection, wrong digest, changed modes, body replacement and post-write review drift, restoration and recovery. They prove no full semantic review, independent protection or final acceptance. Keep whole-file/dependent checks pending until proved. Follow the [body review rules](../SKILL.md#review-and-change-through-the-ledger) for pre/post capture, affected semantic review and valid reuse.

## Refresh derived lineage from the same review

Use these commands only in a skill that owns the factory's standalone lineage interface. Lineage changes a skill file, so it needs ordinary review. Run `mise run lineage -- --plan`; save `content_utf8` unchanged, including two-space JSON indent and final newline. Bind `initial_body_review`, all governing inputs and a `change` for `evals/source-lineage.json`. Run `mise run refresh-lineage -- --review <absolute-request.json>`. Mise requires that argument before prerequisites; the writer checks its contents at the effect. All declared prerequisites must pass.

The [portable lineage run](lineage-public-run.json) keeps eight real CLI cases with all input/output bytes, commands, directories, stdout/stderr and exit codes. Its isolated factory copy uses Mise-selected Python/PyYAML and the standalone Python owner, not the full refresh chain. Full native refresh proof and its private inputs belong outside this example.

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

Under the cooperating package lock, the derivation predicate must return exactly `True` before and after install. Reject changed package/request bytes, `False`, `None` and exceptions. On failed post-check, restore this writer's prior bytes/mode only while its installed bytes still own the target. Preserve independent edits. Separate lock, source/request interference and restoration tests prove no hostile-writer isolation.

This proves the standalone lineage owner. Parent maintenance still needs current reviews for each effect and the right lineage request. A post-dependency may run after parent failure; it grants no permission, accepted parent output or final acceptance. Parent catalog success and full registry acceptance need separate proof.

## Plan and review catalog maintenance

This is the catalog procedure linked from the [generation contract](../references/generation-contract.md). Load it through `mise run mise-primitives-plan` before catalog review and final maintenance.

Run `mise run mise-primitives-plan` to read the selected Mise version's official schema. Save its exact `content_utf8` catalog unchanged. Bind ordinary review to the current `assets/mise-primitives-catalog.json` digest, initial-body review and all inputs. Timezone-aware `checked_at` declares the plan observation, not an authenticated clock or human judgment. Before and after the effect, check version, schema and exact request/prepared bytes. Preserve disposition files.

The [catalog record](catalog-public-run.json) keeps ten real cases: help, native plan, missing parent args, missing writer review, reviewed replacement, stale review, edited metadata, changed schema, recovery and final check. Plan and standalone effects used the selected version and captured official schema. Rejections changed no package files. Success preserved `0640` and disposition bytes. Exact commands, streams, exits and all 240 before/after file values remain, bound to historical runtime prerequisites.

For lossless XZ/base64 records, use Python's standard `json`, `lzma`, `base64` and `hashlib`. Decode `raw = lzma.decompress(base64.b64decode(envelope["record_xz_base64"]))`. Verify `hashlib.sha256(raw).hexdigest() == envelope["record_sha256"]`, then read `json.loads(raw)`. No input, output, content or limit is omitted. This saves storage; it proves no execution speed gain.

After outcome and acceptance work, run `mise run mise-primitives-update -- --catalog-review <absolute-catalog-request.json> --lineage-review <absolute-lineage-request.json>`. Bind lineage to the resulting package, including exact planned catalog bytes. Independent outputs without lineage instead need `--review <absolute-catalog-request.json>`. Outputs that own lineage need their own current-review handoff. Native dependency arguments must preserve values, order and repeats.

Argument presence gates entry before self-update; it validates neither content nor permission. Version/schema changes invalidate the catalog: replan read-only and renew reviews. This example did not run final self-update, catalog effect or successful lineage post-task because outcome work was pending. A post-task may run after a started parent fails. Real semantic/human review, full parent success and final acceptance stay pending.


## Review registry files under their actual owners

Load this section if the factory owns `refresh-registry-lineage`. Run `mise run refresh-registry-lineage -- <skill...> --plan` for native formatted bytes and derived lineage/manifests without bulk writes. The write route rejects missing review before formatting. Each `plan.changes` entry has full `content_base64`, current/prepared digests, ordinary modes, skill and owner. Order selected bodies before sources, lineage and repository manifests. This does not replace full semantic dependency review.

Save the first change's exact decoded bytes. Give its current `write-file` request to `mise run refresh-registry-lineage -- <skill...> --review <request.json>`. Bodies need `body_revision`; other files need current installed-body `initial_body_review`. Apply at most the next file with its planned mode. Recheck request, runtime, sources, target bytes/directories and formatter inputs around the effect. Replan/review next. Keep prior successful writes; use conditional restoration for the failed current effect. An empty plan still needs full source, domain and recipient validation.

The trusted registry consumer selects the exact repository-relative `evidence/ports/<skill>/source-manifest.json` target. The installed body supplies review context. Request data grants no wider filesystem authority. Related targets reject bootstrap/body revision. Keep distinct rules for archived native identity, repository-baseline identity and target-scaffolding attribution.

The [registry run](registry-public-run.json) keeps public help, missing/stale review rejection, reviewed source formatting, lineage and related-manifest effects, full read-only plans and final empty plan. It preserves source `0640` and manifest `0600`. Plan commands use temporary aliases to selected executable bytes; effects use the unmodified public task and derive current bytes anew. Use the catalog section to decode XZ/base64. All commands, streams, exits and fixture input/output files remain. Fixture reviews prove neither semantic judgment nor full acceptance.

Native formatting uses file-info, stdin output and selected Node permissions. The tested incidental config write is denied; ignored/unsupported parser content stays unchanged. Missing configured formatters block consumers. Reject unbound `NODE_OPTIONS`. Record and recheck exact formatter commands and each consumer's ancestor config candidates, including nested configs. This is neither hostile-code isolation nor full dynamic-plugin/environment capture. Separate real tests cover body revision, source changes after writes, conditional manifest restoration, earlier-lineage preservation and recovery.

## Capture and render the recorded file graph

Load this section for `file-graph` or `mise run render-file-graph`. It covers repeated connectors, invalid inputs and new output paths. The [graph run](graph-public-run.json) keeps eight real standalone CLI cases with all commands, streams, exits and fixture bytes in the lossless envelope above.

Bind a `file-graph` request to the current ledger path, exact `ledger_sha256` and positive incidence `budget`. Keep the native result unchanged: individual nodes, typed records, endpoint order, repeats, projection gaps and task/file-set ownership index. This permits rebuilding the projection; a snapshot proves no live files or accepted meaning.

The public task sequence is:

```sh
mise run ledger -- <request.json> > <native-result.json>
mise run render-file-graph -- <native-result.json> <new-output-directory> --sha256 <native-result-sha256> --timeout <positive-seconds>
```

After prerequisites, the parent task installs the locked runtime's browser. Use a new destination outside the skill with an existing parent. Keep the native result, Mermaid, renderer configs, actual streams, SVG and topology proof. Promote owned artifacts only through reviewed file writes. After renderer failure, inspect any diagnostic output and use a new destination to recover.

The record uses standalone owners through `mise exec` with the locked runtime preinstalled, not the full parent chain. Its two-file fixture rejects a low incidence budget, recovers with enough budget, rejects non-object JSON and wrong digest without output, renders, rejects an existing destination and reproduces identical SVG bytes elsewhere. Both parallel connector IDs survive.

Verify bound inputs, every rendered node/connector and projection meaning. Inspect geometry and pixels for readability. These recorded mechanical results leave live inventory, semantic/human review, full parent runs, independent outputs and final skill acceptance separate.
