import assert from 'node:assert/strict';
import test from 'node:test';
import { z } from 'zod';

process.env.MASTRA_TELEMETRY_DISABLED = '1';
const { createStep, createWorkflow } = await import('@mastra/core/workflows');
const { RequestContext } = await import('@mastra/core/request-context');
const shape = z.object({ value: z.number() });

test('output declarations do not replace a domain result validator', async () => {
  const workflow = createWorkflow({
    id: 'output-schema-probe', inputSchema: shape, outputSchema: shape,
  }).then(createStep({
    id: 'wrong-output', inputSchema: shape, outputSchema: shape,
    execute: async () => JSON.parse('{"value":"wrong"}'),
  })).commit();
  const result = await (await workflow.createRun()).start({ inputData: { value: 1 } });
  assert.equal(result.status, 'success');
  if (result.status === 'success') assert.equal(shape.safeParse(result.result).success, false);
});

test('an explicit output parse fails before the downstream effect', async () => {
  let effects = 0;
  const workflow = createWorkflow({
    id: 'output-domain-gate', inputSchema: shape, outputSchema: shape,
  }).then(createStep({
    id: 'checked-output', inputSchema: shape, outputSchema: shape,
    execute: async () => shape.parse(JSON.parse('{"value":"wrong"}')),
  })).then(createStep({
    id: 'effect', inputSchema: shape, outputSchema: shape,
    execute: async ({ inputData }) => { effects += 1; return inputData; },
  })).commit();
  const result = await (await workflow.createRun()).start({ inputData: { value: 1 } });
  assert.equal(result.status, 'failed');
  assert.equal(effects, 0);
});

test('initial state and request context reject before a step', async () => {
  let effects = 0;
  const workflow = createWorkflow({
    id: 'initial-schema-probes', inputSchema: shape, outputSchema: shape,
    stateSchema: shape, requestContextSchema: shape,
  }).then(createStep({
    id: 'effect', inputSchema: shape, outputSchema: shape,
    execute: async ({ inputData }) => { effects += 1; return inputData; },
  })).commit();
  const invalid = JSON.parse('{"value":"wrong"}');
  const goodContext = new RequestContext<{ value: number }>([['value', 1]]);
  await assert.rejects(() => workflow.createRun().then(run =>
    run.start({ inputData: { value: 1 }, initialState: invalid, requestContext: goodContext })));
  await assert.rejects(() => workflow.createRun().then(run =>
    run.start({ inputData: { value: 1 }, initialState: { value: 1 },
      requestContext: new RequestContext<{ value: number }>(JSON.parse('[["value","wrong"]]')) })));
  assert.equal(effects, 0);
});

test('runtime state updates are checked at the step schema', async () => {
  let effects = 0;
  const workflow = createWorkflow({
    id: 'state-update-probe', inputSchema: shape, outputSchema: shape, stateSchema: shape,
  }).then(createStep({
    id: 'update-state', inputSchema: shape, outputSchema: shape, stateSchema: shape,
    execute: async ({ inputData, setState }) => {
      await setState(JSON.parse('{"value":"wrong"}'));
      effects += 1;
      return inputData;
    },
  })).commit();
  const result = await (await workflow.createRun()).start({
    inputData: { value: 1 }, initialState: { value: 1 },
  });
  assert.equal(result.status, 'failed');
  assert.equal(effects, 0);
});
