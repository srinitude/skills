import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const packetRoot = join(root, 'evidence', 'ports', 'dedupe');
const skillRoot = join(root, 'skills', 'dedupe');
const manifestHash = 'f955a6135f547637dc49fb5caa226d6c430344640b51ecb01de90e20e61896c8';
const execFileAsync = promisify(execFile);

interface PacketEntry {
  bytes: number;
  evidence_path: string;
  sha256: string;
  source_path: string;
}

interface PacketManifest {
  excluded_entries: string[];
  file_count: number;
  files: PacketEntry[];
  source_manifest_sha256: string;
}

function sha256(bytes: Buffer | string): string {
  return createHash('sha256').update(bytes).digest('hex');
}

async function json(path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(path, 'utf8')) as Record<string, unknown>;
}

test('keeps every native dedupe file byte exact in one source-bound packet', async () => {
  const manifest = JSON.parse(
    await readFile(join(packetRoot, 'manifest.json'), 'utf8'),
  ) as PacketManifest;

  expect(manifest).toMatchObject({
    excluded_entries: [],
    file_count: 36,
    source_manifest_sha256: manifestHash,
  });
  expect(manifest.files).toHaveLength(36);

  const records: string[] = [];
  for (const entry of manifest.files) {
    const bytes = await readFile(join(packetRoot, entry.evidence_path));
    expect(bytes).toHaveLength(entry.bytes);
    expect(sha256(bytes)).toBe(entry.sha256);
    records.push(`${entry.source_path}\0${entry.sha256}\n`);
  }
  expect(sha256(records.join(''))).toBe(manifestHash);
});

test('maps every native file, nonblank line, and case without a drop', async () => {
  const manifest = (await json(
    join(packetRoot, 'manifest.json'),
  )) as unknown as PacketManifest;
  const lineage = await json(join(skillRoot, 'evals', 'source-lineage.json'));
  const mapping = await json(join(skillRoot, 'evals', 'source-mapping.json'));
  const cases = await json(join(skillRoot, 'evals', 'cases.json'));
  const sourceIds = Array.from(
    { length: 8 },
    (_, index) => `DND-${String(index + 1).padStart(3, '0')}`,
  );

  expect(lineage).toMatchObject({
    native_manifest_sha256: manifestHash,
    native_version: '1.0.0',
    public_version: '0.1.0',
    schema_version: 1,
    source_case_ids: sourceIds,
    source_files: manifest.files.map(({ sha256: digest, source_path: path }) => ({
      path,
      sha256: digest,
    })),
  });

  const publicFiles = lineage.public_files as Array<{
    path: string;
    source_paths: string[];
  }>;
  expect(publicFiles.length).toBeGreaterThanOrEqual(36);
  expect(publicFiles.every((entry) => entry.source_paths.length > 0)).toBe(true);
  await Promise.all(publicFiles.map((entry) => access(join(skillRoot, entry.path))));

  const entries = mapping.entries as Array<Record<string, unknown>>;
  const expectedLines = [] as Array<Record<string, unknown>>;
  for (const file of manifest.files) {
    const source = await readFile(join(packetRoot, file.evidence_path), 'utf8');
    source.split('\n').forEach((text, index) => {
      if (text.trim()) {
        expectedLines.push({
          source_line: index + 1,
          source_line_sha256: sha256(text),
          source_path: file.source_path,
        });
      }
    });
  }
  expect(
    entries.map(({ source_line, source_line_sha256, source_path }) => ({
      source_line,
      source_line_sha256,
      source_path,
    })),
  ).toEqual(expectedLines);
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: expectedLines.length,
    ratio: 1,
    source_nonblank_lines: expectedLines.length,
  });
  expect(entries.every((entry) => entry.action !== 'drop')).toBe(true);
  expect(entries.every((entry) => entry.review_state === 'approved')).toBe(true);
  expect(
    (cases.cases as Array<Record<string, unknown>>).map(({ source_id }) => source_id),
  ).toEqual(sourceIds);
});

test('preserves native cases and labels while exposing a safe inspector', async () => {
  const native = await json(join(packetRoot, 'native', 'evals', 'evals.json'));
  const nativeTriggers = JSON.parse(
    await readFile(join(packetRoot, 'native', 'evals', 'trigger-queries.json'), 'utf8'),
  ) as Array<Record<string, unknown>>;
  const publicCases = await json(join(skillRoot, 'evals', 'cases.json'));
  const publicTriggers = await json(join(skillRoot, 'evals', 'trigger-cases.json'));
  const nativeMapping = await json(join(skillRoot, 'evals', 'native-case-mapping.json'));
  const sourceCases = native.evals as Array<Record<string, unknown>>;
  const mappedCases = nativeMapping.cases as Array<Record<string, unknown>>;

  expect(mappedCases).toEqual(
    sourceCases.map((entry, index) => ({
      assertions: entry.assertions,
      expected_output: entry.expected_output,
      native_id: entry.id,
      prompt: entry.prompt,
      public_id: `DED-${String(index + 1).padStart(3, '0')}`,
      source_id: `DND-${String(index + 1).padStart(3, '0')}`,
    })),
  );
  expect(
    (publicCases.cases as Array<Record<string, unknown>>).map(({ prompt }) => prompt),
  ).toEqual(sourceCases.map(({ prompt }) => prompt));
  expect(
    (publicTriggers.cases as Array<Record<string, unknown>>).map(
      ({ prompt, should_trigger }) => ({ prompt, should_trigger }),
    ),
  ).toEqual(
    nativeTriggers.map(({ query, should_trigger }) => ({
      prompt: String(query).replace('Hermes skills', 'agent skills'),
      should_trigger,
    })),
  );

  const script = join(skillRoot, 'scripts', 'dedupe.py');
  const request = join(skillRoot, 'examples', 'list-request.json');
  const result = await execFileAsync('python3', [script, 'inspect', '--request', request], {
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  expect(JSON.parse(result.stdout)).toMatchObject({
    adapter: 'list',
    canonical_count: 3,
    canonical_indices: [0, 2, 3],
    duplicate_count: 1,
    mode: 'normalized',
    mutated: false,
    source_count: 4,
  });
});

test('removes Hermes-only metadata and does not claim an executable apply command', async () => {
  const skill = await readFile(join(skillRoot, 'SKILL.md'), 'utf8');
  expect(skill).not.toMatch(
    /created_with_hermes_commit|compatibility_reviewed_with_hermes_commit|skill_view|skill_manage/,
  );
  expect(skill).toContain('python3 scripts/dedupe.py inspect --request');
  expect(skill).toContain(
    'The bundled script does not expose an executable `apply` subcommand.',
  );
});
