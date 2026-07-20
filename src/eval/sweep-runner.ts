import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, unlink, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

import { z } from 'zod';

import { SpendLedger } from './spend-ledger.js';
import {
  parseSweepApproval,
  verifySweepApproval,
  type SweepApproval,
} from './sweep-approval.js';
import { planSweep, sweepManifestHash, type SweepManifest } from './sweep-manifest.js';
import { executeSweepRequest } from './sweep-openrouter.js';

const checkpointSchema = z
  .object({
    actual_cost_usd: z.number().nonnegative(),
    ledger_id: z.string().min(1),
    provider_name: z.string().min(1),
    raw_sha256: z.string().regex(/^[a-f0-9]{64}$/),
    request_hash: z.string().regex(/^[a-f0-9]{64}$/),
    request_id: z.string().min(1),
    response_id: z.string().min(1),
    schema_version: z.literal(1),
  })
  .strict();

type SweepPhase = 'dry-run' | 'full' | 'pilot';

export interface SweepOptions {
  apiKey?: string;
  approval?: SweepApproval;
  capUsd: number;
  fetchImpl?: typeof fetch;
  manifest: SweepManifest;
  out: string;
  phase: SweepPhase;
  unknownPriceCapUsd: number;
}

export interface SweepReport {
  completed: number;
  manifest_sha256: string;
  phase: SweepPhase;
  planned: number;
  resumed: number;
  status: 'BLOCKED' | 'PASS';
}

function sha256(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function writeJson(path: string, value: unknown): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  const temporary = `${path}.tmp-${process.pid}-${randomUUID()}`;
  try {
    await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
    await rename(temporary, path);
  } finally {
    await unlink(temporary).catch(() => undefined);
  }
}

async function readCheckpoint(path: string) {
  try {
    return checkpointSchema.parse(JSON.parse(await readFile(path, 'utf8')));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return undefined;
    throw error;
  }
}

export async function runSweep(options: SweepOptions): Promise<SweepReport> {
  const plan = planSweep(options.manifest, {
    capUsd: options.capUsd,
    unknownPriceCapUsd: options.unknownPriceCapUsd,
  });
  const manifestHash = sweepManifestHash(options.manifest);
  const selected =
    options.phase === 'pilot'
      ? options.manifest.requests.slice(0, 1)
      : options.manifest.requests;
  const base: SweepReport = {
    completed: 0,
    manifest_sha256: manifestHash,
    phase: options.phase,
    planned: selected.length,
    resumed: 0,
    status: 'PASS',
  };
  await writeJson(join(options.out, 'plan.json'), {
    ...plan,
    manifest_sha256: manifestHash,
  });
  if (options.phase === 'dry-run') {
    await writeJson(join(options.out, 'report.json'), base);
    return base;
  }
  try {
    if (!options.approval) throw new Error('explicit sweep approval is required');
    verifySweepApproval(parseSweepApproval(options.approval), {
      capUsd: options.capUsd,
      manifestSha256: manifestHash,
      unknownPriceCapUsd: options.unknownPriceCapUsd,
    });
    if (!options.apiKey) throw new Error('OpenRouter API key is required');

    const ledger = await SpendLedger.open(
      join(options.out, 'spend-ledger.json'),
      options.capUsd,
    );
    const fetchImpl = options.fetchImpl ?? fetch;
    for (const request of selected) {
      const requestHash = sha256(JSON.stringify(request));
      const checkpointPath = join(options.out, 'checkpoints', `${request.id}.json`);
      const rawPath = join(options.out, 'raw', `${request.id}.json`);
      const existing = await readCheckpoint(checkpointPath);
      if (existing) {
        if (existing.request_hash !== requestHash)
          throw new Error(`checkpoint conflict: ${request.id}`);
        if (existing.provider_name !== request.provider_name)
          throw new Error(`checkpoint provider mismatch: ${request.id}`);
        const rawSource = await readFile(rawPath, 'utf8');
        if (sha256(rawSource) !== existing.raw_sha256)
          throw new Error(`raw checkpoint hash mismatch: ${request.id}`);
        await ledger.reserve(existing.ledger_id, request.reservation_usd);
        await ledger.reconcile(existing.ledger_id, existing.actual_cost_usd);
        base.completed += 1;
        base.resumed += 1;
        continue;
      }
      const attempts = ledger
        .snapshot()
        .entries.filter((entry) => entry.id.startsWith(`${request.id}#`));
      const ledgerId = `${request.id}#${attempts.length + 1}`;
      await ledger.reserve(ledgerId, request.reservation_usd);
      const result = await executeSweepRequest(request, options.apiKey, fetchImpl);
      const rawSource = `${JSON.stringify(result.raw, null, 2)}\n`;
      await writeJson(rawPath, result.raw);
      await writeJson(checkpointPath, {
        actual_cost_usd: result.cost,
        ledger_id: ledgerId,
        provider_name: result.provider,
        raw_sha256: sha256(rawSource),
        request_hash: requestHash,
        request_id: request.id,
        response_id: result.responseId,
        schema_version: 1,
      });
      await ledger.reconcile(ledgerId, result.cost);
      base.completed += 1;
    }
    await writeJson(join(options.out, 'report.json'), base);
    return base;
  } catch (error) {
    await writeJson(join(options.out, 'report.json'), { ...base, status: 'BLOCKED' });
    throw error;
  }
}
