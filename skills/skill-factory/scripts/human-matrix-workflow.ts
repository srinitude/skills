import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { z } from 'zod';

process.env.MASTRA_TELEMETRY_DISABLED = '1';
const { createStep, createWorkflow } = await import('@mastra/core/workflows');
const root = fileURLToPath(new URL('../', import.meta.url));
const sha = z.string().regex(/^[a-f0-9]{64}$/);
const summary = z.object({
  concepts: z.number().int().positive(), roots: z.number().int().positive(),
  missing_definitions: z.number().int().nonnegative(), inventory_sha256: sha, source_sha256: sha,
  source_version: z.string(), url: z.string(), license: z.string(), scope: z.string(), attribution: z.string(),
}).strict();
const inventory = z.object({ implementation: sha, registry_sha256: sha,
  catalogs: z.record(z.string(), summary) }).strict();
const budgetNames = ['max-members', 'max-output-bytes', 'max-memory-bytes', 'max-seconds'] as const;
const budgets = z.object({ 'max-members': z.number().int().nonnegative(),
  'max-output-bytes': z.number().int().positive().max(2147483647),
  'max-memory-bytes': z.number().int().positive(),
  'max-seconds': z.number().positive().max(2147473) }).strict();
const request = z.object({ resources: z.string().min(1), concepts: z.array(z.string().min(1)).optional(),
  matrix: z.string().min(1).optional(), matrixSha256: sha.optional(),
  enumerate: z.string().min(1).optional(), budgets: budgets.optional() }).strict();
const bound = request.extend({ inventory });
const concept = z.object({
  id: z.string(), native_id: z.string(), label: z.string(), definition: z.string().nullable(),
  broader: z.array(z.string()), locator: z.string(), source_fields: z.record(z.string(), z.string()),
  definition_status: z.enum(['provided', 'not-supplied']), aliases: z.array(z.string()),
}).strict();
const enumeration = z.union([z.object({ state: z.literal('not-requested') }).strict(), z.object({
  state: z.literal('complete'), selector: z.string(), count: z.string().regex(/^\d+$/),
  members: z.array(z.record(z.string(), z.unknown())), budgets,
  metrics: z.object({ peak_traced_bytes: z.number().int().nonnegative(), tracer_bytes: z.number().int().nonnegative(),
    input_pool_bytes: z.number().int().nonnegative(), elapsed_seconds: z.number().nonnegative(),
    memory_scope: z.string(), enforcement: z.string() }).strict(),
  runtime: z.object({ python: z.string(), platform: z.string(), iterator: z.literal('itertools') }).strict(),
  scope: z.string(),
}).strict()]);
const matrixResult = inventory.extend({ matrix_sha256: sha, canonical_sha256: sha,
  matrix: z.record(z.string(), z.unknown()), concepts: z.record(z.string(), z.unknown()),
  records: z.record(z.string(), z.unknown()), spaces: z.array(z.record(z.string(), z.unknown())),
  view: z.array(z.object({ interaction: z.string(), study: z.array(z.string()), work: z.array(z.string()) }).strict()),
  coverage: z.object({ vocabulary: z.literal('complete-declared-inventories'),
    representation: z.literal('validated-records'), evidence: z.literal('not-evaluated'),
    executed_tests: z.literal('not-evaluated') }).strict(),
  enumeration, acceptance: z.literal('pending'),
}).strict();
const resultSchema = z.union([inventory.extend({ selected: z.array(concept),
  acceptance: z.literal('pending') }).strict(), matrixResult]);

function inputRequest(value: unknown) {
  const input = request.parse(value);
  if (input.concepts !== undefined ? input.matrix !== undefined || input.matrixSha256 !== undefined
    : input.matrix === undefined || input.matrixSha256 === undefined) {
    throw new Error('Supply concepts or a matrix with its digest');
  }
  if (input.enumerate !== undefined ? !input.matrix || !input.budgets : input.budgets !== undefined) {
    throw new Error('Enumeration requires a bound matrix and every explicit budget');
  }
  return input;
}

function read(operation: string, input: z.infer<typeof request>) {
  const args = ['run', '--with', 'pypdf==6.10.0', 'python', '-I', '-B', root + 'scripts/human_catalogs.py',
    operation, '--resources', input.resources];
  if (operation === 'select') args.push('--concepts', JSON.stringify(input.concepts));
  if (operation === 'matrix') args.push('--matrix', input.matrix!, '--matrix-sha256', input.matrixSha256!);
  if (operation === 'matrix' && input.enumerate) {
    args.push('--enumerate', input.enumerate);
    for (const name of budgetNames) args.push('--' + name, String(input.budgets![name]));
  }
  return JSON.parse(execFileSync('uv', args, { cwd: root, encoding: 'utf8',
    timeout: Math.max(60000, (input.budgets?.['max-seconds'] ?? 0) * 1000 + 10000),
    maxBuffer: Math.max(8 * 1024 * 1024, input.budgets?.['max-output-bytes'] ?? 0),
    stdio: ['ignore', 'pipe', 'pipe'] })) as unknown;
}

