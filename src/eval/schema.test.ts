import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import {
  casesSchema,
  evalCaseSchema,
  evalManifestSchema,
  loadEvalDefinition,
} from './schema.js';

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

test('loads the complete reify eval definition', async () => {
  const definition = await loadEvalDefinition(root, 'reify');

  expect(definition.manifest.test_classes).toEqual(requiredClasses);
  expect(definition.cases.cases).toHaveLength(5);
  expect(new Set(definition.cases.cases.map((entry) => entry.source_id))).toHaveLength(5);
  expect(definition.triggers.cases.some((entry) => entry.should_trigger)).toBe(true);
  expect(definition.triggers.cases.some((entry) => !entry.should_trigger)).toBe(true);
});

test.each(['would-agents-actually', 'would-humans-actually'])(
  'loads the complete %s eval definition',
  async (name) => {
    const definition = await loadEvalDefinition(root, name);

    expect(definition.manifest.test_classes).toEqual(requiredClasses);
    expect(definition.cases.cases).toHaveLength(8);
    expect(new Set(definition.cases.cases.map((entry) => entry.source_id))).toHaveLength(8);
    expect(definition.triggers.cases.some((entry) => entry.should_trigger)).toBe(true);
    expect(definition.triggers.cases.some((entry) => !entry.should_trigger)).toBe(true);
  },
);

test('loads prime-vector manifest extensions without losing required classes', async () => {
  const definition = await loadEvalDefinition(root, 'prime-vector');

  expect(definition.manifest.test_classes).toEqual([
    ...requiredClasses,
    'ordered_bindings',
    'authorized_loss',
    'logical_consistency',
    'video_learning_coverage',
  ]);
  expect(definition.manifest.public_version).toBe('0.2.4');
  expect(definition.manifest.centrality_mapping).toBe('centrality-mapping.json');
  expect(definition.manifest.video_learning_map).toBe('video-learning-map.json');
  expect(definition.manifest.video_second_map).toBe('video-second-map.json');
});

test('accepts reordered required test classes and rejects omissions', () => {
  const manifest = {
    case_source: 'cases.json',
    conditions: ['with_skill', 'without_skill'],
    contract: 'contract.md',
    repetitions: 2,
    rubric: 'rubric.md',
    schema_version: 1,
    skill: 'starting-point',
    speed_budgets: 'speed-budgets.json',
    test_classes: [
      'rejection',
      'positive_activation',
      'behavior',
      'failure_handling',
      'recovery',
      'speed',
    ],
    trigger_source: 'trigger-cases.json',
  };

  expect(evalManifestSchema.parse(manifest).test_classes).toEqual(manifest.test_classes);
  expect(() =>
    evalManifestSchema.parse({
      ...manifest,
      test_classes: manifest.test_classes.filter((name) => name !== 'failure_handling'),
    }),
  ).toThrow();
});

test('rejects invalid manifest skill names and filenames', () => {
  const manifest = {
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
  };

  for (const invalid of [
    { ...manifest, case_source: 'other.json' },
    { ...manifest, trigger_source: 'other.json' },
    { ...manifest, contract: 'other.md' },
    { ...manifest, rubric: 'other.md' },
    { ...manifest, skill: 'Starting_Point' },
  ]) {
    expect(() => evalManifestSchema.parse(invalid)).toThrow();
  }
});

test('accepts portable skill case identifiers', () => {
  expect(
    evalCaseSchema.parse({
      decision: 'shape_one_object',
      group: 'collaborative_shaping',
      id: 'RFY-001',
      pressures: ['uncertainty'],
      prompt: 'I have a rough thought. Reify it with me.',
      required: ['Offer one concrete object.'],
      source_id: 'RFY-001',
      title: 'Rough thought',
      veto: ['Ask a questionnaire.'],
    }),
  ).toMatchObject({ id: 'RFY-001', source_id: 'RFY-001' });
});

test('accepts source-owned case acceptance and backlink fields', () => {
  const cases = casesSchema.parse({
    acceptance: 'Every required outcome must hold.',
    backlink: '../SKILL.md#progressive-disclosure',
    cases: [
      {
        decision: 'failed',
        group: 'failure_handling',
        id: 'TB-001',
        pressures: ['deadline'],
        prompt: 'Validation finishes late.',
        required: ['TIMEBOX_FAILED'],
        source_id: 'TB-001',
        title: 'Late validation',
        veto: ['TIMEBOX_PASS'],
      },
    ],
    decision_labels: ['failed'],
    groups: ['failure_handling'],
    schema_version: 1,
    skill: 'timebox',
  });

  expect(cases).toMatchObject({
    acceptance: 'Every required outcome must hold.',
    backlink: '../SKILL.md#progressive-disclosure',
  });
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
