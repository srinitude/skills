import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { FixtureTransport } from './fixture-transport.js';
import {
  RetryableTransportError,
  runEvaluation,
  type CompletionRequest,
  type CompletionTransport,
} from './runner.js';
import { loadEvalDefinition } from './schema.js';
import type { TriggerRequest } from './types.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));

class FailOnceTransport implements CompletionTransport {
  readonly name = 'fixture';
  private failed = false;
  private readonly fixture = new FixtureTransport();

  async complete(request: CompletionRequest) {
    if (!this.failed && request.case.id === 'SP-001') {
      this.failed = true;
      throw new RetryableTransportError('fixture interruption');
    }
    return this.fixture.complete(request);
  }

  classifyTrigger(request: TriggerRequest) {
    return this.fixture.classifyTrigger(request);
  }
}

class BlockOneTransport implements CompletionTransport {
  readonly name = 'fixture';
  private readonly fixture = new FixtureTransport();

  async complete(request: CompletionRequest) {
    if (request.case.id === 'SP-001') throw new Error('fixture blocked');
    return this.fixture.complete(request);
  }

  classifyTrigger(request: TriggerRequest) {
    return this.fixture.classifyTrigger(request);
  }
}

test('runs paired cases, trigger checks, and both judge orders', async () => {
  const definition = await loadEvalDefinition(root, 'starting-point');
  const report = await runEvaluation(definition, new FixtureTransport());

  expect(report.status).toBe('PASS');
  expect(report.records).toHaveLength(72);
  expect(report.trigger_records).toHaveLength(20);
  expect(new Set(report.records.map((record) => record.case_id))).toHaveLength(18);
  expect(new Set(report.records.map((record) => record.condition))).toEqual(
    new Set(['with_skill', 'without_skill']),
  );
  expect(new Set(report.records.map((record) => record.replica))).toEqual(new Set([1, 2]));
  expect(
    report.records
      .filter((record) => record.condition === 'with_skill')
      .every((record) => record.status === 'PASS'),
  ).toBe(true);
  expect(report.judge_packets.map((packet) => packet.order)).toEqual([
    'forward',
    'reverse',
  ]);
  expect(report.judge_packets[0]?.record_ids).toHaveLength(36);
  expect(report.judge_packets[1]?.record_ids).toEqual(
    [...(report.judge_packets[0]?.record_ids ?? [])].reverse(),
  );
});

test('retries one declared transient error and records recovery', async () => {
  const definition = await loadEvalDefinition(root, 'starting-point');
  const report = await runEvaluation(definition, new FailOnceTransport());

  expect(report.status).toBe('PASS');
  expect(report.records.some((record) => record.retry_count === 1)).toBe(true);
});

test('keeps terminal records and blocks the suite after an unrecovered error', async () => {
  const definition = await loadEvalDefinition(root, 'starting-point');
  const report = await runEvaluation(definition, new BlockOneTransport());

  expect(report.status).toBe('BLOCKED');
  expect(report.records).toHaveLength(72);
  expect(
    report.records
      .filter((record) => record.case_id === 'SP-001')
      .every((record) => record.status === 'BLOCKED'),
  ).toBe(true);
});
