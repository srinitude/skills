/** Run one native rule task; the host model supplies its own work and tools. */
import { open, unlink } from 'node:fs/promises';
import { isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { openStorage } from './run_standardization.ts';
import { workflowRoots } from './standardization_workflow.ts';
import { publicResult } from './run_markdown.ts';
import { runRule, strictInput } from './rule_workflow.ts';

function options(args: string[]) {
  const [name] = args, request = process.env.SKILL_RULE_REQUEST, state = process.env.SKILL_RULE_STATE;
  if (args.length !== 1 || !name?.startsWith('rule:') || process.env.MISE_TASK_NAME !== name)
    throw Error('Start or resume one declared rule task through Mise');
  if (!request || !state || !isAbsolute(request) || !isAbsolute(state))
    throw Error('Set SKILL_RULE_REQUEST and SKILL_RULE_STATE to absolute paths');
  return { name, request, state, reply: process.env.SKILL_RULE_REPLY };
}

export async function main(args = process.argv.slice(2)) {
  let storage, lock, lockPath;
  try {
    const selected = options(args), root = fileURLToPath(new URL('../', import.meta.url));
    const python = process.env.UV_PYTHON;
    if (!python) throw Error('Use the Mise-resolved Python path');
    await workflowRoots({ factory: root, state: selected.state, environment: { UV_PYTHON: python } });
    storage = await openStorage(selected.state);
    // ponytail: one cooperating state writer; use per-run locks only if measured contention requires them.
    lockPath = join(selected.state, 'rule-workflow.lock');
    lock = await open(lockPath, 'wx', 0o600);
    const input = await strictInput(selected.request);
    const reply = selected.reply ? await strictInput(selected.reply) : undefined;
    const result = await runRule(root, storage, selected.name, input, reply);
    process.stdout.write(JSON.stringify({ ...publicResult(result, 'judgment'), execution_acceptance: 'pending',
      limit: 'Cooperative binding checks only. The model owns meaning; required human and skill acceptance remain separate.' }) + '\n');
    process.exitCode = result.status === 'success' ? 0 : result.status === 'suspended' ? 3 : 1;
  } catch (error) {
    process.stderr.write((error instanceof Error ? error.message : String(error)) + '\n');
    process.exitCode = 1;
  } finally {
    await storage?.close();
    if (lock) { await lock.close(); await unlink(lockPath!); }
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
