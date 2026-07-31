import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { validateSkill } from './skill-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

test('validates the public always-current-date release and native lineage', async () => {
  const report = await validateSkill(root, 'always-current-date');

  expect(report).toEqual({
    caseCount: 11,
    errors: [],
    manifestSha256: '02a7d6cbd55194531fadde08495681fcb5f338034c19294df17424ea6b69d4c4',
    name: 'always-current-date',
    skillPath: join('skills', 'always-current-date', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.1',
  });
});

test('validates the public logic-audit release and native lineage', async () => {
  const report = await validateSkill(root, 'logic-audit');

  expect(report).toEqual({
    caseCount: 10,
    errors: [],
    manifestSha256: 'f0a292579948abd9c7aefb18c18124d207fb19d7c4a94cc971470ce1cfb93384',
    name: 'logic-audit',
    skillPath: join('skills', 'logic-audit', 'SKILL.md'),
    status: 'PASS',
    version: '0.1.0',
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
    version: '0.2.3',
  });
});

test('validates the public starting-point release and native lineage', async () => {
  const report = await validateSkill(root, 'starting-point');

  expect(report).toEqual({
    caseCount: 18,
    errors: [],
    manifestSha256: 'ef10e9c27dec7b9cb594b1bdd7f7a3bdec50caaeb663a21016d8cc483f8cc5f0',
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
