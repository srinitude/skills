import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { parseSweepApproval } from './sweep-approval.js';
import { parseSweepManifest, sweepManifestHash } from './sweep-manifest.js';
import { runSweep } from './sweep-runner.js';

const roots: string[] = [];

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { force: true, recursive: true })),
  );
});

function manifest() {
  return parseSweepManifest({
    requests: [
      {
        id: 'candidate-pending',
        kind: 'candidate',
        max_input_tokens: 100,
        max_output_tokens: 20,
        messages: [{ content: 'Evaluate all cases.', role: 'user' }],
        model: 'vendor/model',
        pricing: {
          completion_usd_per_token: 0.002,
          prompt_usd_per_token: 0.001,
          request_usd: 0,
        },
        provider: 'provider/route',
        provider_name: 'Provider Label',
        reservation_usd: 0.14,
      },
    ],
    run_id: 'run-2026-07-20-pending',
    schema_version: 1,
  });
}

function response(cost = 0.01): Response {
  return new Response(
    JSON.stringify({
      choices: [{ message: { content: 'result', role: 'assistant' } }],
      id: 'generation-must-not-run',
      model: 'vendor/model',
      openrouter_metadata: {
        endpoints: {
          available: [{ provider: 'Provider Label', selected: true }],
          total: 1,
        },
      },
      usage: {
        completion_tokens: 1,
        cost,
        prompt_tokens: 1,
        total_tokens: 2,
      },
    }),
    { status: 200 },
  );
}

test('persists ambiguous in-flight state and blocks automatic repayment', async () => {
  const out = await mkdtemp(join(tmpdir(), 'skills-sweep-pending-'));
  roots.push(out);
  const input = manifest();
  const apiKey = ['local', 'placeholder'].join('-');
  let calls = 0;
  const base = {
    apiKey,
    approval: parseSweepApproval({
      approved_at: '2026-07-20T21:00:00Z',
      approved_by: 'user',
      cap_usd: 1,
      manifest_sha256: sweepManifestHash(input),
      schema_version: 1,
      unknown_price_cap_usd: 0,
    }),
    capUsd: 1,
    manifest: input,
    out,
    phase: 'full' as const,
    unknownPriceCapUsd: 0,
  };

  await expect(
    runSweep({
      ...base,
      fetchImpl: async () => {
        calls += 1;
        throw new TypeError('connection reset');
      },
    }),
  ).rejects.toThrow('connection reset');

  const pendingPath = join(out, 'pending', 'candidate-pending.json');
  const pending = JSON.parse(await readFile(pendingPath, 'utf8'));
  expect(pending).toEqual({
    ledger_id: 'candidate-pending',
    manifest_sha256: sweepManifestHash(input),
    request_hash: expect.stringMatching(/^[a-f0-9]{64}$/),
    request_id: 'candidate-pending',
    schema_version: 1,
  });
  expect(JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8'))).toMatchObject({
    actual_usd: 0,
    reserved_usd: 0.14,
  });
  const artifactText = (
    await Promise.all(
      [
        'plan.json',
        'report.json',
        'spend-ledger.json',
        'pending/candidate-pending.json',
      ].map((path) => readFile(join(out, path), 'utf8')),
    )
  ).join('\n');
  expect(artifactText).not.toContain(apiKey);

  const mustNotRun = async () => {
    calls += 1;
    return response();
  };
  await expect(runSweep({ ...base, fetchImpl: mustNotRun })).rejects.toThrow(
    'pending request requires reconciliation: candidate-pending',
  );
  expect(calls).toBe(1);

  await rm(pendingPath);
  await expect(runSweep({ ...base, fetchImpl: mustNotRun })).rejects.toThrow(
    'reservation requires reconciliation: candidate-pending',
  );
  expect(calls).toBe(1);
});

test('blocks repayment when actual cost exceeds the reservation', async () => {
  const out = await mkdtemp(join(tmpdir(), 'skills-sweep-overrun-'));
  roots.push(out);
  const input = manifest();
  let calls = 0;
  const options = {
    apiKey: ['local', 'placeholder'].join('-'),
    approval: parseSweepApproval({
      approved_at: '2026-07-20T21:00:00Z',
      approved_by: 'user',
      cap_usd: 1,
      manifest_sha256: sweepManifestHash(input),
      schema_version: 1,
      unknown_price_cap_usd: 0,
    }),
    capUsd: 1,
    fetchImpl: async () => {
      calls += 1;
      return response(0.15);
    },
    manifest: input,
    out,
    phase: 'full' as const,
    unknownPriceCapUsd: 0,
  };

  await expect(runSweep(options)).rejects.toThrow('actual cost exceeds reservation');
  await expect(runSweep(options)).rejects.toThrow('actual cost exceeds reservation');
  expect(calls).toBe(1);
  expect(
    await Promise.all(
      ['checkpoints/candidate-pending.json', 'pending/candidate-pending.json'].map((path) =>
        readFile(join(out, path), 'utf8'),
      ),
    ),
  ).toHaveLength(2);
});
