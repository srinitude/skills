import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const execFileAsync = promisify(execFile);
const sourceHashes = {
  'SKILL.md': '7dd1bcbb16f862f426214b10b05e192413d6b7fcac3a9dced7ef272b25254204',
  'references/eval-contract.md':
    'efd3b5e05e68846e229bff376c71bf0081e831984bba1f199d7dc9578da46aa3',
  'references/eval-cases.json':
    '613c3c83e67f922dae4d8ed21bdd0055065cbbe42d98910b341272186866e20b',
  'scripts/current_anchor.py':
    'dc2e2ff4edc302ed26b2b194ab6db31c5a6badf2223f42efd2d9ef088819b68f',
};
const packetFiles = {
  'SKILL.md': 'SKILL.native.md',
  'references/eval-cases.json': 'eval-cases.native.json',
  'references/eval-contract.md': 'eval-contract.native.md',
  'scripts/current_anchor.py': 'current-anchor.native.py',
};

function sha256(bytes: Buffer): string {
  return createHash('sha256').update(bytes).digest('hex');
}

async function json(relative: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(join(root, relative), 'utf8')) as Record<
    string,
    unknown
  >;
}

test('keeps a byte-exact packet of every native source file', async () => {
  for (const [sourcePath, packetName] of Object.entries(packetFiles)) {
    const bytes = await readFile(
      join(root, 'evidence', 'ports', 'always-current-date', packetName),
    );
    expect(sha256(bytes)).toBe(sourceHashes[sourcePath as keyof typeof sourceHashes]);
  }
});

test('runs the bundled clock without a shell directory variable', async () => {
  const skill = await readFile(
    join(root, 'skills', 'always-current-date', 'SKILL.md'),
    'utf8',
  );

  expect(skill).toContain('python3 scripts/current_anchor.py');
  expect(skill).toContain("process runner's working directory");
  expect(skill).not.toContain('SKILL_DIR');
});

test('binds the portable files to every source file and eval case', async () => {
  const lineage = await json('skills/always-current-date/evals/source-lineage.json');
  const mapping = await json('skills/always-current-date/evals/source-mapping.json');
  expect(lineage).toMatchObject({
    native_manifest_sha256:
      '02a7d6cbd55194531fadde08495681fcb5f338034c19294df17424ea6b69d4c4',
    native_version: '1.0.1',
    public_version: '0.1.1',
  });
  expect(lineage.source_files).toEqual(
    Object.entries(sourceHashes).map(([path, hash]) => ({ path, sha256: hash })),
  );
  expect(mapping).toMatchObject({ coverage: 1 });
  expect(mapping.source_case_ids).toEqual(
    Array.from({ length: 11 }, (_, index) => `ACD-${String(index + 1).padStart(3, '0')}`),
  );
});

test('emits one timezone-aware anchor through the portable script', async () => {
  const script = join(
    root,
    'skills',
    'always-current-date',
    'scripts',
    'current_anchor.py',
  );
  const result = await execFileAsync('python3', [script], {
    env: { ...process.env, PROFILE_TIMEZONE: 'UTC' },
  });
  const lines = result.stdout.trimEnd().split('\n');
  const payload = JSON.parse(lines[0]!) as Record<string, string>;
  expect(lines).toHaveLength(1);
  expect(payload).toMatchObject({
    source: 'profile-environment',
    timezone: 'UTC',
    utc_offset: '+00:00',
  });
});