function checkedEnumeration(result: z.infer<typeof resultSchema>, input: z.infer<typeof request>) {
  if (!('enumeration' in result)) return;
  const value = result.enumeration;
  if (!input.enumerate && value.state !== 'not-requested') throw new Error('Unrequested enumeration');
  if (!input.enumerate) return;
  if (value.state !== 'complete' || value.selector !== input.enumerate
    || JSON.stringify(value.budgets) !== JSON.stringify(input.budgets)
    || BigInt(value.count) !== BigInt(value.members.length)) throw new Error('Incomplete enumeration');
  if (value.metrics.peak_traced_bytes + value.metrics.tracer_bytes > input.budgets!['max-memory-bytes']
    || value.metrics.elapsed_seconds > input.budgets!['max-seconds']
    || value.members.length > input.budgets!['max-members']) throw new Error('Enumeration budget exceeded');
}

function budgetInput(values: Record<string, string | boolean | undefined>) {
  if (!budgetNames.some(name => values[name] !== undefined)) return undefined;
  return Object.fromEntries(budgetNames.map(name => {
    const value = values[name];
    const grammar = name === 'max-seconds' ? /^\d+(?:\.\d+)?$/ : /^\d+$/;
    if (typeof value !== 'string' || !grammar.test(value)) throw new Error('Invalid or missing budget: ' + name);
    return [name, Number(value)];
  }));
}

function workflow() {
  return createWorkflow({ id: 'human-study-work-selection-v1', inputSchema: request,
    outputSchema: resultSchema, retryConfig: { attempts: 0, delay: 0 } })
    .then(createStep({ id: 'resolve-complete-inventories', inputSchema: request, outputSchema: bound,
      execute: async ({ inputData }) => ({ ...inputRequest(inputData),
        inventory: inventory.parse(read('inspect', inputRequest(inputData))) }),
    })).then(createStep({ id: 'resolve-selected-concepts', inputSchema: bound, outputSchema: resultSchema,
      execute: async ({ inputData }) => {
        const input = bound.parse(inputData);
        const { inventory: before, ...selection } = input;
        const result = resultSchema.parse(read(input.matrix ? 'matrix' : 'select', inputRequest(selection)));
        const current = inventory.parse({ implementation: result.implementation,
          registry_sha256: result.registry_sha256, catalogs: result.catalogs });
        if (JSON.stringify(current) !== JSON.stringify(before)) throw new Error('Matrix inventory changed');
        if ('selected' in result && JSON.stringify(result.selected.map(item => item.id)) !== JSON.stringify(input.concepts)) {
          throw new Error('Selected identity, order or repetition changed');
        }
        if ('matrix_sha256' in result && result.matrix_sha256 !== input.matrixSha256) throw new Error('Matrix input changed');
        checkedEnumeration(result, input);
        return resultSchema.parse(result);
      },
    })).commit();
}

function parseInput() {
  const { values, tokens } = parseArgs({ options: {
    resources: { type: 'string' }, concepts: { type: 'string' }, matrix: { type: 'string' },
    'matrix-sha256': { type: 'string' }, enumerate: { type: 'string' },
    'max-members': { type: 'string' }, 'max-output-bytes': { type: 'string' },
    'max-memory-bytes': { type: 'string' }, 'max-seconds': { type: 'string' }, help: { type: 'boolean' } },
    strict: true, tokens: true });
  if (new Set(tokens.map(token => token.kind === 'option' ? token.name : '')).size !== tokens.length) {
    throw new Error('Duplicate matrix argument');
  }
  if (values.help) {
    process.stdout.write('Usage: mise run human-matrix -- --resources <bindings.json> --concepts <JSON-array>\n' +
      'Or: mise run human-matrix -- --resources <bindings.json> --matrix <case.json> --matrix-sha256 <sha256>\n' +
      'Bind every inventory in assets/human-catalogs.json to its captured file and digest.\n' +
      'Concept lookup preserves order and repetitions. Acceptance remains pending.\n' +
      'Enumeration: --enumerate <selector> --max-members <n> --max-output-bytes <n> ' +
      '--max-memory-bytes <n> --max-seconds <n>. Every budget is required.\n' +
      'Budget counts are decimal integers; seconds may include a decimal fraction.\n' +
      'Memory counts traced Python allocations plus tracer metadata, not process RSS.\n' +
      'Exit codes: 0 for lookup, 1 for missing, changed or invalid inputs and runtime failure.\n');
    return;
  }
  return inputRequest({ resources: values.resources,
    concepts: values.concepts === undefined ? undefined : JSON.parse(values.concepts),
    matrix: values.matrix, matrixSha256: values['matrix-sha256'], enumerate: values.enumerate,
    budgets: budgetInput(values) });
}

async function main() {
  const input = parseInput();
  if (!input) return;
  const run = await workflow().createRun();
  const result = await run.start({ inputData: input });
  if (result.status === 'failed') throw new Error(result.error.message);
  if (result.status !== 'success') throw new Error('Matrix workflow ended with status: ' + result.status);
  const output = JSON.stringify(resultSchema.parse(result.result)) + '\n';
  if (input.budgets && Buffer.byteLength(output) > input.budgets['max-output-bytes']) {
    throw new Error('Enumeration output budget exceeded');
  }
  process.stdout.write(output);
}

if (import.meta.main) main().catch(error => {
  process.stderr.write(String(error) + '\n');
  process.exitCode = 1;
});
