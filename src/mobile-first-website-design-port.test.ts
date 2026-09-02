import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';
import { expect, test } from 'vitest';

import { readSkillDocument } from './skill-document.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const evidence = join(root, 'evidence', 'ports', 'mobile-first-website-design');
const skill = join(root, 'skills', 'mobile-first-website-design');
const nativeManifestSha =
  '8fcb66453d80f1454804c37770db179b83c171136dd05e1d0b541bfd3380e5c3';
const sourceCases = [
  'fail-breakpoint-order',
  'fail-capability-floor',
  'fail-flora-routing',
  'fail-performance',
  'fail-prompt-hash',
  'fail-style-in-wireframe',
  'pass-degraded',
  'pass-full',
];

interface SourceFile {
  bytes: number;
  lines: number;
  path: string;
  sha256: string;
}

interface MappingEntry {
  action: string;
  evidence_target: string;
  public_semantic_id?: string;
  public_targets: string[];
  public_text_sha256?: string;
  review_state: string;
  source_line: number;
  source_path: string;
  source_text_sha256: string;
}

function sha256(value: Buffer | string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function json<T>(path: string): Promise<T> {
  return JSON.parse(await readFile(path, 'utf8')) as T;
}

function evidencePath(sourcePath: string): string {
  return sourcePath === 'SKILL.md' ? 'native/SKILL.native.md' : `native/${sourcePath}`;
}

test('keeps an exact evidence packet of all 228 native files', async () => {
  const sourceManifestPath = join(evidence, 'freeze-manifest.json');
  const sourceManifest = await json<{
    exclusions: { generated_runtime_residue: string[]; unsafe_private: string[] };
    files: SourceFile[];
    manifest_sha256: string;
  }>(sourceManifestPath);
  expect(sourceManifest.manifest_sha256).toBe(nativeManifestSha);
  const packet = await json<{
    files: Array<{ evidence_path: string; source_path: string }>;
    source_case_ids: string[];
  }>(join(evidence, 'manifest.json'));
  expect(sourceManifest.files).toHaveLength(228);
  expect(sourceManifest.exclusions).toEqual({
    generated_runtime_residue: [],
    unsafe_private: [],
  });
  expect(packet.source_case_ids).toEqual(sourceCases);
  for (const source of sourceManifest.files) {
    const target = evidencePath(source.path);
    expect(packet.files).toContainEqual({
      evidence_path: target,
      source_path: source.path,
    });
    const bytes = await readFile(join(evidence, target));
    expect(bytes.byteLength).toBe(source.bytes);
    expect(sha256(bytes)).toBe(source.sha256);
  }
});

test('maps every native nonblank line and behavior case without loss', async () => {
  const mapping = await json<{
    case_mapping: Record<string, { lineage_source_id: string; public_id: string }>;
    coverage: Record<string, number>;
    entries: MappingEntry[];
  }>(join(skill, 'evals', 'source-mapping.json'));
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: 12029,
    ratio: 1,
    source_nonblank_lines: 12029,
  });
  expect(mapping.entries).toHaveLength(12029);
  expect(mapping.entries.every((entry) => !('source_text' in entry))).toBe(true);
  const nativeLines = new Map<string, string[]>();
  for (const entry of mapping.entries) {
    if (!nativeLines.has(entry.source_path)) {
      nativeLines.set(
        entry.source_path,
        (await readFile(join(evidence, evidencePath(entry.source_path)), 'utf8')).split(
          '\n',
        ),
      );
    }
    const sourceLine = nativeLines.get(entry.source_path)?.[entry.source_line - 1];
    expect(sourceLine?.trim().length).toBeGreaterThan(0);
    expect(sha256(sourceLine ?? '')).toBe(entry.source_text_sha256);
    expect(['keep', 'split', 'move', 'clarify']).toContain(entry.action);
    expect(entry.review_state).toBe('approved');
    expect(entry.evidence_target).toBe(evidencePath(entry.source_path));
    expect(entry.public_targets.length).toBeGreaterThan(0);
    expect(Boolean(entry.public_text_sha256 ?? entry.public_semantic_id)).toBe(true);
  }
  expect(Object.keys(mapping.case_mapping)).toEqual(sourceCases);
  sourceCases.forEach((source, index) => {
    expect(mapping.case_mapping[source]).toEqual({
      lineage_source_id: source,
      public_id: `MFWD-${String(index + 1).padStart(3, '0')}`,
    });
  });
}, 20_000);

