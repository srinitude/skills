import { expect, test } from 'vitest';

import { estimateInventoryCost, fetchOpenRouterInventory } from './openrouter-inventory.js';

function model(id: string) {
  return {
    architecture: {
      input_modalities: ['text'],
      modality: 'text->text',
      output_modalities: ['text'],
      tokenizer: 'test',
    },
    context_length: 100_000,
    created: 1_700_000_000,
    id,
    name: id,
    pricing: {
      completion: '0.000002',
      prompt: '0.000001',
      request: '0',
    },
    supported_parameters: ['temperature'],
  };
}

test('freezes the Text and This Week server ranking without removing variants', async () => {
  let requested = '';
  const fetchImpl: typeof fetch = async (input) => {
    requested = String(input);
    return new Response(
      JSON.stringify({ data: [model('vendor/alpha'), model('vendor/alpha:free')] }),
      { headers: { 'content-type': 'application/json' }, status: 200 },
    );
  };

  const manifest = await fetchOpenRouterInventory({
    capturedAt: '2026-07-20T15:00:00.000Z',
    fetchImpl,
  });

  expect(requested).toBe(
    'https://openrouter.ai/api/v1/models?input_modalities=text&output_modalities=text&sort=top-weekly',
  );
  expect(manifest.models.map((entry) => [entry.id, entry.rank])).toEqual([
    ['vendor/alpha', 1],
    ['vendor/alpha:free', 2],
  ]);
  expect(manifest.filter).toEqual({
    input_modalities: 'text',
    output_modalities: 'text',
    sort: 'top-weekly',
  });
  expect(estimateInventoryCost(manifest, 1000, 500)).toBeCloseTo(0.004);
});

test('fails closed on a non-success model response', async () => {
  const fetchImpl: typeof fetch = async () => new Response('denied', { status: 403 });
  await expect(
    fetchOpenRouterInventory({ capturedAt: '2026-07-20T15:00:00.000Z', fetchImpl }),
  ).rejects.toThrow('model inventory request failed: 403');
});
