import { cp, mkdir, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { loadCatalog } from './catalog.js';
import { validateCopy } from './copy.js';
import { buildEvalReport } from './eval/report.js';
import type { CompletionTransport } from './eval/types.js';
import { validateRepository } from './repository-validation.js';

const root = process.cwd();
const temporary: string[] = [];

const fixtureTransport: CompletionTransport = {
  name: 'fixture',
  async complete() {
    throw new Error('not used');
  },
};

function emptyDefinition() {
  return {
    cases: {
      cases: [],
    },
    manifest: {
      conditions: ['with_skill', 'without_skill'] as const,
      repetitions: 2,
      schema_version: 1 as const,
      skill: 'sample',
      test_classes: [
        'positive_activation',
        'rejection',
        'behavior',
        'failure_handling',
        'recovery',
        'speed',
      ],
    },
    triggers: {
      cases: [],
    },
  } as never;
}

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

async function copyTimeboxFixture(fixture: string) {
  await cp(join(root, 'skills', 'timebox'), join(fixture, 'skills', 'timebox'), {
    recursive: true,
  });
  await cp(join(root, 'package.json'), join(fixture, 'package.json'));
  await cp(
    join(root, 'evidence', 'agentskills-pages.json'),
    join(fixture, 'evidence', 'agentskills-pages.json'),
  );
  await cp(
    join(root, 'evidence', 'skills-sh-pages.json'),
    join(fixture, 'evidence', 'skills-sh-pages.json'),
  );
  await mkdir(join(fixture, 'evidence', 'ports'), { recursive: true });
  await cp(
    join(root, 'evidence', 'ports', 'timebox'),
    join(fixture, 'evidence', 'ports', 'timebox'),
    { recursive: true },
  );
}

test('LOGIC-001 empty evaluation data never passes', () => {
  const report = buildEvalReport(emptyDefinition(), fixtureTransport, [], []);
  expect(report.status).not.toBe('PASS');
});

test('LOGIC-002 fixture reports state that they do not prove effectiveness', () => {
  const report = buildEvalReport(emptyDefinition(), fixtureTransport, [], []);
  expect(report).toMatchObject({
    claim_limit: expect.stringMatching(/does not prove skill effectiveness/i),
    evidence_class: 'deterministic_contract_check',
  });
});

test('LOGIC-001 duplicate evaluation identities cannot replace missing records', () => {
  const definition = {
    cases: { cases: [{ id: 'CASE-001' }] },
    manifest: {
      conditions: ['with_skill', 'without_skill'],
      repetitions: 2,
      skill: 'sample',
      test_classes: [
        'positive_activation',
        'rejection',
        'behavior',
        'failure_handling',
        'recovery',
        'speed',
      ],
    },
    triggers: { cases: [{ id: 'TR-001' }] },
  } as never;
  const record = {
    case_id: 'CASE-001',
    condition: 'with_skill',
    replica: 1,
    status: 'PASS',
  } as never;
  const trigger = { id: 'TR-001', replica: 1, status: 'PASS' } as never;
  const report = buildEvalReport(
    definition,
    fixtureTransport,
    [record, record, record, record],
    [trigger, trigger],
  );
  expect(report.status).toBe('BLOCKED');
});

test('LOGIC-003 and LOGIC-004 repository validation verifies every source claim', async () => {
  const report = await validateRepository(root);
  expect(report.status, report.errors.join('\n')).toBe('PASS');
  expect(report.skills.every((skill) => skill.errors.length === 0)).toBe(true);
});

test('LOGIC-005 copy validation rejects symlinks before packaging can omit them', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'copy-special-entry-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills', 'sample'), { recursive: true });
  await writeFile(join(fixture, 'skills', 'sample', 'SKILL.md'), '# Sample\n');
  await writeFile(join(fixture, 'outside.txt'), 'outside\n');
  await symlink(
    join(fixture, 'outside.txt'),
    join(fixture, 'skills', 'sample', 'escape.md'),
  );

  const report = await validateCopy(fixture);
  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toContain('SPECIAL_ENTRY');
});

test('LOGIC-006 repository validation rejects an unlisted public skill file', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'lineage-public-file-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await mkdir(join(fixture, 'evidence'), { recursive: true });
  await copyTimeboxFixture(fixture);
  await writeFile(join(fixture, 'skills', 'timebox', 'unlisted.txt'), 'unlisted\n');

  const report = await validateRepository(fixture);
  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/public file.*lineage|lineage.*public file/i);
});

test('LOGIC-006 repository validation rejects an unknown lineage source path', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'lineage-source-path-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await mkdir(join(fixture, 'evidence'), { recursive: true });
  await copyTimeboxFixture(fixture);
  const lineagePath = join(fixture, 'skills', 'timebox', 'evals', 'source-lineage.json');
  const lineage = JSON.parse(await readFile(lineagePath, 'utf8'));
  lineage.public_files[0].source_paths = ['missing-source.md'];
  await writeFile(lineagePath, JSON.stringify(lineage));

  const report = await validateRepository(fixture);
  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/unknown source path/i);
});

test('LOGIC-007 repository validation rejects an empty trigger set', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'empty-triggers-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills'), { recursive: true });
  await mkdir(join(fixture, 'evidence'), { recursive: true });
  await copyTimeboxFixture(fixture);
  const triggerPath = join(fixture, 'skills', 'timebox', 'evals', 'trigger-cases.json');
  const triggers = JSON.parse(await readFile(triggerPath, 'utf8'));
  triggers.cases = [];
  await writeFile(triggerPath, JSON.stringify(triggers));

  const report = await validateRepository(fixture);
  expect(report.status).toBe('FAIL');
  expect(report.errors.join('\n')).toMatch(/trigger/i);
});

test('LOGIC-008 catalog loading rejects a directory and frontmatter name mismatch', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'catalog-name-mismatch-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills', 'wrong-directory'), { recursive: true });
  await writeFile(
    join(fixture, 'skills', 'wrong-directory', 'SKILL.md'),
    [
      '---',
      'name: declared-name',
      'description: Use when testing catalog identity.',
      'metadata:',
      '  version: 0.1.0',
      '---',
      '',
    ].join('\n'),
  );

  await expect(loadCatalog(fixture)).rejects.toThrow(/does not match name/i);
});
