import { expect, test } from 'vitest';
import { derivationSchema } from './variant-lineage.js';

const hash = 'a'.repeat(64);
const record = {
  schema_version: 1,
  source: {
    identity: 'skill:source',
    scope: 'user',
    version: '0.1.0',
    digest: hash,
    baseline: { [hash]: hash },
  },
  target_scope: 'project',
  target_project: 'repo:atlas',
  adaptations: ['Bind the input directory to the project configuration.'],
  requirements: ['Read-only file inventory.'],
  compatibility: 'Python and UTF-8 source files.',
  plan_digest: hash,
  candidate_digest: hash,
  target_baseline: { 'SKILL.md': hash },
};

test('accepts derivation with both scopes and immutable source evidence', () => {
  expect(derivationSchema.parse(record)).toEqual(record);
});

test('rejects conflicting scope lineage and missing project identity', () => {
  expect(() => derivationSchema.parse({ ...record, target_scope: 'user' })).toThrow();
  expect(() => derivationSchema.parse({ ...record, target_project: null })).toThrow();
  expect(() =>
    derivationSchema.parse({ ...record, source: { ...record.source, digest: 'latest' } }),
  ).toThrow();
});
