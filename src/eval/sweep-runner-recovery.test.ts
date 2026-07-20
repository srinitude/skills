import { access, mkdtemp, readFile, rm } from 'node:fs/promises';
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
    kind: 'candidate' as const,
    max_input_tokens: 100,
    max_output_tokens: 20,
    messages: [{ content: 'Evaluate all cases.', role: 'user' as const }],
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

function manifest(requests: SweepRequest[] = [request('candidate-001')]) {
  return parseSweepManifest({
    requests,
    run_id: 'run-2026-07-20-recovery',
    schema_version: 1,
  });
}

function approval(
  input: ReturnType<typeof manifest>,
  capUsd: number,
  unknownPriceCapUsd = 0,
) {
  return parseSweepApproval({
    approved_at: '2026-07-20T21:00:00Z',
    approved_by: 'user',
    cap_usd: capUsd,
    manifest_sha256: sweepManifestHash(input),
    schema_version: 1,
    unknown_price_cap_usd: unknownPriceCapUsd,
  });
}

async function output(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'skills-sweep-recovery-'));
  roots.push(root);
  return root;
}

function response(id: string, cost: number): Response {
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
      usage: { completion_tokens: 1, cost, prompt_tokens: 1, total_tokens: 2 },
    }),
    { status: 200 },
  );
}

test('executes and reconciles a verified zero-cost route', async () => {
  const out = await output();
  const zero = request('candidate-zero');
  zero.pricing = {
    completion_usd_per_token: 0,
    prompt_usd_per_token: 0,
    request_usd: 0,
  };
  zero.reservation_usd = 0;
  const input = manifest([zero]);

  const result = await runSweep({
    apiKey: ['test', 'key'].join('-'),
    approval: approval(input, 1),
    capUsd: 1,
    fetchImpl: async () => response('generation-zero', 0),
    manifest: input,
    out,
    phase: 'full',
    unknownPriceCapUsd: 0,
  });

  expect(result).toMatchObject({ completed: 1, status: 'PASS' });
  expect(JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8'))).toMatchObject({
    actual_usd: 0,
    entries: [
      {
        actual_usd: 0,
        id: 'candidate-zero',
        reservation_usd: 0,
        status: 'completed',
      },
    ],
    reserved_usd: 0,
  });
});

test('releases a rejected request and resumes under a tight cap', async () => {
  const out = await output();
  const input = manifest([request('candidate-a'), request('candidate-b')]);
  let calls = 0;
  const options = {
    apiKey: ['test', 'key'].join('-'),
    approval: approval(input, 0.28),
    capUsd: 0.28,
    fetchImpl: async () => {
      calls += 1;
      if (calls === 1) return new Response('temporary failure', { status: 503 });
      return response(`generation-${calls}`, 0.01);
    },
    manifest: input,
    out,
    phase: 'full' as const,
    unknownPriceCapUsd: 0,
  };

  await expect(runSweep(options)).rejects.toThrow('OpenRouter request failed: 503');
  expect(JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8'))).toMatchObject({
    actual_usd: 0,
    entries: [],
    reserved_usd: 0,
  });

  const resumed = await runSweep(options);
  const ledger = JSON.parse(await readFile(join(out, 'spend-ledger.json'), 'utf8')) as {
    entries: Array<{ id: string }>;
  };
  expect(calls).toBe(3);
  expect(resumed).toMatchObject({ completed: 2, status: 'PASS' });
  expect(ledger.entries.map((entry) => entry.id)).toEqual(['candidate-a', 'candidate-b']);
});

test('blocks unknown pricing before opening the ledger', async () => {
  const out = await output();
  const unknown = request('candidate-unknown');
  unknown.pricing = {
    completion_usd_per_token: null,
    prompt_usd_per_token: null,
    request_usd: 0,
  };
  unknown.reservation_usd = 0.05;
  const input = manifest([unknown]);
  let calls = 0;

  await expect(
    runSweep({
      apiKey: ['test', 'key'].join('-'),
      approval: approval(input, 1, 0.05),
      capUsd: 1,
      fetchImpl: async () => {
        calls += 1;
        return response('must-not-run', 0);
      },
      manifest: input,
      out,
      phase: 'full',
      unknownPriceCapUsd: 0.05,
    }),
  ).rejects.toThrow('cannot execute unknown-price request');

  expect(calls).toBe(0);
  await expect(access(join(out, 'spend-ledger.json'))).rejects.toMatchObject({
    code: 'ENOENT',
  });
});
