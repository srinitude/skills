import { performance } from 'node:perf_hooks';

import type { EvalDefinition, TriggerCases } from './schema.js';
import type { CompletionTransport, TriggerRecord } from './types.js';

async function runTrigger(
  definition: EvalDefinition,
  transport: CompletionTransport,
  test: TriggerCases['cases'][number],
  replica: number,
): Promise<TriggerRecord> {
  const started = performance.now();
  if (!transport.classifyTrigger) {
    return {
      duration_ms: performance.now() - started,
      expected: test.should_trigger,
      id: test.id,
      replica,
      status: 'BLOCKED',
    };
  }
  try {
    const response = await transport.classifyTrigger({
      replica,
      skill: definition.manifest.skill,
      test,
    });
    return {
      duration_ms: performance.now() - started,
      expected: test.should_trigger,
      id: test.id,
      replica,
      status: response.triggered === test.should_trigger ? 'PASS' : 'FAIL',
      triggered: response.triggered,
    };
  } catch {
    return {
      duration_ms: performance.now() - started,
      expected: test.should_trigger,
      id: test.id,
      replica,
      status: 'BLOCKED',
    };
  }
}

export async function runTriggers(
  definition: EvalDefinition,
  transport: CompletionTransport,
): Promise<TriggerRecord[]> {
  const records: TriggerRecord[] = [];
  for (const test of definition.triggers.cases) {
    for (let replica = 1; replica <= definition.manifest.repetitions; replica += 1) {
      records.push(await runTrigger(definition, transport, test, replica));
    }
  }
  return records;
}
