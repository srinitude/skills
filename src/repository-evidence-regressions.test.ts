import { cp, mkdir, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { validateRepository } from './repository-validation.js';
import { repositoryFiles } from './source-evidence-files.js';

const root = process.cwd();
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

async function copyTimeboxFixture(): Promise<string> {
  const fixture = await mkdtemp(join(tmpdir(), 'lineage-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await mkdir(join(fixture, 'evidence'), { recursive: true });
  await cp(join(root, 'skills', 'timebox'), join(fixture, 'skills', 'timebox'), {
    recursive: true,
  });
  await cp(join(root, 'package.json'), join(fixture, 'package.json'));
  for (const pageSet of ['agentskills-pages.json', 'skills-sh-pages.json']) {
    await cp(join(root, 'evidence', pageSet), join(fixture, 'evidence', pageSet));
  }
  await mkdir(join(fixture, 'evidence', 'ports'), { recursive: true });
  await cp(
    join(root, 'evidence', 'ports', 'timebox'),
    join(fixture, 'evidence', 'ports', 'timebox'),
    { recursive: true },
  );
  return fixture;
}

test('LOGIC-003 and LOGIC-004 repository validation verifies every source claim', async () => {
  const report = await validateRepository(root);
  expect(report.status, report.errors.join('\n')).toBe('PASS');
  expect(report.skills.every((skill) => skill.errors.length === 0)).toBe(true);
});

test('LOGIC-006A repository validation rejects an unlisted public skill file', async () => {
  const fixture = await copyTimeboxFixture();
  await writeFile(join(fixture, 'skills', 'timebox', 'unlisted.txt'), 'unlisted\n');

  const report = await validateRepository(fixture);

  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/public file.*lineage|lineage.*public file/i);
});

test('source inventory excludes installed runtime entries but rejects owned links', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'source-inventory-'));
  temporary.push(fixture);
  await writeFile(join(fixture, 'SKILL.md'), '# Owned source\n');
  for (const folder of ['node_modules', '.mise', '.artifacts', '__pycache__']) {
    await mkdir(join(fixture, folder));
    await symlink(join(fixture, 'SKILL.md'), join(fixture, folder, 'runtime-link'));
    await writeFile(join(fixture, folder, 'generated.json'), '{}\n');
  }
  expect(await repositoryFiles(fixture)).toEqual(['SKILL.md']);
  await symlink(join(fixture, 'SKILL.md'), join(fixture, 'owned-link'));
  await expect(repositoryFiles(fixture)).rejects.toThrow(/unsupported entry/);
});

test('LOGIC-006B repository validation rejects an unknown lineage source path', async () => {
  const fixture = await copyTimeboxFixture();
  const lineagePath = join(fixture, 'skills', 'timebox', 'evals', 'source-lineage.json');
  const lineage = JSON.parse(await readFile(lineagePath, 'utf8'));
  lineage.public_files[0].source_paths = ['missing-source.md'];
  await writeFile(lineagePath, JSON.stringify(lineage));

  const report = await validateRepository(fixture);

  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/unknown source path/i);
});

test('LOGIC-007 repository validation rejects an empty trigger set', async () => {
  const fixture = await copyTimeboxFixture();
  const triggerPath = join(fixture, 'skills', 'timebox', 'evals', 'trigger-cases.json');
  const triggers = JSON.parse(await readFile(triggerPath, 'utf8'));
  triggers.cases = [];
  await writeFile(triggerPath, JSON.stringify(triggers));

  const report = await validateRepository(fixture);

  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/trigger/i);
});
