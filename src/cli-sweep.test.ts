import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { runCli } from './cli.js';

const roots: string[] = [];

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { force: true, recursive: true })),
  );
});

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), 'skills-cli-sweep-'));
  roots.push(root);
  const manifest = join(root, 'manifest.json');
  const out = join(root, 'out');
  await writeFile(
    manifest,
    `${JSON.stringify({
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
    })}\n`,
  );
  return { manifest, out };
}

test('runs a credential-free sweep dry-run', async () => {
  const { manifest, out } = await fixture();
  let diagnostics = '';

  const code = await runCli(
    [
      'sweep',
      '--phase',
      'dry-run',
      '--manifest',
      manifest,
      '--cap',
      '1',
      '--unknown-price-cap',
      '0',
      '--out',
      out,
    ],
    { stderr: { write: (text) => (diagnostics += text) } },
  );

  expect(code).toBe(0);
  expect(JSON.parse(await readFile(join(out, 'report.json'), 'utf8'))).toMatchObject({
    phase: 'dry-run',
    planned: 1,
    status: 'PASS',
  });
  expect(diagnostics).toContain('sweep: PASS');
});

test('blocks a paid CLI phase without an approval artifact', async () => {
  const { manifest, out } = await fixture();
  let diagnostics = '';

  const code = await runCli(
    [
      'sweep',
      '--phase',
      'pilot',
      '--manifest',
      manifest,
      '--cap',
      '1',
      '--unknown-price-cap',
      '0',
      '--out',
      out,
    ],
    { stderr: { write: (text) => (diagnostics += text) } },
  );

  expect(code).toBe(2);
  expect(diagnostics).toContain('BLOCKED: explicit sweep approval is required');
  expect(JSON.parse(await readFile(join(out, 'report.json'), 'utf8'))).toMatchObject({
    phase: 'pilot',
    status: 'BLOCKED',
  });
});
