import { expect, test } from 'vitest';

import { OpenRouterTransport } from './openrouter-transport.js';
import {
  RetryableTransportError,
  type CompletionRequest,
  type TriggerRequest,
} from './types.js';
import type { EvalCase } from './schema.js';

const testCase: EvalCase = {
  decision: 'align',
  group: 'alignment',
  id: 'SP-001',
  pressures: [],
  prompt: 'Find the real outcome.',
  required: ['State the outcome.'],
  source_id: 'SP-001',
  title: 'Outcome first',
  veto: ['Do not guess.'],
};

const request: CompletionRequest = {
  case: testCase,
  condition: 'with_skill',
  replica: 1,
  skill: 'starting-point',
};

function completionResponse(content = 'State the outcome.') {
  return new Response(
    JSON.stringify({
      choices: [{ message: { content, role: 'assistant' } }],
      model: 'vendor/model',
      usage: { completion_tokens: 4, prompt_tokens: 10, total_tokens: 14 },
    }),
    { headers: { 'content-type': 'application/json' }, status: 200 },
  );
}

test('sends a paired completion request and captures normalized usage', async () => {
  let captured: { body?: Record<string, unknown>; headers?: Headers; url?: string } = {};
  const fetchImpl: typeof fetch = async (input, init) => {
    captured = {
      body: JSON.parse(String(init?.body)) as Record<string, unknown>,
      headers: new Headers(init?.headers),
      url: String(input),
    };
    return completionResponse();
  };
  const transport = new OpenRouterTransport({
    apiKey: 'test-secret',
    fetchImpl,
    model: 'vendor/model',
    skillDescription: 'Use when the real outcome or route is unclear.',
    skillSource: '# Starting point\n\nUse the proof loop.',
  });

  const response = await transport.complete(request);
  const messages = captured.body?.messages as Array<{ content: string; role: string }>;

  expect(captured.url).toBe('https://openrouter.ai/api/v1/chat/completions');
  expect(captured.headers?.get('authorization')).toBe('Bearer test-secret');
  expect(messages[0]?.content).toContain('Use the proof loop.');
  expect(messages.at(-1)).toEqual({ content: testCase.prompt, role: 'user' });
  expect(captured.body).toMatchObject({
    max_tokens: 512,
    model: 'vendor/model',
    stream: false,
  });
  expect(response).toMatchObject({
    model: 'vendor/model',
    provider: 'openrouter',
    text: 'State the outcome.',
    usage: { input_tokens: 10, output_tokens: 4 },
  });
});

test('omits skill bytes from the baseline condition', async () => {
  let body: Record<string, unknown> = {};
  const fetchImpl: typeof fetch = async (_input, init) => {
    body = JSON.parse(String(init?.body)) as Record<string, unknown>;
    return completionResponse('baseline');
  };
  const transport = new OpenRouterTransport({
    apiKey: 'test-secret',
    fetchImpl,
    model: 'vendor/model',
    skillDescription: 'Use when the real outcome or route is unclear.',
    skillSource: 'PRIVATE SKILL BYTES',
  });

  await transport.complete({ ...request, condition: 'without_skill' });
  expect(JSON.stringify(body)).not.toContain('PRIVATE SKILL BYTES');
});

test('uses strict structured output for trigger classification', async () => {
  let body: Record<string, unknown> = {};
  const fetchImpl: typeof fetch = async (_input, init) => {
    body = JSON.parse(String(init?.body)) as Record<string, unknown>;
    return completionResponse('{"triggered":true}');
  };
  const transport = new OpenRouterTransport({
    apiKey: 'test-secret',
    fetchImpl,
    model: 'vendor/model',
    skillDescription: 'Use when the real outcome or route is unclear.',
    skillSource: 'skill',
  });
  const triggerRequest: TriggerRequest = {
    replica: 1,
    skill: 'starting-point',
    test: {
      id: 'TR-001',
      kind: 'positive',
      prompt: 'The route is unclear.',
      should_trigger: true,
    },
  };

  const response = await transport.classifyTrigger(triggerRequest);
  expect(response.triggered).toBe(true);
  expect(body).toMatchObject({
    provider: { require_parameters: true },
    response_format: { type: 'json_schema' },
  });
});

test('marks documented transient HTTP errors as retryable', async () => {
  const transport = new OpenRouterTransport({
    apiKey: 'test-secret',
    fetchImpl: async () => new Response('limited', { status: 429 }),
    model: 'vendor/model',
    skillDescription: 'Use when the real outcome or route is unclear.',
    skillSource: 'skill',
  });

  await expect(transport.complete(request)).rejects.toBeInstanceOf(RetryableTransportError);
});
