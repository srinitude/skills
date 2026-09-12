/** Public Markdown gates. State uses the existing Mastra storage owner. */
import { lstat, realpath } from 'node:fs/promises';
import { isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { bound } from './standardization_workflow.ts';
import { openStorage } from './run_standardization.ts';
import { markdownWorkflows, phases, questions, stages, requestSchema, runPhase } from './markdown_workflow.ts';

function options(args: string[]) {
  if (args.length !== 1 || !phases.includes(args[0] as typeof phases[number]))
    throw new Error('Use one phase: ' + phases.join(', '));
  const request = process.env.SKILL_MARKDOWN_REQUEST, state = process.env.SKILL_MARKDOWN_STATE;
  if (!request || !state || !isAbsolute(request) || !isAbsolute(state))
    throw new Error('Set SKILL_MARKDOWN_REQUEST and SKILL_MARKDOWN_STATE to absolute paths');
  return { phase: args[0] as typeof phases[number], request, state, reply: process.env.SKILL_MARKDOWN_REPLY };
}

async function stateBoundary(state: string, roots: string[]) {
  const info = await lstat(state);
  if (!info.isDirectory() || info.isSymbolicLink() || await realpath(state) !== state)
    throw new Error('Use a real private state directory');
  for (const root of roots) {
    const part = relative(await realpath(root), state);
    if (part !== '..' && !part.startsWith('..' + sep) && !isAbsolute(part))
      throw new Error('Keep workflow state outside Markdown roots');
  }
}

export async function runMarkdown(args = process.argv.slice(2)) {
  if (args.includes('--help')) {
    process.stdout.write('Usage: mise run markdown:<phase>\nSet SKILL_MARKDOWN_REQUEST, SKILL_MARKDOWN_STATE and, for resume, SKILL_MARKDOWN_REPLY.\n'
      + 'Example: mise run markdown:review-request\nExit 0: step passed; 1: failed; 2: bad input; 3: model review needed.\n');
    return;
  }
  let storage;
  try {
    const selected = options(args);
    const request = requestSchema.parse(JSON.parse((await bound(selected.request)).raw.toString()));
    await stateBoundary(selected.state, request.roots);
    storage = await openStorage(selected.state);
    const reply = selected.reply ? JSON.parse((await bound(selected.reply)).raw.toString()) : undefined;
    const result = await runPhase(markdownWorkflows(storage), selected.phase, request, reply);
    process.stdout.write(JSON.stringify({ ...result, questions,
      stage_questions: selected.phase in stages ? stages[selected.phase as keyof typeof stages] : [], execution_acceptance: 'pending',
      limit: 'Cooperative checks and model review. Required human and whole-goal acceptance remain separate.' }) + '\n');
    process.exitCode = result.status === 'success' ? 0 : result.status === 'suspended' ? 3 : 1;
  } catch (error) {
    process.stderr.write((error instanceof Error ? error.message : String(error)) + '\n');
    process.exitCode = 2;
  } finally { await storage?.close(); }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await runMarkdown();
