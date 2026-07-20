import { randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, unlink, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

import { z } from 'zod';

const entrySchema = z
  .object({
    actual_usd: z.number().nonnegative().optional(),
    id: z.string().min(1),
    reservation_usd: z.number().positive(),
    status: z.enum(['completed', 'reserved']),
  })
  .strict();

const stateSchema = z
  .object({
    actual_usd: z.number().nonnegative(),
    cap_usd: z.number().positive(),
    entries: z.array(entrySchema),
    reserved_usd: z.number().nonnegative(),
    schema_version: z.literal(1),
  })
  .strict();

type LedgerEntry = z.infer<typeof entrySchema>;
export type SpendLedgerState = z.infer<typeof stateSchema>;

function total(entries: LedgerEntry[], key: 'actual' | 'reserved'): number {
  return entries.reduce((sum, entry) => {
    if (key === 'actual') return sum + (entry.actual_usd ?? 0);
    return sum + (entry.status === 'reserved' ? entry.reservation_usd : 0);
  }, 0);
}

function normalized(state: SpendLedgerState): SpendLedgerState {
  const entries = [...state.entries].sort((left, right) => left.id.localeCompare(right.id));
  return {
    ...state,
    actual_usd: total(entries, 'actual'),
    entries,
    reserved_usd: total(entries, 'reserved'),
  };
}

async function persist(path: string, state: SpendLedgerState): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  const temporary = `${path}.tmp-${process.pid}-${randomUUID()}`;
  try {
    await writeFile(temporary, `${JSON.stringify(normalized(state), null, 2)}\n`, {
      encoding: 'utf8',
      flag: 'wx',
    });
    await rename(temporary, path);
  } finally {
    await unlink(temporary).catch(() => undefined);
  }
}

export class SpendLedger {
  private queue: Promise<void> = Promise.resolve();

  private constructor(
    private readonly path: string,
    private state: SpendLedgerState,
  ) {}

  static async open(path: string, capUsd: number): Promise<SpendLedger> {
    const cap = z.number().positive().parse(capUsd);
    try {
      const state = stateSchema.parse(JSON.parse(await readFile(path, 'utf8')));
      if (state.cap_usd !== cap) throw new Error('spend cap mismatch');
      return new SpendLedger(path, normalized(state));
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
      const state = normalized({
        actual_usd: 0,
        cap_usd: cap,
        entries: [],
        reserved_usd: 0,
        schema_version: 1,
      });
      await persist(path, state);
      return new SpendLedger(path, state);
    }
  }

  snapshot(): SpendLedgerState {
    return structuredClone(this.state);
  }

  reserve(id: string, reservationUsd: number): Promise<void> {
    return this.mutate(async (next) => {
      const amount = z.number().positive().parse(reservationUsd);
      const existing = next.entries.find((entry) => entry.id === id);
      if (existing) {
        if (existing.reservation_usd !== amount)
          throw new Error(`reservation conflict: ${id}`);
        return;
      }
      if (next.actual_usd + next.reserved_usd + amount > next.cap_usd) {
        throw new Error(`spend cap exceeded: ${id}`);
      }
      next.entries.push({ id, reservation_usd: amount, status: 'reserved' });
    });
  }

  reconcile(id: string, actualUsd: number): Promise<void> {
    return this.mutate(async (next) => {
      const amount = z.number().nonnegative().parse(actualUsd);
      const entry = next.entries.find((candidate) => candidate.id === id);
      if (!entry) throw new Error(`missing reservation: ${id}`);
      if (entry.status === 'completed') {
        if (entry.actual_usd !== amount) throw new Error(`actual cost conflict: ${id}`);
        return;
      }
      if (amount > entry.reservation_usd) {
        throw new Error(`actual cost exceeds reservation: ${id}`);
      }
      entry.actual_usd = amount;
      entry.status = 'completed';
    });
  }

  private mutate(change: (next: SpendLedgerState) => Promise<void>): Promise<void> {
    const operation = this.queue.then(async () => {
      const next = this.snapshot();
      await change(next);
      const updated = normalized(next);
      await persist(this.path, updated);
      this.state = updated;
    });
    this.queue = operation.catch(() => undefined);
    return operation;
  }
}
