import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { SpendLedger } from './spend-ledger.js';

const roots: string[] = [];

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { force: true, recursive: true })),
  );
});

async function ledger(cap = 1): Promise<{ ledger: SpendLedger; path: string }> {
  const root = await mkdtemp(join(tmpdir(), 'skills-spend-ledger-'));
  roots.push(root);
  const path = join(root, 'spend.json');
  return { ledger: await SpendLedger.open(path, cap), path };
}

test('reserves before spend and rejects a hard-cap overrun', async () => {
  const { ledger: spend } = await ledger();

  await spend.reserve('request-a', 0.6);

  await expect(spend.reserve('request-b', 0.41)).rejects.toThrow('spend cap exceeded');
  expect(spend.snapshot()).toMatchObject({ actual_usd: 0, cap_usd: 1, reserved_usd: 0.6 });
});

test('reconciles first-party cost and makes released capacity reusable', async () => {
  const { ledger: spend } = await ledger();

  await spend.reserve('request-a', 0.6);
  await spend.reconcile('request-a', 0.35);
  await spend.reserve('request-b', 0.6);

  expect(spend.snapshot()).toMatchObject({ actual_usd: 0.35, reserved_usd: 0.6 });
});

test('persists and reconciles a zero-dollar reservation', async () => {
  const { ledger: spend, path } = await ledger();

  await spend.reserve('free-request', 0);
  await spend.reconcile('free-request', 0);

  expect(spend.snapshot()).toMatchObject({ actual_usd: 0, reserved_usd: 0 });
  expect(JSON.parse(await readFile(path, 'utf8'))).toMatchObject({
    entries: [
      {
        actual_usd: 0,
        id: 'free-request',
        reservation_usd: 0,
        status: 'completed',
      },
    ],
  });
});

test('releases an uncharged reservation before retry', async () => {
  const { ledger: spend } = await ledger();

  await spend.reserve('rejected-request', 0.6);
  await spend.release('rejected-request');

  expect(spend.snapshot()).toMatchObject({ actual_usd: 0, entries: [], reserved_usd: 0 });
});

test('persists exact state and resumes completed reservations idempotently', async () => {
  const { ledger: spend, path } = await ledger();
  await spend.reserve('request-a', 0.6);
  await spend.reconcile('request-a', 0.4);

  const resumed = await SpendLedger.open(path, 1);
  await resumed.reserve('request-a', 0.6);
  await resumed.reconcile('request-a', 0.4);

  expect(resumed.snapshot()).toMatchObject({ actual_usd: 0.4, reserved_usd: 0 });
  expect(JSON.parse(await readFile(path, 'utf8'))).toEqual(resumed.snapshot());
});

test('rejects cap drift and conflicting duplicate costs', async () => {
  const { ledger: spend, path } = await ledger();
  await spend.reserve('request-a', 0.6);

  await expect(SpendLedger.open(path, 2)).rejects.toThrow('spend cap mismatch');
  await expect(spend.reserve('request-a', 0.5)).rejects.toThrow('reservation conflict');
  await expect(spend.reconcile('request-a', 0.7)).rejects.toThrow(
    'actual cost exceeds reservation',
  );
});
