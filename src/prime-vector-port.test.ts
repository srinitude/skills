import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skillRoot = join(root, 'skills', 'prime-vector');

function sha256(bytes: Buffer): string {
  return createHash('sha256').update(bytes).digest('hex');
}

interface SourceMapping {
  coverage: Record<string, number>;
  entries: Array<{ action: string }>;
}

interface VideoLearningMap {
  coverage: Record<string, number>;
  learnings: unknown[];
}

async function json<T>(path: string): Promise<T> {
  return JSON.parse(await readFile(join(root, path), 'utf8')) as T;
}

async function files(path: string): Promise<string[]> {
  const entries = await readdir(path, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const target = join(path, entry.name);
      return entry.isDirectory() ? files(target) : [target];
    }),
  );
  return nested.flat();
}

test('ships one source-bound, video-informed, dependency-free Prime Vector port', async () => {
  const source = await readFile(
    join(root, 'evidence', 'ports', 'prime-vector', 'SKILL.native.md'),
  );
  expect(sha256(source)).toBe(
    'b358ac94da13b083a6459a76e8de0262f1cb4e7e0f6be6460e80d616b02b9816',
  );

  const manifest = await json<Record<string, unknown>>(
    'evidence/ports/prime-vector/manifest.json',
  );
  expect(manifest).toMatchObject({
    excluded_entries: [],
    files: [
      {
        bytes: 13216,
        evidence_path: 'SKILL.native.md',
        lines: 150,
        nonblank_lines: 107,
        sha256: 'b358ac94da13b083a6459a76e8de0262f1cb4e7e0f6be6460e80d616b02b9816',
        source_path: 'SKILL.md',
      },
    ],
    skill: 'prime-vector',
    source_case_ids: [],
    source_version: '1.0.0',
  });

  const skill = await readFile(join(skillRoot, 'SKILL.md'), 'utf8');
  expect(skill.split('\n').length).toBeLessThan(200);
  for (const phrase of [
    'rough notes or dictation',
    'practice loop',
    'unaided reasoning',
    'first principles',
    'outcome ownership',
    'advisory panel',
    'approved examples',
    'least data needed',
    'observed traces',
    'Do not diagnose personality',
  ]) {
    expect(skill).toContain(phrase);
  }
  expect(skill).not.toContain('(evals/video-learning-map.json)');

  const publicFiles = await files(skillRoot);
  const forbidden =
    /\b(?:hermes|herdr|mcp|starting-point|outcome-bounded-work|would-humans-actually|would-agents-actually|computer-user|claude|codex|chatgpt|openai)\b/i;
  for (const path of publicFiles) {
    const bytes = await readFile(path);
    expect(bytes.includes(0), relative(skillRoot, path)).toBe(false);
    expect(bytes.toString('utf8'), relative(skillRoot, path)).not.toMatch(forbidden);
  }

  const mapping = await json<SourceMapping>(
    'skills/prime-vector/evals/source-mapping.json',
  );
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: 107,
    ratio: 1,
    source_nonblank_lines: 107,
  });
  expect(mapping.entries).toHaveLength(107);
  expect(mapping.entries.every((entry) => entry.action !== 'drop')).toBe(true);

  const video = await json<VideoLearningMap>(
    'skills/prime-vector/evals/video-learning-map.json',
  );
  const videoEvidence = await json<VideoLearningMap>(
    'evidence/ports/prime-vector/video-learning-map.json',
  );
  expect(video.coverage).toEqual({
    claim_only: 2,
    material_learning_clusters: 25,
    missing_without_disposition: 0,
    present: 13,
    strengthen: 10,
  });
  expect(video.learnings).toHaveLength(25);
  expect(videoEvidence.coverage).toEqual(video.coverage);
  expect(videoEvidence.learnings).toEqual(video.learnings);
});
