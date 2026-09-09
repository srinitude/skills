import assert from 'node:assert/strict';
import test from 'node:test';
import { z } from 'zod';

process.env.MASTRA_TELEMETRY_DISABLED = '1';
const { createStep, createWorkflow } = await import('@mastra/core/workflows');
const input = z.object({ text: z.string() });

function countStep(id: string) {
  return createStep({
    id, inputSchema: input, outputSchema: z.number(),
    execute: async ({ inputData }) => inputData.text.length,
  });
}

test('native default branches select all true conditions', async () => {
  const workflow = createWorkflow({
    id: 'branch-all-true', inputSchema: input,
    outputSchema: z.object({ first: z.number(), second: z.number() }),
  }).branch([
    [async () => true, countStep('first')],
    [async () => true, countStep('second')],
  ]).commit();
  const result = await (await workflow.createRun()).start({ inputData: { text: 'abc' } });
  assert.equal(result.status, 'success');
  if (result.status === 'success') assert.deepEqual(result.result, { first: 3, second: 3 });
});

test('no match and a predicate error do not provide a failing acceptance gate', async () => {
  const workflow = createWorkflow({
    id: 'branch-no-match', inputSchema: input, outputSchema: z.object({}),
  }).branch([
    [async () => false, countStep('not-selected')],
    [async () => { throw new Error('predicate rejection probe'); }, countStep('predicate-error')],
  ]).commit();
  const result = await (await workflow.createRun()).start({ inputData: { text: 'abc' } });
  assert.equal(result.status, 'success');
  if (result.status === 'success') assert.deepEqual(result.result, {});
});

test('a failing finish callback cannot reject the successful domain result', async () => {
  let observed = 0;
  const workflow = createWorkflow({
    id: 'finish-callback', inputSchema: input, outputSchema: z.number(),
    options: { onFinish: () => { observed += 1; throw new Error('callback rejection probe'); } },
  }).then(countStep('count')).commit();
  const result = await (await workflow.createRun()).start({ inputData: { text: 'abc' } });
  assert.equal(result.status, 'success');
  assert.equal(observed, 1);
  if (result.status === 'success') assert.equal(result.result, 3);
});

test('an explicit failing step blocks later work even when its error callback fails', async () => {
  let reached = false;
  let observed = 0;
  const workflow = createWorkflow({
    id: 'failing-step', inputSchema: input, outputSchema: z.number(),
    options: { onError: () => { observed += 1; throw new Error('error callback probe'); } },
  }).then(createStep({
    id: 'reject', inputSchema: input, outputSchema: input,
    execute: async () => { throw new Error('explicit gate rejection'); },
  })).then(createStep({
    id: 'protected', inputSchema: input, outputSchema: z.number(),
    execute: async () => { reached = true; return 1; },
  })).commit();
  const result = await (await workflow.createRun()).start({ inputData: { text: 'abc' } });
  assert.equal(result.status, 'failed');
  assert.equal(observed, 1);
  assert.equal(reached, false);
});

test('invalid runtime input is rejected before executing a step', async () => {
  let reached = false;
  const workflow = createWorkflow({
    id: 'input-schema', inputSchema: input, outputSchema: z.number(),
  }).then(createStep({
    id: 'protected', inputSchema: input, outputSchema: z.number(),
    execute: async () => { reached = true; return 1; },
  })).commit();
  const run = await workflow.createRun();
  await assert.rejects(() => run.start({ inputData: JSON.parse('{"text":42}') }));
  assert.equal(reached, false);
});
