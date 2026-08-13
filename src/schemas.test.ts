import { readFile, readdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Ajv } from 'ajv';
import { expect, test } from 'vitest';

import { FixtureTransport } from './eval/fixture-transport.js';
import { runEvaluation } from './eval/runner.js';
import { loadEvalDefinition } from './eval/schema.js';
import { runSkillBenchmark } from './eval/speed.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

async function schema(name: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(join(root, 'schemas', name), 'utf8')) as Record<
    string,
    unknown
  >;
}

test('eval manifest schema accepts the canonical manifest and rejects extras', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('eval-manifest.schema.json'));
  const definition = await loadEvalDefinition(root, 'starting-point');
  expect(validate(definition.manifest), ajv.errorsText(validate.errors)).toBe(true);
  expect(validate({ ...definition.manifest, unknown: true })).toBe(false);
});

test('eval manifest schema accepts every live skill manifest', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('eval-manifest.schema.json'));
  const entries = await readdir(join(root, 'skills'), { withFileTypes: true });

  for (const entry of entries.filter((candidate) => candidate.isDirectory())) {
    const path = join(root, 'skills', entry.name, 'evals', 'manifest.json');
    const manifest = JSON.parse(await readFile(path, 'utf8')) as Record<string, unknown>;
    expect(validate(manifest), `${entry.name}: ${ajv.errorsText(validate.errors)}`).toBe(
      true,
    );
  }
});

test('eval manifest schema accepts reordered required classes and rejects omissions', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('eval-manifest.schema.json'));
  const definition = await loadEvalDefinition(root, 'starting-point');
  const reordered = {
    ...definition.manifest,
    test_classes: [
      'rejection',
      'positive_activation',
      ...definition.manifest.test_classes.slice(2),
    ],
  };

  expect(validate(reordered), ajv.errorsText(validate.errors)).toBe(true);
  expect(
    validate({
      ...definition.manifest,
      test_classes: definition.manifest.test_classes.filter(
        (name) => name !== 'failure_handling',
      ),
    }),
  ).toBe(false);
});

test('eval manifest schema enforces parser-owned names and filenames', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('eval-manifest.schema.json'));
  const definition = await loadEvalDefinition(root, 'starting-point');

  for (const invalid of [
    { ...definition.manifest, case_source: 'other.json' },
    { ...definition.manifest, trigger_source: 'other.json' },
    { ...definition.manifest, contract: 'other.md' },
    { ...definition.manifest, rubric: 'other.md' },
    { ...definition.manifest, skill: 'Starting_Point' },
  ]) {
    expect(validate(invalid)).toBe(false);
  }
});

test('eval manifest schema identifies its live repository owner', async () => {
  const manifestSchema = await schema('eval-manifest.schema.json');

  expect(manifestSchema.$id).toBe(
    'https://raw.githubusercontent.com/srinitude/skills/main/schemas/eval-manifest.schema.json',
  );
});

test('eval report schema accepts a real fixture report and rejects extras', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('eval-report.schema.json'));
  const definition = await loadEvalDefinition(root, 'starting-point');
  const report = await runEvaluation(definition, new FixtureTransport());
  expect(validate(report), ajv.errorsText(validate.errors)).toBe(true);
  expect(validate({ ...report, unknown: true })).toBe(false);
});

test('benchmark schema accepts real metrics and rejects extras', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('benchmark-report.schema.json'));
  const report = await runSkillBenchmark(
    root,
    'starting-point',
    new FixtureTransport(),
    10,
  );
  expect(validate(report), ajv.errorsText(validate.errors)).toBe(true);
  expect(validate({ ...report, unknown: true })).toBe(false);
});

test('checkpoint schema requires one terminal case identity', async () => {
  const ajv = new Ajv({ allErrors: true, strict: true });
  const validate = ajv.compile(await schema('checkpoint.schema.json'));
  const valid = {
    case_id: 'SP-001',
    condition: 'with_skill',
    model: 'vendor/model',
    record_hash: 'a'.repeat(64),
    replica: 1,
    status: 'PASS',
  };
  expect(validate(valid), ajv.errorsText(validate.errors)).toBe(true);
  expect(validate({ ...valid, extra: true })).toBe(false);
});
