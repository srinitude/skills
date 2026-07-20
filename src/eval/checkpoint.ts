import { createHash, randomUUID } from 'node:crypto';
import { link, mkdir, readFile, readdir, unlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

import { z } from 'zod';

const checkpointSchema = z
  .object({
    case_id: z.string().min(1),
    condition: z.enum(['with_skill', 'without_skill']),
    model: z.string().min(1),
    record_hash: z.string().regex(/^[a-f0-9]{64}$/),
    replica: z.number().int().positive(),
    status: z.enum(['PASS', 'FAIL', 'BLOCKED']),
  })
  .strict();

export type Checkpoint = z.infer<typeof checkpointSchema>;

export function checkpointKey(checkpoint: Checkpoint): string {
  return [
    checkpoint.model,
    checkpoint.case_id,
    checkpoint.condition,
    checkpoint.replica,
  ].join('|');
}

function filename(checkpoint: Checkpoint): string {
  const hash = createHash('sha256').update(checkpointKey(checkpoint)).digest('hex');
  return `${hash}.json`;
}

function parseCheckpoint(source: string, name: string): Checkpoint {
  try {
    return checkpointSchema.parse(JSON.parse(source));
  } catch {
    throw new Error(`invalid checkpoint: ${name}`);
  }
}

async function readExisting(path: string): Promise<Checkpoint | undefined> {
  try {
    return parseCheckpoint(await readFile(path, 'utf8'), path.split('/').at(-1) ?? path);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return undefined;
    throw error;
  }
}

function verifyCompatible(existing: Checkpoint, next: Checkpoint): void {
  if (
    checkpointKey(existing) !== checkpointKey(next) ||
    existing.record_hash !== next.record_hash
  ) {
    throw new Error(`checkpoint conflict: ${checkpointKey(next)}`);
  }
}

async function commitTemp(
  temp: string,
  target: string,
  checkpoint: Checkpoint,
): Promise<void> {
  try {
    await link(temp, target);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error;
    const existing = await readExisting(target);
    if (!existing) throw error;
    verifyCompatible(existing, checkpoint);
  } finally {
    await unlink(temp).catch(() => undefined);
  }
}

export async function writeCheckpoint(
  directory: string,
  checkpoint: Checkpoint,
): Promise<void> {
  const parsed = checkpointSchema.parse(checkpoint);
  await mkdir(directory, { recursive: true });
  const target = join(directory, filename(parsed));
  const existing = await readExisting(target);
  if (existing) {
    verifyCompatible(existing, parsed);
    return;
  }
  const temp = join(directory, `.tmp-${process.pid}-${randomUUID()}`);
  await writeFile(temp, `${JSON.stringify(parsed)}\n`, { encoding: 'utf8', flag: 'wx' });
  await commitTemp(temp, target, parsed);
}

export async function loadCheckpoints(directory: string): Promise<Map<string, Checkpoint>> {
  let names: string[];
  try {
    names = await readdir(directory);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return new Map();
    throw error;
  }
  const checkpoints = new Map<string, Checkpoint>();
  for (const name of names.filter((value) => value.endsWith('.json')).sort()) {
    const checkpoint = parseCheckpoint(await readFile(join(directory, name), 'utf8'), name);
    const key = checkpointKey(checkpoint);
    if (checkpoints.has(key)) throw new Error(`checkpoint conflict: ${key}`);
    checkpoints.set(key, checkpoint);
  }
  return checkpoints;
}
