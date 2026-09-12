/** Usage: mise run ledger -- request.json [--write-root ROOT [--pending-body-review SHA256]]. Exit 0 returns a result, 1 rejects work, 2 is misuse. */
import { readFile } from 'node:fs/promises';
import { readThroughOwner, runLedger } from './review_ledger_workflow.ts';

const help = `Usage: mise run ledger -- <request.json> [--write-root ROOT [--pending-body-review SHA256]]
Read ledger relationships or apply one caller-scoped file change through native Mastra. Saved handoff help: --native-loop --help.
Exit codes: 0 result, 1 failed input/workflow, 2 bad usage.
Example: mise run ledger -- review-request.json

Request JSON requires action, ledger (absolute file path), and ledger_sha256
(the 64-character lowercase SHA-256 of that file's exact current bytes).
Actions: catalog, show, relations, trace, check-capture, check-sources, pairs, selections, work, impact, file-graph, write-file, native-file.
native-file requires phase: before or after and the same source/body/review/root bindings as write-file.
Its change adds operation: add, update or delete; mode requires expected and new ordinary permission bits.
Add uses null expected_sha256 and expected mode. Delete uses null new_file and new mode; SKILL.md cannot be removed.
Update binds both existing identity and replacement bytes. Add/update candidates must be UTF-8.
Each phase checks current inputs and file state without applying or restoring the native effect.
The result remains pending; returned checks are not complete READY evidence, authority or hook activation.
The current model performs authorized native effects between checks. The enclosing goal workflow owns
the persistent handoff, graph/lineage/authority checks, event correlation and required concurrency protection.
check-capture validates the documents present and the full source byte partition,
including source/clause byte and line locations. It does not read live originals.
check-sources and write-file also require expected_documents (name, absolute path, sha256),
original_source (absolute path, sha256), and inventory_document (captured name).
The supplied inventory document binds source_sha256, source_bytes, source_lines
and exact frozen records keyed by stable ID, plus mapping_defaults when present.
Root records may follow dependency order; nested contents and JSON types stay exact.
These inputs must come from independent source authority. Each present captured
document needs one exact live binding.
show, relations, trace, work and impact require selector. Other actions reject it.
Use a known subject ID, for example source:rule-id. impact requires file:<path>
for one recorded file, including a recorded missing file; a file set is not a file.
relations and trace accept direction: in, out or both (default both), and
relation_type from the ledger catalog. trace accepts depth: a nonnegative
safe integer (default 1). Zero depth keeps only the starting subject.

pairs requires scope (all or rules), offset, limit and budget. All includes every
indexed subject; rules selects only recorded obligation rows and their clauses.
Subject IDs sort by Unicode code point; ordered pairs include self-pairs.
selections requires offset, limit and selection: {members, size, order, repeats,
budget}. Members are unique existing subject IDs. Size is a nonnegative safe
integer; order is ordered or unordered; repeats is a boolean.
Both actions require offset as canonical nonnegative decimal text, e.g. "0".
Limit and each budget are positive safe integers. Counts, ranks and continuation
offsets return decimal strings without JavaScript integer rounding. Empty pools
and zero-length selections retain their mathematical meanings, not acceptance.
Ordered pools preserve input position; unordered membership uses Unicode code-point
ID order. Each result preserves meaningful sequence and repetition. Pages rank
results directly without rescanning earlier pages. Reuse the same ledger digest
and selection for continuation; a changed input invalidates the previous space.
Budgeted work slots cover pools and result work, not integer arithmetic cost or OS
time/memory. Infeasible requests reject rather than silently truncate or sample.
Candidates remain unreviewed. Conditions, roles, groups and higher-order meaning
remain in the actual relationship records. Enumeration does not prove vocabulary,
evidence, permission, required matrix use, semantic judgment or execution acceptance.

file-graph requires a positive safe-integer budget for the total file incidences.
It emits Mermaid source, individual stable file/connector IDs, exact original
records and explicit projection gaps from the recorded current package snapshot.
Non-file meaning and historical endpoints remain in records; task endpoints use
their explicit file owner. Endpoint order and repetition remain intact. The budget
rejects excess incidences before Cartesian expansion; it is not an OS resource cap.
This read action does not write, render, check live files or accept topology.

work and impact expose the complete recorded review workflow, review fields,
body-hub decisions and mechanism map beside the selected subject and its inherited
context. The workflow requires consecutive integer step numbers starting at 1,
nonempty action/rule text, review records with nonempty field/review text, and
nonempty body_hub/mechanism_map objects. Extension fields remain intact.
Stored states may be historical. These views perform no work, writes, invalidation,
judgment or acceptance. File observations are not live file proof. Resolve current
owners and evidence before an effect; no warning or returned record is a write guard.

write-file requires --write-root with an absolute canonical directory, selected by
its authorized caller outside request data. Read actions reject this argument.
It also requires change: {path, expected_sha256, new_file, body_sha256, reviewer,
review}. Path is a canonical relative file with existing parent directories. SKILL.md
requires the explicit body_revision input below; body case aliases reject.
expected_sha256 is the current file digest, or null for exclusive creation.
new_file has an absolute path and sha256; its actual binary bytes are installed.
body_sha256 binds the target root's nonempty UTF-8 SKILL.md, or the explicit
bootstrap candidate described below. Body case aliases reject.
review supplies one nonempty
string per exact field in the actual ledger's reusable_review_protocol. reviewer
and review remain caller declarations, never authenticated judgment or permission.
The caller first performs the required semantic review and establishes source authority.
The owner reads the whole current ledger, body and every supplied governing input
before and after this individual write, including repeats. Missing/stale bindings,
unsafe paths, links, physical input aliases/overlap, creation collisions, unchanged writes and stale
replays reject before mutation. Existing file modes stay intact; new files use 0644.
The existing package lock serializes cooperating promotion and file writers.
Replacement is atomic; creation is exclusive. Post-check failure attempts restoration
only while the target still matches this write and required inputs remain readable.
Restoration also reads all inputs before and after; drift stays failed. Unreadable
inputs can prevent restoration, and independent target edits are never overwritten.
This is not crash rollback, hostile-writer isolation or a cross-file transaction.
Scaffold creation, standardization and variant staging explicitly use this guard.
Removals and remaining maintenance writers need their own integration, semantic
review and ledger invalidation before acceptance.

Ordinary file writes require initial_body_review: {path, sha256}, binding a separate
absolute regular-file review of the installed body. Its JSON uses the current
candidate_sha256, ledger_sha256, source_sha256 and initial-review fields below.
The complete review is captured and checked before and after each write; stale,
incomplete, overlapping or changed review inputs reject. Do not combine this
field with bootstrap_body or body_revision. Read actions reject all three fields.
The record declares initial contract validation while full acceptance stays pending.

Before a target SKILL.md exists, write-file may supply bootstrap_body: {body, review}.
Each member is an absolute regular-file path and exact sha256 binding. Read actions
reject bootstrap_body. The candidate must be nonempty UTF-8 and match body_sha256.
The review JSON binds candidate_sha256, ledger_sha256 and source_sha256 to current
inputs, keeps execution_acceptance: "pending", and supplies initial_contract_validation:
{state: "PASS", reviewer, method, limit}, with nonempty reviewer/method/limit text.
Extension fields remain intact. These are declared initial-review results, not
machine proof of complete meaning, authenticated judgment or final acceptance.
The writer reads the full candidate and review before and after each write, plus
all normal governing inputs. Any installed body or case alias rejects bootstrap.
This route creates no SKILL.md and never hides an installed one. It supports the
required task/test/script build order after initial candidate review. Scaffold,
standardization and variant staging preserve this gate through their shared writer.

For SKILL.md creation/replacement, supply body_revision: {previous, review} instead
of bootstrap_body. previous is null for creation or an absolute, separately retained
old-body snapshot with sha256 for replacement. review is an absolute path/sha256
binding. new_file supplies the nonempty UTF-8 candidate. expected_sha256 matches
previous or null; body_sha256 matches the previous body or the candidate for creation.
The review uses the initial-review fields above and also requires previous_sha256,
matching that prior identity or explicitly null. Candidate, source and ledger remain
bound. Before/after captures read all governing inputs, the snapshot and review;
replacement reads the actual old body before and the installed candidate afterward.
Creation requires absence and then exact installed candidate readback. Supplied
sources, snapshots, reviews and candidates cannot overlap the destination. Modes
and independent edits retain the existing preservation and restoration rules.
Review text remains a declaration with semantic, human and final acceptance pending.

For an explicitly authorized prerequisite before integrated body validation, the
caller may select --pending-body-review SHA256 outside request data. It must match
the bound initial_body_review or body_revision.review digest. The review retains
initial_contract_validation.state: "pending" and execution_acceptance: "pending".
Its prerequisite object has exactly change_sha256, reason and pending_validation.
Hash the complete change object as UTF-8 JSON with sorted keys, no added spaces and
unescaped Unicode, binding modes and review fields too. reason is nonempty text;
pending_validation is a nonempty list of nonempty strings. Normal review
fields and all before/after bindings remain required. Bootstrap rejects this mode.
The flag selects a declared exception; it does not authenticate authority, judge
necessity, certify semantic coverage or finalize the file. The caller must establish
actual approval and complete every remaining validation. Other writers remain strict.

The result contains the whole current SKILL.md and a JSON-encoded view_text.
Views preserve asserted conditions, review states, recorded source context and
explicit facet inheritance. Historical observations keep their identity.
Source checks prove only supplied live bindings and the frozen source inventory.
The optional derived_relationships version-1 ledger profile adds declared clause,
group, section and source-links.json definition relations plus recorded reading
prerequisites. Historical declarations and current import observations stay distinct.
Version-2 python-imports-and-toml-tasks-v2 task observations must match the recorded
current file digest. Task selectors such as task:mise.toml#build expose their whole
declarations, conditions, arguments, environment, repeated occurrences and file context.
Same-file literal depends, depends_post and wait_for references add conditional
executes-before edges; structured run/run_windows entries add references with their
sequence positions and parallel groups. Shell entries remain in the declaration.
Aliases, patterns, templates, includes, inheritance, external references and argument
interpolation need native resolution; unresolved forms remain visible. No declaration
proves native task selection, execution, live files or acceptance.
Unknown profile rules, missing references, stale observations and reading cycles reject.
Absent profiles retain asserted-only edges. Other derived coverage, source authority
and semantic acceptance remain separate.
`;

