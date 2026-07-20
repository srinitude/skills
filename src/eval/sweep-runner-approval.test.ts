import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { expect, test } from 'vitest';

import { parseSweepManifest } from './sweep-manifest.js';
import { runSweep } from './sweep-runner.js';

test('blocks paid phases without manifest-bound user approval', async () => {
  const out = await mkdtemp(join(tmpdir(), 'skills-sweep-approval-'));
  let calls = 0;
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

  try {
    await expect(
      runSweep({
        apiKey: 'test-secret',
        capUsd: 1,
        fetchImpl: async () => {
          calls += 1;
          throw new Error('network must not run');
        },
        manifest,
        out,
        phase: 'pilot',
        unknownPriceCapUsd: 0,
      }),
    ).rejects.toThrow('explicit sweep approval is required');
    expect(calls).toBe(0);
  } finally {
    await rm(out, { force: true, recursive: true });
  }
});
