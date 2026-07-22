import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

import { validateRepository } from './repository-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const roots: string[] = [];

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('validates every skill and all frozen specification pages', async () => {
  const report = await validateRepository(root);

  expect(report).toMatchObject({
    errors: [],
    skillCount: 2,
    sourcePageCount: 13,
    status: 'PASS',
    version: '0.1.0',
  });
  expect(report.skills).toEqual([
    expect.objectContaining({ name: 'skill-factory', status: 'PASS', version: '0.1.0' }),
    expect.objectContaining({ name: 'starting-point', status: 'PASS', version: '0.1.0' }),
  ]);
});

test('validates package and skill versions independently', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'skills-version-independence-'));
  roots.push(fixture);
  await mkdir(join(fixture, 'evidence'), { recursive: true });
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await cp(
    join(root, 'evidence', 'agentskills-pages.json'),
    join(fixture, 'evidence', 'agentskills-pages.json'),
  );
  await cp(
    join(root, 'evidence', 'skills-sh-pages.json'),
    join(fixture, 'evidence', 'skills-sh-pages.json'),
  );
  await cp(
    join(root, 'skills', 'starting-point'),
    join(fixture, 'skills', 'starting-point'),
    {
      recursive: true,
    },
  );
  await cp(
    join(root, 'skills', 'starting-point'),
    join(fixture, 'skills', 'independent-skill'),
    { recursive: true },
  );
  await writeFile(
    join(fixture, 'package.json'),
    JSON.stringify({ name: 'version-fixture', version: '9.9.9' }),
  );

  const independent = join(fixture, 'skills', 'independent-skill');
  const skill = await readFile(join(independent, 'SKILL.md'), 'utf8');
  await writeFile(
    join(independent, 'SKILL.md'),
    skill
      .replace('name: starting-point', 'name: independent-skill')
      .replace("version: '0.1.0'", "version: '7.4.2'"),
  );
  const cases = JSON.parse(
    await readFile(join(independent, 'evals', 'cases.json'), 'utf8'),
  );
  cases.skill = 'independent-skill';
  await writeFile(join(independent, 'evals', 'cases.json'), JSON.stringify(cases));
  const lineage = JSON.parse(
    await readFile(join(independent, 'evals', 'source-lineage.json'), 'utf8'),
  );
  lineage.public_version = '7.4.2';
  await writeFile(
    join(independent, 'evals', 'source-lineage.json'),
    JSON.stringify(lineage),
  );

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

test('fails when the frozen skills.sh documentation set is incomplete', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'skills-docs-evidence-'));
  roots.push(fixture);
  await mkdir(join(fixture, 'evidence'), { recursive: true });
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await cp(
    join(root, 'evidence', 'agentskills-pages.json'),
    join(fixture, 'evidence', 'agentskills-pages.json'),
  );
  await cp(
    join(root, 'skills', 'starting-point'),
    join(fixture, 'skills', 'starting-point'),
    { recursive: true },
  );
  await writeFile(
    join(fixture, 'package.json'),
    JSON.stringify({ name: 'docs-fixture', version: '0.1.0' }),
  );
  await writeFile(
    join(fixture, 'evidence', 'skills-sh-pages.json'),
    JSON.stringify({
      captured_at: '2026-07-21',
      pages: [],
      schema: 'skills-sh-pages/v1',
      source: 'https://www.skills.sh/sitemap-misc.xml',
    }),
  );

  const report = await validateRepository(fixture);

  expect(report.status).toBe('FAIL');
  expect(report.errors).toContain(
    'missing skills.sh documentation page: https://www.skills.sh/docs',
  );
});
