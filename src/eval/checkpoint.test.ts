import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import {
  checkpointKey,
  loadCheckpoints,
  writeCheckpoint,
  type Checkpoint,
} from './checkpoint.js';

const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

async function directory(): Promise<string> {
  const path = await mkdtemp(join(tmpdir(), 'skill-checkpoint-'));
  temporary.push(path);
  return path;
}

function record(overrides: Partial<Checkpoint> = {}): Checkpoint {
  return {
    case_id: 'SP-001',
    condition: 'with_skill',
    model: 'vendor/model',
    record_hash: 'a'.repeat(64),
    replica: 1,
    status: 'PASS',
    ...overrides,
  };
}

test('writes and reloads atomic per-case checkpoints', async () => {
  const root = await directory();
  const first = record();
  const second = record({ case_id: 'SP-002', record_hash: 'b'.repeat(64) });
  await writeCheckpoint(root, first);
  await writeCheckpoint(root, second);
  await writeCheckpoint(root, first);

  const loaded = await loadCheckpoints(root);
  expect([...loaded.keys()].sort()).toEqual(
    [checkpointKey(first), checkpointKey(second)].sort(),
  );
});

test('rejects a conflicting checkpoint for the same paid call', async () => {
  const root = await directory();
  await writeCheckpoint(root, record());
  await expect(
    writeCheckpoint(root, record({ record_hash: 'c'.repeat(64) })),
  ).rejects.toThrow('checkpoint conflict');
});

test('fails closed on a malformed checkpoint file', async () => {
  const root = await directory();
  await mkdir(root, { recursive: true });
  await writeFile(join(root, 'broken.json'), '{', 'utf8');
  await expect(loadCheckpoints(root)).rejects.toThrow('invalid checkpoint');
});
