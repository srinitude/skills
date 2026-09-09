/** Usage: mise run ledger -- request.json. Exit 0 returns a view, 1 rejects work, 2 is CLI misuse. */
import { readFile } from 'node:fs/promises';
import { readThroughOwner, runLedger } from './review_ledger_workflow.ts';

const help = `Usage: mise run ledger -- <request.json>
Read recorded ledger relationships through native Mastra.
Exit codes: 0 view, 1 failed input/workflow, 2 bad usage.
Example: mise run ledger -- review-request.json

Request JSON requires action, ledger (absolute file path), and ledger_sha256
(the 64-character lowercase SHA-256 of that file's exact current bytes).
Actions: catalog, show, relations, trace, check-capture, check-sources.
check-capture validates the documents present and the full source byte partition,
including source/clause byte and line locations. It does not read live originals.
check-sources also requires expected_documents (name, absolute path, sha256),
original_source (absolute path, sha256), and inventory_document (captured name).
The supplied inventory document binds source_sha256, source_bytes, source_lines
and exact frozen records keyed by stable ID, plus mapping_defaults when present.
Root records may follow dependency order; nested contents and JSON types stay exact.
These inputs must come from independent source authority. Each present captured
document needs one exact live binding.
Only show, relations and trace accept a selector.
show, relations and trace require selector, for example source:rule-id.
relations and trace accept direction: in, out or both (default both), and
relation_type from the ledger catalog. trace accepts depth: a nonnegative
safe integer (default 1). Zero depth keeps only the starting subject.

The result contains the whole current SKILL.md and a JSON-encoded view_text.
Views preserve asserted conditions, review states, recorded source context and
explicit facet inheritance. Historical observations keep their identity.
Source checks prove only supplied live bindings and the frozen source inventory.
The optional derived_relationships version-1 ledger profile adds declared clause,
group, section and source-links.json definition relations plus recorded reading
prerequisites. Historical declarations and current import observations stay distinct.
Unknown profile rules, missing references, stale observations and reading cycles reject.
Absent profiles retain asserted-only views. Task and other derived coverage, source
authority and semantic acceptance remain separate.
`;

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 1 && args[0] === '--help') {
    process.stdout.write(help);
    return;
  }
  if (args.length !== 1 || !args[0]) {
    process.stderr.write('Usage: mise run ledger -- <request.json>\n');
    process.exitCode = 2;
    return;
  }
  try {
    const request = await readThroughOwner('parse', new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(await readFile(args[0])));
    const result = await runLedger(request);
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