async function main() {
  const args = process.argv.slice(2);
  if (args[0] === '--native-loop') return (await import('./native_file_workflow.ts')).runNativeHandoff(args.slice(1));
  if (args.length === 1 && args[0] === '--help') {
    process.stdout.write(help);
    return;
  }
  const pending = args.length === 5 && args[3] === '--pending-body-review' ? args[4] : undefined;
  const writing = (args.length === 3 || pending !== undefined) && args[1] === '--write-root' && Boolean(args[2]);
  if ((!writing && args.length !== 1) || !args[0]) {
    process.stderr.write('Usage: mise run ledger -- <request.json> [--write-root ROOT [--pending-body-review SHA256]]\n');
    process.exitCode = 2;
    return;
  }
  try {
    const request = await readThroughOwner('parse', new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(await readFile(args[0])));
    const result = await runLedger(request, writing ? args[2] : undefined, pending);
    const report = { run_id: result.run_id, status: result.status,
      steps: Object.fromEntries(Object.entries(result.steps).filter(([id]) => id !== 'input').map(([id, step]) => [id, { status: step.status }])),
      result: result.status === 'success' ? result.result : undefined,
      error: result.status === 'success' ? undefined : result.status === 'failed' ? result.error.message : `Ledger workflow ${result.status}` };
    process.stdout.write(JSON.stringify(report) + '\n');
    if (result.status !== 'success') process.exitCode = 1;
  } catch (error) {
    process.stderr.write((error instanceof Error ? error.message : String(error)) + '\n');
    process.exitCode = 1;
  }
}

await main();
