import { randomUUID } from 'node:crypto';
import { mkdir, open, readFile, rename, unlink } from 'node:fs/promises';
import { dirname } from 'node:path';

import { z } from 'zod';

const hash = z.string().regex(/^[a-f0-9]{64}$/);

const checkpointSchema = z
  .object({
    actual_cost_usd: z.number().nonnegative(),
    ledger_id: z.string().min(1),
    provider_name: z.string().min(1),
    raw_sha256: hash,
    request_hash: hash,
    request_id: z.string().min(1),
    response_id: z.string().min(1),
    schema_version: z.literal(1),
  })
  .strict();

const pendingSchema = z
  .object({
    ledger_id: z.string().min(1),
    manifest_sha256: hash,
    request_hash: hash,
    request_id: z.string().min(1),
    schema_version: z.literal(1),
  })
  .strict();

export type SweepCheckpoint = z.infer<typeof checkpointSchema>;
export type SweepPending = z.infer<typeof pendingSchema>;

export function verifyPending(
  pending: SweepPending,
  expected: Omit<SweepPending, 'ledger_id' | 'schema_version'>,
): void {
  if (
    pending.request_id !== expected.request_id ||
    pending.request_hash !== expected.request_hash ||
    pending.manifest_sha256 !== expected.manifest_sha256
  ) {
    throw new Error(`pending request conflict: ${expected.request_id}`);
  }
}

async function readOptional<T>(path: string, schema: z.ZodType<T>): Promise<T | undefined> {
  try {
    return schema.parse(JSON.parse(await readFile(path, 'utf8')));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return undefined;
    throw error;
  }
}

async function syncDirectory(path: string): Promise<void> {
  let directory;
  try {
    directory = await open(path, 'r');
    await directory.sync();
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (
      process.platform === 'win32' &&
      ['EINVAL', 'EISDIR', 'EPERM'].includes(code ?? '')
    ) {
      return;
    }
    throw error;
  } finally {
    await directory?.close();
  }
}

export async function writeJson(path: string, value: unknown): Promise<void> {
  const parent = dirname(path);
  await mkdir(parent, { recursive: true });
  const temporary = `${path}.tmp-${process.pid}-${randomUUID()}`;
  const file = await open(temporary, 'wx');
  try {
    try {
      await file.writeFile(`${JSON.stringify(value, null, 2)}\n`);
      await file.sync();
    } finally {
      await file.close();
    }
    await rename(temporary, path);
    await syncDirectory(parent);
  } finally {
    await unlink(temporary).catch((error: NodeJS.ErrnoException) => {
      if (error.code !== 'ENOENT') throw error;
    });
  }
}

export async function unlinkIfExists(path: string): Promise<void> {
  await unlink(path).catch((error: NodeJS.ErrnoException) => {
    if (error.code !== 'ENOENT') throw error;
  });
}

export function readCheckpoint(path: string): Promise<SweepCheckpoint | undefined> {
  return readOptional(path, checkpointSchema);
}

export function readPending(path: string): Promise<SweepPending | undefined> {
  return readOptional(path, pendingSchema);
}
