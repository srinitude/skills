import { cp, mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

import { validateRepository } from './repository-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('fails when the frozen skills.sh documentation set is incomplete', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'skills-docs-evidence-'));
  temporary.push(fixture);
  await copyFixtureInputs(fixture);
  await writeFixtureInputs(fixture);

  const report = await validateRepository(fixture);

  expect(report.status).toBe('FAIL');
  expect(report.errors).toContain(
    'missing skills.sh documentation page: https://www.skills.sh/docs',
  );
});

async function copyFixtureInputs(fixture: string): Promise<void> {
  await mkdir(join(fixture, 'evidence', 'ports'), { recursive: true });
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await cp(
    join(root, 'evidence', 'agentskills-pages.json'),
    join(fixture, 'evidence', 'agentskills-pages.json'),
  );
  await cp(
    join(root, 'skills', 'starting-point'),
    join(fixture, 'skills', 'starting-point'),
    {
      recursive: true,
    },
  );
  await cp(
    join(root, 'evidence', 'ports', 'starting-point'),
    join(fixture, 'evidence', 'ports', 'starting-point'),
    { recursive: true },
  );
}

async function writeFixtureInputs(fixture: string): Promise<void> {
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
}
