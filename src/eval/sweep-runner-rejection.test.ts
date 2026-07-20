import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { parseSweepApproval } from './sweep-approval.js';
import {
  parseSweepManifest,
  sweepManifestHash,
  type SweepRequest,
} from './sweep-manifest.js';
import { runSweep } from './sweep-runner.js';

const roots: string[] = [];

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { force: true, recursive: true })),
  );
});

function request(id: string): SweepRequest {
  return {
    id,
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
  };
}

function manifest(requests: SweepRequest[]) {
  return parseSweepManifest({
    requests,
    run_id: 'run-2026-07-20-rejection',
    schema_version: 1,
  });
}

function options(input: ReturnType<typeof manifest>, out: string, fetchImpl: typeof fetch) {
  return {
    apiKey: process.version,
    approval: parseSweepApproval({
      approved_at: '2026-07-20T21:00:00Z',
      approved_by: 'user',
      cap_usd: 0.28,
      manifest_sha256: sweepManifestHash(input),
      schema_version: 1,
      unknown_price_cap_usd: 0,
    }),
    capUsd: 0.28,
    fetchImpl,
    manifest: input,
    out,
    phase: 'full' as const,
    unknownPriceCapUsd: 0,
  };
}

function rejection(attempt?: number): Response {
  return new Response(
    JSON.stringify({
      error: { code: 503, message: 'temporary failure' },
      ...(attempt === undefined ? {} : { openrouter_metadata: { attempt } }),
    }),
    { status: 503 },
  );
}

function success(id: string): Response {
  return new Response(
    JSON.stringify({
      choices: [{ message: { content: 'result', role: 'assistant' } }],
      id,
      model: 'vendor/model',
      openrouter_metadata: {
        endpoints: {
          available: [{ provider: 'Provider Label', selected: true }],
          total: 1,
        },
      },
      usage: { completion_tokens: 1, cost: 0.01, prompt_tokens: 1, total_tokens: 2 },
    }),
    { status: 200 },
  );
}

async function output(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'skills-sweep-rejection-'));
  roots.push(root);
  return root;
}

test('keeps an ambiguous rejection pending and blocks retry before HTTP', async () => {
  const out = await output();
  const input = manifest([request('candidate-a')]);
  let calls = 0;
  const run = options(input, out, async () => {
    calls += 1;
    return rejection();
  });

  await expect(runSweep(run)).rejects.toThrow('OpenRouter request failed: 503');
  expect(JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8'))).toMatchObject({
    entries: [{ id: 'candidate-a', status: 'reserved' }],
    reserved_usd: 0.14,
  });

  await expect(runSweep(run)).rejects.toThrow('pending request requires reconciliation');
  expect(calls).toBe(1);
});

test('releases a rejection proven unsent and resumes under a tight cap', async () => {
  const out = await output();
  const input = manifest([request('candidate-a'), request('candidate-b')]);
  let calls = 0;
  const run = options(input, out, async () => {
    calls += 1;
    if (calls === 1) return rejection(0);
    return success(`generation-${calls}`);
  });

  await expect(runSweep(run)).rejects.toThrow('OpenRouter request failed: 503');
  expect(JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8'))).toMatchObject({
    entries: [],
    reserved_usd: 0,
  });

  const resumed = await runSweep(run);
  expect(calls).toBe(3);
  expect(resumed).toMatchObject({ completed: 2, status: 'PASS' });
});
