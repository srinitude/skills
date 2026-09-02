import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { validateCopy } from './copy.js';

const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('passes the current public repository copy', async () => {
  const root = process.cwd();
  const report = await validateCopy(root);
  expect(report.status, report.findings.map((finding) => finding.message).join('\n')).toBe(
    'PASS',
  );
  expect(report.inspected_files).toBeGreaterThan(10);
  expect(report.skill_files).toEqual([
    'skills/always-current-datetime/SKILL.md',
    'skills/by-design/SKILL.md',
    'skills/dedupe/SKILL.md',
    'skills/design-like-im-5/SKILL.md',
    'skills/dtcg-tokens/SKILL.md',
    'skills/figma-code-connect-design-system/SKILL.md',
    'skills/goal-prompt/SKILL.md',
    'skills/logic-audit/SKILL.md',
    'skills/meaning-preserving-rewrite/SKILL.md',
    'skills/mobile-first-website-design/SKILL.md',
    'skills/only-one-interpretation/SKILL.md',
    'skills/outcome-bounded-work/SKILL.md',
    'skills/prompt-enhancer/SKILL.md',
    'skills/reify/SKILL.md',
    'skills/simplify-skill/SKILL.md',
    'skills/skill-factory/SKILL.md',
    'skills/starting-point/SKILL.md',
    'skills/timebox/SKILL.md',
    'skills/tool-call-configuration-for/SKILL.md',
    'skills/visual-design-system-extractor/SKILL.md',
    'skills/would-agents-actually/SKILL.md',
    'skills/would-humans-actually/SKILL.md',
  ]);
}, 30_000);

test('reports banned wording and duplicate skill locations', async () => {
  const root = await mkdtemp(join(tmpdir(), 'copy-gate-'));
  temporary.push(root);
  await writeFile(join(root, 'README.md'), 'We leverage this route.\n', 'utf8');
  await writeFile(join(root, 'SKILL.md'), 'copied body\n', 'utf8');

  const report = await validateCopy(root);
  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toEqual(
    expect.arrayContaining(['BANNED_TERM', 'DUPLICATE_SKILL_LOCATION']),
  );
});

test('does not style-check byte-exact frozen source evidence', async () => {
  const root = await mkdtemp(join(tmpdir(), 'copy-evidence-gate-'));
  temporary.push(root);
  const evidence = join(root, 'evidence', 'ports', 'sample');
  await mkdir(evidence, { recursive: true });
  await writeFile(
    join(evidence, 'SKILL.native.md'),
    'A beginner can leverage this source.\n',
  );

  const report = await validateCopy(root);

  expect(report).toMatchObject({ findings: [], inspected_files: 0, status: 'PASS' });
});

test('ignores repository-local execution artifacts', async () => {
  const root = await mkdtemp(join(tmpdir(), 'copy-local-artifacts-'));
  temporary.push(root);
  const packet = join(root, '.hermes', 'reports', 'candidate');
  await mkdir(packet, { recursive: true });
  await writeFile(join(packet, 'SKILL.md'), 'frozen candidate\n');

  const report = await validateCopy(root);

  expect(report).toMatchObject({ findings: [], inspected_files: 0, status: 'PASS' });
});

test('allows exact client names only in machine-readable source provenance', async () => {
  const root = await mkdtemp(join(tmpdir(), 'copy-provenance-gate-'));
  temporary.push(root);
  const provenance = join(root, 'skills', 'sample', 'evals');
  await mkdir(provenance, { recursive: true });
  await writeFile(
    join(provenance, 'source-lineage.json'),
    JSON.stringify({ source_path: 'references/hermes-docs-inventory.md' }),
  );

  const report = await validateCopy(root);

  expect(report).toMatchObject({ findings: [], inspected_files: 1, status: 'PASS' });
});

test('allows client names in the source-shape classification corpus', async () => {
  const root = await mkdtemp(join(tmpdir(), 'copy-source-corpus-'));
  temporary.push(root);
  const assets = join(root, 'skills', 'sample', 'assets');
  await mkdir(assets, { recursive: true });
  await writeFile(
    join(assets, 'source-shape-corpus.json'),
    JSON.stringify({ clients: [{ id: 'hermes-agent' }] }),
  );

  const report = await validateCopy(root);

  expect(report).toMatchObject({ findings: [], inspected_files: 1, status: 'PASS' });
});
