import { expect, test } from 'vitest';

import { parseSweepManifest } from './sweep-manifest.js';
import { executeSweepRequest } from './sweep-openrouter.js';

function request() {
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
  }).requests[0]!;
}

function chat(overrides: Record<string, unknown> = {}) {
  return {
    choices: [{ message: { content: 'result', role: 'assistant' } }],
    id: 'generation-1',
    model: 'vendor/model',
    openrouter_metadata: {
      attempt: 1,
      endpoints: {
        available: [{ model: 'vendor/model', provider: 'Provider Label', selected: true }],
        total: 1,
      },
      requested: 'vendor/model',
      strategy: 'direct',
    },
    usage: { completion_tokens: 4, cost: 0.05, prompt_tokens: 10, total_tokens: 14 },
    ...overrides,
  };
}

test('locks one route and reads selected provider metadata', async () => {
  let headers = new Headers();
  let body: Record<string, unknown> = {};
  const result = await executeSweepRequest(request(), 'test-secret', async (_url, init) => {
    headers = new Headers(init?.headers);
    body = JSON.parse(String(init?.body));
    return new Response(JSON.stringify(chat()), { status: 200 });
  });

  expect(headers.get('X-OpenRouter-Metadata')).toBe('enabled');
  expect(body.provider).toEqual({
    allow_fallbacks: false,
    max_price: { completion: 2000, prompt: 1000 },
    only: ['provider/route'],
    require_parameters: true,
  });
  expect(result).toMatchObject({ cost: 0.05, provider: 'Provider Label' });
});

test('uses generation metadata when chat usage omits cost', async () => {
  const urls: string[] = [];
  const result = await executeSweepRequest(request(), 'test-secret', async (url) => {
    urls.push(String(url));
    if (urls.length === 1) {
      return new Response(
        JSON.stringify(
          chat({
            usage: { completion_tokens: 4, prompt_tokens: 10, total_tokens: 14 },
          }),
        ),
        { status: 200 },
      );
    }
    return new Response(
      JSON.stringify({ data: { provider_name: 'Provider Label', total_cost: 0.05 } }),
      { status: 200 },
    );
  });

  expect(urls[1]).toContain('/generation?id=generation-1');
  expect(result.cost).toBe(0.05);
});

test('blocks a selected or reconciled provider mismatch', async () => {
  await expect(
    executeSweepRequest(
      request(),
      'test-secret',
      async () =>
        new Response(
          JSON.stringify(
            chat({
              openrouter_metadata: {
                endpoints: {
                  available: [{ provider: 'Other Provider', selected: true }],
                  total: 1,
                },
              },
            }),
          ),
          { status: 200 },
        ),
    ),
  ).rejects.toThrow('provider mismatch');
});
