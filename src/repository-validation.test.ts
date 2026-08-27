import { rm } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

import { createVersionFixture } from './repository-validation-fixture.js';
import { validateRepository } from './repository-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const expectedSkills = [
  ['always-current-datetime', '0.1.0'],
  ['dedupe', '0.1.0'],
  ['dtcg-tokens', '0.2.2'],
  ['goal-prompt', '0.1.0'],
  ['logic-audit', '0.1.1'],
  ['meaning-preserving-rewrite', '0.1.0'],
  ['mobile-first-website-design', '0.1.0'],
  ['outcome-bounded-work', '0.1.0'],
  ['prompt-enhancer', '0.1.0'],
  ['reify', '0.1.0'],
  ['simplify-skill', '0.1.0'],
  ['skill-factory', '0.1.0'],
  ['starting-point', '0.1.0'],
  ['timebox', '0.1.1'],
  ['visual-design-system-extractor', '0.2.1'],
  ['would-agents-actually', '0.1.0'],
  ['would-humans-actually', '0.1.0'],
] as const;
const fixtures: string[] = [];

afterEach(async () => {
  await Promise.all(
    fixtures.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('validates every skill and all frozen specification pages', async () => {
  const report = await validateRepository(root);

  expect(report).toMatchObject({
    errors: [],
    skillCount: 17,
    sourcePageCount: 13,
    status: 'PASS',
    version: '0.1.0',
  });
  expect(report.skills).toEqual(
    expectedSkills.map(([name, version]) =>
      expect.objectContaining({ name, status: 'PASS', version }),
    ),
  );
});

test('validates package and skill versions independently', async () => {
  const fixture = await createVersionFixture(root);
  fixtures.push(fixture);

  const report = await validateRepository(fixture);

  expect(report).toMatchObject({
    errors: [],
    skillCount: 2,
    status: 'PASS',
    version: '9.9.9',
  });
  expect(report.skills.map(({ name, version }) => ({ name, version }))).toEqual([
    { name: 'independent-skill', version: '7.4.2' },
    { name: 'starting-point', version: '0.1.0' },
  ]);
});
