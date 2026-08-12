import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { validateSkill } from './skill-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

test('validates the public always-current-datetime release and native lineage', async () => {
  const report = await validateSkill(root, 'always-current-datetime');

  expect(report).toEqual({
    caseCount: 12,
    errors: [],
    manifestSha256: 'b647248569c7664ae8dcba5161a748ccfc7eafa33c5d9bb6d5378fed63c9bc86',
    name: 'always-current-datetime',
    skillPath: join('skills', 'always-current-datetime', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.0',
  });
});

test('validates the public logic-audit release and native lineage', async () => {
  const report = await validateSkill(root, 'logic-audit');

  expect(report).toEqual({
    caseCount: 10,
    errors: [],
    manifestSha256: 'fe949512d2fd091a39606dab3e1644289032231d2ba27fc929a2efbb1fae8b18',
    name: 'logic-audit',
    skillPath: join('skills', 'logic-audit', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.1',
  });
});

test('validates the public outcome-bounded-work release and native lineage', async () => {
  const report = await validateSkill(root, 'outcome-bounded-work');

  expect(report).toEqual({
    caseCount: 10,
    errors: [],
    manifestSha256: '75d2a9fad3962caf9f1f1e05f8783522c3481e8a9c2c2d36a75899762e61a2f2',
    name: 'outcome-bounded-work',
    skillPath: join('skills', 'outcome-bounded-work', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.0',
  });
});

test('validates the public prime-vector release and source lineage', async () => {
  const report = await validateSkill(root, 'prime-vector');

  expect(report).toEqual({
    caseCount: 27,
    errors: [],
    manifestSha256: '6de25e5099680a3bc691b6b03f91258b3d04474211b50272c5e1f1ab71f7b29d',
    name: 'prime-vector',
    skillPath: join('skills', 'prime-vector', 'SKILL.md'),
    status: 'PASS',
    version: '0.2.4',
  });
});

test('validates the public starting-point release and native lineage', async () => {
  const report = await validateSkill(root, 'starting-point');

  expect(report).toEqual({
    caseCount: 18,
    errors: [],
    manifestSha256: '56de13051e3eb01974c9d819af3546efb136bf83de85e25a026901912950c156',
    name: 'starting-point',
    skillPath: join('skills', 'starting-point', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.0',
  });
});

test('validates the public reify release and native lineage', async () => {
  const report = await validateSkill(root, 'reify');

  expect(report).toEqual({
    caseCount: 5,
    errors: [],
    manifestSha256: 'd9a6be674ac2999354f07b3510733a53351b468a7f0042c3ea8c1a65ea1b7c6a',
    name: 'reify',
    skillPath: join('skills', 'reify', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.0',
  });
});

test.each([
  ['would-agents-actually', 8],
  ['would-humans-actually', 8],
])('validates the public %s release and source lineage', async (name, caseCount) => {
  const report = await validateSkill(root, name);

  expect(report).toMatchObject({
    caseCount,
    errors: [],
    name,
    skillPath: join('skills', name, 'SKILL.md'),
    status: 'PASS',
    version: '0.1.0',
  });
  expect(report.manifestSha256).toMatch(/^[a-f0-9]{64}$/);
});