test('binds every mapped line to its public text or portable semantic owner', async () => {
  const mapping = await json<{
    entries: MappingEntry[];
    semantic_mappings: Array<{ contains: string; id: string; target: string }>;
  }>(join(skill, 'evals', 'source-mapping.json'));
  const semanticIds = new Set(mapping.semantic_mappings.map(({ id }) => id));
  const hashes = new Map<string, Set<string>>();
  for (const entry of mapping.entries) {
    if (entry.public_semantic_id) {
      expect(semanticIds).toContain(entry.public_semantic_id);
      continue;
    }
    const target = entry.public_targets[0]!;
    if (!hashes.has(target)) {
      const lines = (await readFile(join(skill, target), 'utf8'))
        .split('\n')
        .filter((line) => line.trim().length > 0);
      hashes.set(target, new Set(lines.map(sha256)));
    }
    expect(hashes.get(target)).toContain(entry.public_text_sha256);
  }
  for (const semantic of mapping.semantic_mappings) {
    expect(await readFile(join(skill, semantic.target), 'utf8')).toContain(
      semantic.contains,
    );
  }
}, 20_000);

test('publishes 1000 normalized prompts in 201 verified shards', async () => {
  const manifest = await json<{
    count: number;
    shards: Array<{ bytes: number; count: number; path: string; sha256: string }>;
  }>(join(skill, 'assets', 'prompt-manifest.json'));
  expect(manifest.count).toBe(1000);
  expect(manifest.shards).toHaveLength(201);
  let count = 0;
  for (const shard of manifest.shards) {
    const bytes = await readFile(join(skill, shard.path));
    expect(bytes.byteLength).toBe(shard.bytes);
    expect(sha256(bytes)).toBe(shard.sha256);
    const parsed = parse(bytes.toString('utf8')) as {
      prompts: Array<{ bytes: number; prompt: string; sha256: string }>;
    };
    expect(parsed.prompts).toHaveLength(shard.count);
    for (const prompt of parsed.prompts) {
      expect(prompt.prompt).not.toMatch(/[\u2013\u2014]/u);
      expect(Buffer.byteLength(prompt.prompt, 'utf8')).toBe(prompt.bytes);
      expect(sha256(prompt.prompt)).toBe(prompt.sha256);
      count += 1;
    }
  }
  expect(count).toBe(1000);
}, 30_000);

test('binds native lineage, public version, and all eight cases', async () => {
  const lineage = await json<{
    active_case_ids: string[];
    native_manifest_sha256: string;
    native_version: string;
    public_version: string;
    source_case_ids: string[];
    source_files: SourceFile[];
  }>(join(skill, 'evals', 'source-lineage.json'));
  const cases = await json<{
    cases: Array<{ id: string; source_id: string }>;
  }>(join(skill, 'evals', 'cases.json'));
  expect(lineage.native_manifest_sha256).toBe(nativeManifestSha);
  expect(lineage.native_version).toBe('1.1.1');
  expect(lineage.public_version).toBe('0.1.0');
  expect(lineage.source_files).toHaveLength(228);
  expect(lineage.source_case_ids).toEqual(sourceCases);
  const activeCases = sourceCases.map(
    (_, index) => `MFWD-${String(index + 1).padStart(3, '0')}`,
  );
  expect(lineage.active_case_ids).toEqual(activeCases);
  expect(cases.cases.map(({ source_id }) => source_id)).toEqual(activeCases);
  expect(cases.cases.map(({ id }) => id)).toEqual(activeCases);
});

test('publishes the material mobile-first release contract', async () => {
  const document = await readSkillDocument(join(skill, 'SKILL.md'));
  expect(document.metadata.version).toBe('0.1.0');
  for (const marker of [
    'five-part conversion narrative',
    'exactly three style-free wireframe sequences',
    'wireframe_sha256',
    'smallest width first',
    'PASS_RELEASE_DEGRADED',
    'BLOCKED_CAPABILITY_FLOOR',
    'LCP `<=2.5s`',
    'at most two bounded repair passes',
    'Release only when',
  ])
    expect(document.source).toContain(marker);
  expect(document.source.trimEnd().split('\n').length).toBeLessThan(200);
});
