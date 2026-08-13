import { expect, test } from 'vitest';

import { buildEvalReport } from './eval/report.js';
import type { CompletionTransport } from './eval/types.js';

const fixtureTransport: CompletionTransport = {
  name: 'fixture',
  async complete() {
    throw new Error('not used');
  },
};

function emptyDefinition() {
  return {
    cases: { cases: [] },
    manifest: {
      conditions: ['with_skill', 'without_skill'] as const,
      repetitions: 2,
      schema_version: 1 as const,
      skill: 'sample',
      test_classes: [
        'positive_activation',
        'rejection',
        'behavior',
        'failure_handling',
        'recovery',
        'speed',
      ],
    },
    triggers: { cases: [] },
  } as never;
}

test('LOGIC-001A empty evaluation data never passes', () => {
  const report = buildEvalReport(emptyDefinition(), fixtureTransport, [], []);
  expect(report.status).not.toBe('PASS');
});

test('LOGIC-002 fixture reports state that they do not prove effectiveness', () => {
  const report = buildEvalReport(emptyDefinition(), fixtureTransport, [], []);
  expect(report).toMatchObject({
    claim_limit: expect.stringMatching(/does not prove skill effectiveness/i),
    evidence_class: 'deterministic_contract_check',
  });
});

test('LOGIC-001B duplicate evaluation identities cannot replace missing records', () => {
  const definition = {
    cases: { cases: [{ id: 'CASE-001' }] },
    manifest: {
      conditions: ['with_skill', 'without_skill'],
      repetitions: 2,
      skill: 'sample',
      test_classes: [
        'positive_activation',
        'rejection',
        'behavior',
        'failure_handling',
        'recovery',
        'speed',
      ],
    },
    triggers: { cases: [{ id: 'TR-001' }] },
  } as never;
  const report = buildEvalReport(
    definition,
    fixtureTransport,
    duplicateRecords(),
    duplicateTriggers(),
  );
  expect(report.status).toBe('BLOCKED');
});

function duplicateRecords() {
  const record = {
    case_id: 'CASE-001',
    condition: 'with_skill',
    replica: 1,
    status: 'PASS',
  } as never;
  return [record, record, record, record];
}

function duplicateTriggers() {
  const trigger = { id: 'TR-001', replica: 1, status: 'PASS' } as never;
  return [trigger, trigger];
}
