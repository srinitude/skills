import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { FixtureTransport } from './fixture-transport.js';
import { loadEvalDefinition } from './schema.js';
import { percentile, runSkillBenchmark } from './speed.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));

test('computes nearest-rank percentiles', () => {
  expect(percentile([1, 2, 3, 4, 5], 0.5)).toBe(3);
  expect(percentile([1, 2, 3, 4, 5], 0.95)).toBe(5);
});

test('benchmarks cold, warm, case, and full-run fixture speed', async () => {
  const definition = await loadEvalDefinition(root, 'starting-point');
  const report = await runSkillBenchmark(
    root,
    'starting-point',
    new FixtureTransport(),
    1000,
  );

  expect(report).toMatchObject({
    samples: 1000,
    skill: 'starting-point',
    status: 'PASS',
    transport: 'fixture',
  });
  expect(report.cold_start_ms).toBeGreaterThanOrEqual(0);
  expect(report.discovery_ms).toBeGreaterThanOrEqual(0);
  expect(report.full_load_ms).toBeGreaterThanOrEqual(0);
  expect(report.warm_start_p50_ms).toBeLessThanOrEqual(report.warm_start_p95_ms);
  expect(report.case_p95_ms).toBeLessThanOrEqual(
    definition.budgets.fixture.case_p95_ms_max,
  );
  expect(report.full_run_ms).toBeLessThanOrEqual(
    definition.budgets.fixture.full_run_ms_max,
  );
});
