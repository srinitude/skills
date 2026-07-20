import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { validateSkill } from './skill-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

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
