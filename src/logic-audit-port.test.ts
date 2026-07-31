import { createHash } from 'node:crypto';
import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const packetRoot = join(root, 'evidence', 'ports', 'logic-audit');
const skillRoot = join(root, 'skills', 'logic-audit');
const manifestHash = 'f0a292579948abd9c7aefb18c18124d207fb19d7c4a94cc971470ce1cfb93384';
const sourceHashes = {
  'SKILL.md': '2454abc677c73b8ba0fff6932a6301dedeeda36538957d0bf40fe84d74891bbb',
  'references/check-catalog.md':
    'e9a7fe8dfa4f145fb61d3e82117bf3406d5cd95fd1ee95b774b35406b8b3360f',
  'references/eval-cases.json':
    '456c3019f38b2009aba52125efb7036ead79f382ec91c10262218a16d4d82af8',
};
const packetFiles = {
  'SKILL.md': 'SKILL.native.md',
  'references/check-catalog.md': 'check-catalog.native.md',
  'references/eval-cases.json': 'eval-cases.native.json',
};
const sourceCases = [
  'direct-contradiction',
  'temporal-non-contradiction',
  'quantifier-drift',
  'necessary-sufficient-reversal',
  'missing-case',
  'component-proof-gap',
  'authority-conflict',
  'current-web-claim',
  'web-tool-failure',
  'exact-method-preservation',
];

function sha256(bytes: Buffer | string): string {
  return createHash('sha256').update(bytes).digest('hex');
}

async function json(relative: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(join(root, relative), 'utf8')) as Record<
    string,
    unknown
  >;
}

function nonblankLines(text: string): Array<{ line: number; text: string }> {
  return text
    .split('\n')
    .map((value, index) => ({ line: index + 1, text: value }))
    .filter(({ text: value }) => value.trim().length > 0);
}

function normalizeCatalog(text: string): string {
  return text
    .replace(/-{3,}/g, '---')
    .replace(/\s*\|\s*/g, '|')
    .replace(/\s+/g, ' ')
    .trim();
}

test('keeps every native source file byte exact', async () => {
  const records: string[] = [];
  for (const [sourcePath, packetName] of Object.entries(packetFiles)) {
    const bytes = await readFile(join(packetRoot, packetName));
    const digest = sourceHashes[sourcePath as keyof typeof sourceHashes];
    expect(sha256(bytes)).toBe(digest);
    records.push(`${sourcePath}\0${digest}\0${bytes.length}\n`);
  }
  expect(sha256(records.join(''))).toBe(manifestHash);
  const manifest = await json('evidence/ports/logic-audit/manifest.json');
  expect(manifest.source_manifest_sha256).toBe(manifestHash);
  expect(manifest.excluded_entries).toEqual([]);
});

test('maps every nonblank source line and native case without a drop', async () => {
  const mapping = await json('skills/logic-audit/evals/source-mapping.json');
  const entries = mapping.entries as Array<Record<string, unknown>>;
  const expected = [] as Array<Record<string, unknown>>;
  for (const [sourcePath, packetName] of Object.entries(packetFiles)) {
    const text = await readFile(join(packetRoot, packetName), 'utf8');
    for (const line of nonblankLines(text)) {
      expected.push({
        source_line: line.line,
        source_line_sha256: sha256(line.text),
        source_path: sourcePath,
      });
    }
  }
  expect(
    entries.map(({ source_line, source_line_sha256, source_path }) => ({
      source_line,
      source_line_sha256,
      source_path,
    })),
  ).toEqual(expected);
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: expected.length,
    ratio: 1,
    source_nonblank_lines: expected.length,
  });
  expect(entries.every((entry) => !('source_text' in entry))).toBe(true);
  expect(entries.every((entry) => entry.action !== 'drop')).toBe(true);
  expect(entries.every((entry) => entry.review_state === 'approved')).toBe(true);
  expect(entries.every((entry) => entry.public_target && entry.evidence_target)).toBe(true);
  expect(Object.keys(mapping.case_mapping as object)).toEqual(sourceCases);
});

test('binds every public file and native case to the packet', async () => {
  const lineage = await json('skills/logic-audit/evals/source-lineage.json');
  const lineageCases = sourceCases.map(
    (_, index) => `NLA-${String(index + 1).padStart(3, '0')}`,
  );
  expect(lineage).toMatchObject({
    native_manifest_sha256: manifestHash,
    native_version: '1.0.1',
    public_version: '0.1.0',
    source_case_ids: lineageCases,
    source_files: Object.entries(sourceHashes).map(([path, hash]) => ({
      path,
      sha256: hash,
    })),
  });
  const publicFiles = lineage.public_files as Array<{
    path: string;
    source_paths: string[];
  }>;
  expect(publicFiles.length).toBeGreaterThan(0);
  await Promise.all(publicFiles.map((entry) => access(join(skillRoot, entry.path))));
  expect(publicFiles.every((entry) => entry.source_paths.length > 0)).toBe(true);
});

test('preserves native references and portable audit behavior', async () => {
  const catalog = await readFile(join(skillRoot, 'references', 'check-catalog.md'), 'utf8');
  const nativeCatalog = await readFile(join(packetRoot, 'check-catalog.native.md'), 'utf8');
  expect(normalizeCatalog(catalog)).toBe(normalizeCatalog(nativeCatalog));
  expect(await json('skills/logic-audit/references/eval-cases.json')).toEqual(
    JSON.parse(await readFile(join(packetRoot, 'eval-cases.native.json'), 'utf8')),
  );
  const skill = await readFile(join(skillRoot, 'SKILL.md'), 'utf8');
  expect(skill).not.toMatch(
    /Hermes Agent|computer-user|tool_search|web_search|web_extract|x_search/,
  );
  expect(skill).toContain('Normalize terms');
  expect(skill.indexOf('Normalize terms')).toBeLessThan(skill.indexOf('dependency map'));
  expect(skill).toContain('search capability');
  expect(skill).toContain('source extraction capability');
  expect(skill).toContain('rendered browser capability');
});

test('preserves every native pressure case in public evaluations', async () => {
  const cases = await json('skills/logic-audit/evals/cases.json');
  const publicCases = cases.cases as Array<Record<string, unknown>>;
  const sourceIds = sourceCases.map(
    (_, index) => `NLA-${String(index + 1).padStart(3, '0')}`,
  );
  expect(publicCases.map((entry) => entry.source_id)).toEqual(sourceIds);
  expect(publicCases.map((entry) => entry.id)).toEqual(
    sourceCases.map((_, index) => `LA-${String(index + 1).padStart(3, '0')}`),
  );
  const native = JSON.parse(
    await readFile(join(packetRoot, 'eval-cases.native.json'), 'utf8'),
  ) as { cases: Array<Record<string, unknown>> };
  const mapping = await json('skills/logic-audit/evals/source-mapping.json');
  const caseMapping = mapping.case_mapping as Record<
    string,
    { lineage_source_id: string; public_id: string }
  >;
  for (const sourceCase of native.cases) {
    const mapped = caseMapping[String(sourceCase.id)]!;
    const publicCase = publicCases.find((entry) => entry.id === mapped.public_id);
    expect(publicCase).toMatchObject({
      prompt: sourceCase.input,
      required: sourceCase.expect,
      source_id: mapped.lineage_source_id,
      veto: sourceCase.forbid,
    });
  }
});
