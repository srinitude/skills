import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { evalManifestSchema, loadEvalDefinition } from './schema.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));

const requiredClasses = [
  'positive_activation',
  'rejection',
  'behavior',
  'failure_handling',
  'recovery',
  'speed',
];

test('loads the complete starting-point eval definition', async () => {
  const definition = await loadEvalDefinition(root, 'starting-point');

  expect(definition.manifest.test_classes).toEqual(requiredClasses);
  expect(definition.manifest.conditions).toEqual(['with_skill', 'without_skill']);
  expect(definition.manifest.repetitions).toBe(2);
  expect(definition.cases.cases).toHaveLength(18);
  expect(new Set(definition.cases.cases.map((entry) => entry.source_id))).toHaveLength(18);
  expect(definition.triggers.cases.some((entry) => entry.should_trigger)).toBe(true);
  expect(definition.triggers.cases.some((entry) => !entry.should_trigger)).toBe(true);
  expect(definition.budgets.fixture.cold_start_ms_max).toBeGreaterThan(0);
  expect(definition.budgets.fixture.warm_start_ms_max).toBeGreaterThan(0);
});

test('rejects unknown manifest fields', () => {
  expect(() =>
    evalManifestSchema.parse({
      case_source: 'cases.json',
      conditions: ['with_skill', 'without_skill'],
      contract: 'contract.md',
      repetitions: 2,
      rubric: 'rubric.md',
      schema_version: 1,
      skill: 'starting-point',
      speed_budgets: 'speed-budgets.json',
      test_classes: requiredClasses,
      trigger_source: 'trigger-cases.json',
      unknown: true,
    }),
  ).toThrow();
});
