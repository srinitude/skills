import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { expect, test } from 'vitest';

import { parseSweepApproval } from './sweep-approval.js';
import { parseSweepManifest, sweepManifestHash } from './sweep-manifest.js';
import { runSweep } from './sweep-runner.js';

test('blocks execution when the response omits route evidence', async () => {
  const out = await mkdtemp(join(tmpdir(), 'skills-sweep-route-'));
  const manifest = parseSweepManifest({
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
  const approval = parseSweepApproval({
    approved_at: '2026-07-20T21:00:00Z',
    approved_by: 'user',
    cap_usd: 1,
    manifest_sha256: sweepManifestHash(manifest),
    schema_version: 1,
    unknown_price_cap_usd: 0,
  });

  try {
    await expect(
      runSweep({
        apiKey: 'test-secret',
        approval,
        capUsd: 1,
        fetchImpl: async () =>
          new Response(
            JSON.stringify({
              choices: [{ message: { content: 'result', role: 'assistant' } }],
              id: 'generation-1',
              model: 'vendor/model',
              usage: {
                completion_tokens: 4,
                cost: 0.05,
                prompt_tokens: 10,
                total_tokens: 14,
              },
            }),
            { status: 200 },
          ),
        manifest,
        out,
        phase: 'full',
        unknownPriceCapUsd: 0,
      }),
    ).rejects.toThrow();
  } finally {
    await rm(out, { force: true, recursive: true });
  }
});
