import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

import { SpendLedger } from './spend-ledger.js';
import {
  readCheckpoint,
  readPending,
  unlinkIfExists,
  verifyPending,
  writeJson,
} from './sweep-artifacts.js';
import {
  parseSweepApproval,
  verifySweepApproval,
  type SweepApproval,
} from './sweep-approval.js';
import { planSweep, sweepManifestHash, type SweepManifest } from './sweep-manifest.js';
import {
  assertSweepRequestExecutable,
  executeSweepRequest,
  OpenRouterRequestRejectedError,
} from './sweep-openrouter.js';

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

function reservationId(ledger: SpendLedger, requestId: string): string {
  const matching = ledger
    .snapshot()
    .entries.filter(
      (entry) => entry.id === requestId || entry.id.startsWith(`${requestId}#`),
    );
  const reserved = matching.filter((entry) => entry.status === 'reserved');
  if (reserved.length > 1)
    throw new Error(`multiple reservations require repair: ${requestId}`);
  if (reserved[0]) throw new Error(`reservation requires reconciliation: ${requestId}`);
  if (matching.some((entry) => entry.status === 'completed')) {
    throw new Error(`completed ledger entry missing checkpoint: ${requestId}`);
  }
  return requestId;
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
    selected.forEach(assertSweepRequestExecutable);

    const ledger = await SpendLedger.open(
      join(options.out, 'spend-ledger.json'),
      options.capUsd,
    );
    const fetchImpl = options.fetchImpl ?? fetch;
    for (const request of selected) {
      const requestHash = sha256(JSON.stringify(request));
      const checkpointPath = join(options.out, 'checkpoints', `${request.id}.json`);
      const pendingPath = join(options.out, 'pending', `${request.id}.json`);
      const rawPath = join(options.out, 'raw', `${request.id}.json`);
      const expectedPending = {
        manifest_sha256: manifestHash,
        request_hash: requestHash,
        request_id: request.id,
      };
      const existing = await readCheckpoint(checkpointPath);
      const pending = await readPending(pendingPath);
      if (existing) {
        if (pending) {
          verifyPending(pending, expectedPending);
          if (pending.ledger_id !== existing.ledger_id) {
            throw new Error(`pending ledger conflict: ${request.id}`);
          }
        }
        if (existing.request_hash !== requestHash)
          throw new Error(`checkpoint conflict: ${request.id}`);
        if (existing.provider_name !== request.provider_name)
          throw new Error(`checkpoint provider mismatch: ${request.id}`);
        const rawSource = await readFile(rawPath, 'utf8');
        if (sha256(rawSource) !== existing.raw_sha256)
          throw new Error(`raw checkpoint hash mismatch: ${request.id}`);
        await ledger.reserve(existing.ledger_id, request.reservation_usd);
        await ledger.reconcile(existing.ledger_id, existing.actual_cost_usd);
        await unlinkIfExists(pendingPath);
        base.completed += 1;
        base.resumed += 1;
        continue;
      }
      if (pending) {
        verifyPending(pending, expectedPending);
        const entry = ledger.snapshot().entries.find(({ id }) => id === pending.ledger_id);
        if (
          !entry ||
          entry.status !== 'reserved' ||
          entry.reservation_usd !== request.reservation_usd
        ) {
          throw new Error(`pending ledger mismatch: ${request.id}`);
        }
        throw new Error(`pending request requires reconciliation: ${request.id}`);
      }
      const ledgerId = reservationId(ledger, request.id);
      await ledger.reserve(ledgerId, request.reservation_usd);
      await writeJson(pendingPath, {
        ...expectedPending,
        ledger_id: ledgerId,
        schema_version: 1,
      });
      const result = await executeSweepRequest(request, options.apiKey, fetchImpl).catch(
        async (error: unknown) => {
          if (error instanceof OpenRouterRequestRejectedError) {
            await ledger.release(ledgerId);
            await unlinkIfExists(pendingPath);
          }
          throw error;
        },
      );
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
      await unlinkIfExists(pendingPath);
      base.completed += 1;
    }
    await writeJson(join(options.out, 'report.json'), base);
    return base;
  } catch (error) {
    await writeJson(join(options.out, 'report.json'), { ...base, status: 'BLOCKED' });
    throw error;
  }
}
