import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const execFileAsync = promisify(execFile);
const sourceHashes = {
  'SKILL.md': 'dac89519a06ca944c0a14e2b0a46fdc1687627cb80014d55d6efbb2e31143e4c',
  'references/eval-contract.md':
    'e20a0622b583f2c9c78e6d21cf335a5dbf886c9b3a352bac1376c65f3058b97e',
  'references/eval-cases.json':
    '1245c83719bd94418654567f23f4dade91b6226eab400c9e79f2b893e695b8aa',
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
      join(root, 'evidence', 'ports', 'always-current-datetime', packetName),
    );
    expect(sha256(bytes)).toBe(sourceHashes[sourcePath as keyof typeof sourceHashes]);
  }
});

test('runs the bundled clock without a shell directory variable', async () => {
  const skill = await readFile(
    join(root, 'skills', 'always-current-datetime', 'SKILL.md'),
    'utf8',
  );

  expect(skill).toContain('python3 scripts/current_anchor.py');
  expect(skill).toContain("process runner's working directory");
  expect(skill).not.toContain('SKILL_DIR');
});

test('binds the portable files to every source file and eval case', async () => {
  const lineage = await json('skills/always-current-datetime/evals/source-lineage.json');
  const mapping = await json('skills/always-current-datetime/evals/source-mapping.json');
  expect(lineage).toMatchObject({
    native_manifest_sha256:
      'b647248569c7664ae8dcba5161a748ccfc7eafa33c5d9bb6d5378fed63c9bc86',
    native_version: '2.0.0',
    public_version: '0.1.0',
  });
  expect(lineage.source_files).toEqual(
    Object.entries(sourceHashes).map(([path, hash]) => ({ path, sha256: hash })),
  );
  expect(mapping).toMatchObject({ coverage: 1 });
  expect(mapping.source_case_ids).toEqual(
    Array.from({ length: 12 }, (_, index) => `ACDT-${String(index + 1).padStart(3, '0')}`),
  );
});

test('emits one timezone-aware anchor through the portable script', async () => {
  const script = join(
    root,
    'skills',
    'always-current-datetime',
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

test('removes the superseded skill name from every published skill body', async () => {
  const entries = await readdir(join(root, 'skills'), { withFileTypes: true });
  const files = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(root, 'skills', entry.name, 'SKILL.md'));
  const matches: string[] = [];
  const supersededName = ['always', 'current', 'date'].join('-');
  const supersededPattern = new RegExp(`${supersededName}(?!time)`, 'u');
  for (const file of files) {
    const body = await readFile(file, 'utf8');
    if (supersededPattern.test(body)) {
      matches.push(file.slice(root.length + 1));
    }
  }
  expect(matches).toEqual([]);
});
