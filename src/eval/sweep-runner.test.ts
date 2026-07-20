import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
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
        id: 'candidate-001',
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
    run_id: 'run-2026-07-20',
    schema_version: 1,
  });
}

function approval(input: ReturnType<typeof manifest>) {
  return parseSweepApproval({
    approved_at: '2026-07-20T21:00:00Z',
    approved_by: 'user',
    cap_usd: 1,
    manifest_sha256: sweepManifestHash(input),
    schema_version: 1,
    unknown_price_cap_usd: 0,
  });
}

async function output(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'skills-sweep-'));
  roots.push(root);
  return root;
}

test('dry-run validates and writes a plan without a key or network call', async () => {
  const out = await output();
  let calls = 0;

  const report = await runSweep({
    capUsd: 1,
    fetchImpl: async () => {
      calls += 1;
      throw new Error('network must not run');
    },
    manifest: manifest(),
    out,
    phase: 'dry-run',
    unknownPriceCapUsd: 0,
  });

  expect(calls).toBe(0);
  expect(report).toMatchObject({
    completed: 0,
    phase: 'dry-run',
    planned: 1,
    status: 'PASS',
  });
  expect(JSON.parse(await readFile(join(out, 'plan.json'), 'utf8'))).toMatchObject({
    request_count: 1,
    reservation_usd: 0.14,
  });
});

test('executes one exact fixed route and reconciles first-party response cost', async () => {
  const out = await output();
  const input = manifest();
  let body: Record<string, unknown> = {};
  let authorization = '';
  const fetchImpl: typeof fetch = async (_input, init) => {
    body = JSON.parse(String(init?.body)) as Record<string, unknown>;
    authorization = new Headers(init?.headers).get('authorization') ?? '';
    return new Response(
      JSON.stringify({
        choices: [{ message: { content: 'result', role: 'assistant' } }],
        id: 'generation-1',
        model: 'vendor/model',
        openrouter_metadata: {
          endpoints: {
            available: [{ provider: 'Provider Label', selected: true }],
            total: 1,
          },
        },
        usage: {
          completion_tokens: 4,
          cost: 0.05,
          prompt_tokens: 10,
          total_tokens: 14,
        },
      }),
      { status: 200 },
    );
  };

  const report = await runSweep({
    apiKey: 'test-secret',
    approval: approval(input),
    capUsd: 1,
    fetchImpl,
    manifest: input,
    out,
    phase: 'full',
    unknownPriceCapUsd: 0,
  });

  expect(authorization).toBe('Bearer test-secret');
  expect(body).toMatchObject({
    max_tokens: 20,
    model: 'vendor/model',
    provider: {
      allow_fallbacks: false,
      max_price: { completion: 2000, prompt: 1000 },
      only: ['provider/route'],
      require_parameters: true,
    },
    stream: false,
  });
  expect(report).toMatchObject({ completed: 1, planned: 1, status: 'PASS' });
  expect(JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8'))).toMatchObject({
    actual_usd: 0.05,
    reserved_usd: 0,
  });
  expect(
    JSON.parse(await readFile(join(out, 'checkpoints', 'candidate-001.json'), 'utf8')),
  ).toMatchObject({ provider_name: 'Provider Label' });
});

test('resumes a completed request without sending it twice', async () => {
  const out = await output();
  const input = manifest();
  let calls = 0;
  const fetchImpl: typeof fetch = async () => {
    calls += 1;
    return new Response(
      JSON.stringify({
        choices: [{ message: { content: 'result', role: 'assistant' } }],
        id: 'generation-1',
        model: 'vendor/model',
        openrouter_metadata: {
          endpoints: {
            available: [{ provider: 'Provider Label', selected: true }],
            total: 1,
          },
        },
        usage: { completion_tokens: 4, cost: 0.05, prompt_tokens: 10, total_tokens: 14 },
      }),
      { status: 200 },
    );
  };
  const options = {
    apiKey: 'test-secret',
    approval: approval(input),
    capUsd: 1,
    fetchImpl,
    manifest: input,
    out,
    phase: 'full' as const,
    unknownPriceCapUsd: 0,
  };

  await runSweep(options);
  const resumed = await runSweep(options);

  expect(calls).toBe(1);
  expect(resumed).toMatchObject({ completed: 1, resumed: 1, status: 'PASS' });

  await writeFile(join(out, 'raw', 'candidate-001.json'), '{}\n');
  await expect(runSweep(options)).rejects.toThrow('raw checkpoint hash mismatch');
  expect(calls).toBe(1);
});
