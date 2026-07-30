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
  'SKILL.md': 'c11d50e7a48723c89702af27e198676528c0679578c9e000aac6e5c929bd5153',
  'references/eval-contract.md':
    '4d9547ebcd41ea83187c4379b2958cc01785e43d227d606fedbe03f48a3a6e05',
  'references/eval-cases.json':
    '4341b1d29523bb349abd31d45afcfa7f245fe0ad75c62ce88e62a0694bc516d5',
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

test('binds the portable files to every source file and eval case', async () => {
  const lineage = await json('skills/always-current-date/evals/source-lineage.json');
  const mapping = await json('skills/always-current-date/evals/source-mapping.json');
  expect(lineage).toMatchObject({
    native_manifest_sha256:
      '682512a523d7e5a7e2ebf4b8a4854d1067957575c37ff29a456c8331821c773b',
    native_version: '1.0.0',
    public_version: '0.1.0',
  });
  expect(lineage.source_files).toEqual(
    Object.entries(sourceHashes).map(([path, hash]) => ({ path, sha256: hash })),
  );
  expect(mapping).toMatchObject({ coverage: 1 });
  expect(mapping.source_case_ids).toEqual(
    Array.from({ length: 10 }, (_, index) => `ACD-${String(index + 1).padStart(3, '0')}`),
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
