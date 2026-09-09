/** Usage: mise run ledger -- request.json. Exit 0 returns a view, 1 rejects work, 2 is CLI misuse. */
import { readFile } from 'node:fs/promises';
import { readThroughOwner, runLedger } from './review_ledger_workflow.ts';

const help = `Usage: mise run ledger -- <request.json>
Read an asserted ledger relationship view through native Mastra.
Exit codes: 0 view, 1 failed input/workflow, 2 bad usage.
Example: mise run ledger -- review-request.json

Request JSON requires action, ledger (absolute file path), and ledger_sha256
(the 64-character lowercase SHA-256 of that file's exact current bytes).
Actions: catalog, show, relations, trace.
show, relations and trace require selector, for example source:rule-id.
relations and trace accept direction: in, out or both (default both), and
relation_type from the ledger catalog. trace accepts depth: a nonnegative
safe integer (default 1). Zero depth keeps only the starting subject.

The result contains the whole current SKILL.md and a JSON-encoded view_text.
Views preserve asserted conditions and review states; they do not imply truth,
semantic acceptance, inherited context or complete derived relationships.
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
