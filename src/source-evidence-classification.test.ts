import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { validateSkill } from './skill-validation.js';

const root = process.cwd();
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

async function copySkillFixture(name: string): Promise<string> {
  const fixture = await mkdtemp(join(tmpdir(), 'source-kind-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await mkdir(join(fixture, 'evidence', 'ports'), { recursive: true });
  await cp(join(root, 'skills', name), join(fixture, 'skills', name), {
    recursive: true,
  });
  await cp(
    join(root, 'evidence', 'ports', name),
    join(fixture, 'evidence', 'ports', name),
    { recursive: true },
  );
  return fixture;
}

function manifestPath(fixture: string, name: string): string {
  return join(fixture, 'evidence', 'ports', name, 'source-manifest.json');
}

test('LOGIC-004A labels mixed archived and baseline evidence explicitly', async () => {
  const path = manifestPath(root, 'visual-design-system-extractor');
  const manifest = JSON.parse(await readFile(path, 'utf8'));
  const kinds = new Set(
    manifest.files.map((entry: { location_kind: string }) => entry.location_kind),
  );

  expect(manifest.source_kind).toBe('hybrid_archived_and_repository_baseline');
  expect(kinds).toEqual(new Set(['evidence', 'repository']));
  expect((await validateSkill(root, manifest.skill)).status).toBe('PASS');
});

test('LOGIC-004B rejects a hybrid label without both evidence classes', async () => {
  const fixture = await copySkillFixture('timebox');
  const path = manifestPath(fixture, 'timebox');
  const manifest = JSON.parse(await readFile(path, 'utf8'));
  manifest.source_kind = 'hybrid_archived_and_repository_baseline';
  await writeFile(path, JSON.stringify(manifest));

  const report = await validateSkill(fixture, 'timebox');

  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/hybrid.*evidence.*repository/i);
});

test('LOGIC-004C rejects an archive-backed repository baseline label', async () => {
  const fixture = await copySkillFixture('starting-point');
  const path = manifestPath(fixture, 'starting-point');
  const manifest = JSON.parse(await readFile(path, 'utf8'));
  manifest.source_kind = 'repository_baseline';
  await writeFile(path, JSON.stringify(manifest));

  const report = await validateSkill(fixture, 'starting-point');

  expect(report.status).toBe('FAIL');
  expect(report.errors).toContain(
    'repository baseline evidence must use repository locations only',
  );
});
