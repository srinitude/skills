import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Ajv } from 'ajv';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

async function validate(name: string, value: unknown): Promise<boolean> {
  const source = JSON.parse(await readFile(join(root, 'schemas', name), 'utf8'));
  return new Ajv({ allErrors: true, strict: true }).compile(source)(value) as boolean;
}

const request = {
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
};

test('sweep manifest schema accepts one immutable fixed-route request', async () => {
  const manifest = { requests: [request], run_id: 'run-2026-07-20', schema_version: 1 };
  expect(await validate('sweep-manifest.schema.json', manifest)).toBe(true);
  expect(await validate('sweep-manifest.schema.json', { ...manifest, extra: true })).toBe(
    false,
  );
});

test('sweep approval schema binds one manifest and both spend caps', async () => {
  const approval = {
    approved_at: '2026-07-20T21:00:00Z',
    approved_by: 'user',
    cap_usd: 1,
    manifest_sha256: 'a'.repeat(64),
    schema_version: 1,
    unknown_price_cap_usd: 0,
  };
  expect(await validate('sweep-approval.schema.json', approval)).toBe(true);
  expect(
    await validate('sweep-approval.schema.json', { ...approval, approved_by: 'agent' }),
  ).toBe(false);
});

test('sweep checkpoint schema records reconciliable first-party cost', async () => {
  const checkpoint = {
    actual_cost_usd: 0.05,
    ledger_id: 'candidate-001#1',
    provider_name: 'Provider Label',
    raw_sha256: 'a'.repeat(64),
    request_hash: 'b'.repeat(64),
    request_id: 'candidate-001',
    response_id: 'generation-1',
    schema_version: 1,
  };
  expect(await validate('sweep-checkpoint.schema.json', checkpoint)).toBe(true);
  expect(
    await validate('sweep-checkpoint.schema.json', { ...checkpoint, extra: true }),
  ).toBe(false);
});

test('sweep pending schema binds an in-flight request before execution', async () => {
  const pending = {
    ledger_id: 'candidate-001',
    manifest_sha256: 'a'.repeat(64),
    request_hash: 'b'.repeat(64),
    request_id: 'candidate-001',
    schema_version: 1,
  };
  expect(await validate('sweep-pending.schema.json', pending)).toBe(true);
  expect(await validate('sweep-pending.schema.json', { ...pending, extra: true })).toBe(
    false,
  );
});
