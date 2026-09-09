/** Usage: mise run ledger -- request.json [--write-root ROOT]. Exit 0 returns a result, 1 rejects work, 2 is misuse. */
import { readFile } from 'node:fs/promises';
import { readThroughOwner, runLedger } from './review_ledger_workflow.ts';

const help = `Usage: mise run ledger -- <request.json> [--write-root ROOT]
Read ledger relationships or apply one caller-scoped file change through native Mastra.
Exit codes: 0 result, 1 failed input/workflow, 2 bad usage.
Example: mise run ledger -- review-request.json

Request JSON requires action, ledger (absolute file path), and ledger_sha256
(the 64-character lowercase SHA-256 of that file's exact current bytes).
Actions: catalog, show, relations, trace, check-capture, check-sources, pairs, selections, work, impact, write-file.
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
review}. Path is a canonical relative non-body file with existing parent directories.
expected_sha256 is the current file digest, or null for exclusive creation.
new_file has an absolute path and sha256; its actual binary bytes are installed.
body_sha256 binds the target root's nonempty UTF-8 SKILL.md. Body case aliases reject.
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
Body rewrites, removals and other scaffold/update/maintenance writers remain outside
this guard. Finish their integration, semantic review and ledger invalidation separately.

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
  if (args.length === 1 && args[0] === '--help') {
    process.stdout.write(help);
    return;
  }
  const writing = args.length === 3 && args[1] === '--write-root' && Boolean(args[2]);
  if ((!writing && args.length !== 1) || !args[0]) {
    process.stderr.write('Usage: mise run ledger -- <request.json> [--write-root ROOT]\n');
    process.exitCode = 2;
    return;
  }
  try {
    const request = await readThroughOwner('parse', new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(await readFile(args[0])));
    const result = await runLedger(request, writing ? args[2] : undefined);
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
