import { z } from 'zod';

import type { SweepRequest } from './sweep-manifest.js';

const chatUrl = 'https://openrouter.ai/api/v1/chat/completions';
const generationUrl = 'https://openrouter.ai/api/v1/generation';

const responseSchema = z
  .object({
    choices: z
      .array(
        z.object({ message: z.object({ content: z.string().nullable() }).passthrough() }),
      )
      .min(1),
    id: z.string().min(1),
    model: z.string().min(1),
    openrouter_metadata: z
      .object({
        endpoints: z.object({
          available: z.array(
            z.object({ provider: z.string().min(1), selected: z.boolean() }).passthrough(),
          ),
          total: z.number().int().positive(),
        }),
      })
      .passthrough(),
    usage: z
      .object({
        completion_tokens: z.number().int().nonnegative(),
        cost: z.number().nonnegative().optional(),
        prompt_tokens: z.number().int().nonnegative(),
        total_tokens: z.number().int().nonnegative(),
      })
      .passthrough(),
  })
  .passthrough();

const rejectionSchema = z
  .object({
    openrouter_metadata: z
      .object({ attempt: z.number().int().nonnegative() })
      .passthrough()
      .optional(),
  })
  .passthrough();

const generationSchema = z.object({
  data: z
    .object({ provider_name: z.string().min(1), total_cost: z.number().nonnegative() })
    .passthrough(),
});

export interface SweepResponse {
  cost: number;
  provider: string;
  raw: unknown;
  responseId: string;
}

export class OpenRouterRequestRejectedError extends Error {
  constructor(
    status: number,
    readonly confirmedUnsent: boolean,
    readonly generationId: string | null,
  ) {
    super(
      `OpenRouter request failed: ${status}${generationId ? `; generation: ${generationId}` : ''}`,
    );
    this.name = 'OpenRouterRequestRejectedError';
  }
}

type ExecutableSweepRequest = SweepRequest & {
  pricing: {
    completion_usd_per_token: number;
    prompt_usd_per_token: number;
    request_usd: number;
  };
};

export function assertSweepRequestExecutable(
  request: SweepRequest,
): asserts request is ExecutableSweepRequest {
  const pricing = request.pricing;
  if (pricing.prompt_usd_per_token === null || pricing.completion_usd_per_token === null) {
    throw new Error(`cannot execute unknown-price request: ${request.id}`);
  }
}

function route(request: SweepRequest): Record<string, unknown> {
  assertSweepRequestExecutable(request);
  const pricing = request.pricing;
  return {
    allow_fallbacks: false,
    max_price: {
      completion: pricing.completion_usd_per_token * 1_000_000,
      prompt: pricing.prompt_usd_per_token * 1_000_000,
    },
    only: [request.provider],
    require_parameters: true,
  };
}

async function actualCost(
  response: z.infer<typeof responseSchema>,
  expectedProvider: string,
  apiKey: string,
  fetchImpl: typeof fetch,
): Promise<number> {
  if (response.usage.cost !== undefined) return response.usage.cost;
  const lookup = await fetchImpl(`${generationUrl}?id=${encodeURIComponent(response.id)}`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  if (!lookup.ok) throw new Error(`generation cost lookup failed: ${lookup.status}`);
  const generation = generationSchema.parse(await lookup.json()).data;
  if (generation.provider_name !== expectedProvider) {
    throw new Error(`provider mismatch: ${generation.provider_name}`);
  }
  return generation.total_cost;
}

function selectedProvider(response: z.infer<typeof responseSchema>): string {
  const selected = response.openrouter_metadata.endpoints.available.filter(
    (endpoint) => endpoint.selected,
  );
  if (selected.length !== 1) throw new Error('selected provider evidence is not unique');
  return selected[0]!.provider;
}

async function rejectedError(response: Response): Promise<OpenRouterRequestRejectedError> {
  const raw: unknown = await response.json().catch(() => undefined);
  const parsed = rejectionSchema.safeParse(raw);
  const confirmedUnsent = parsed.success && parsed.data.openrouter_metadata?.attempt === 0;
  return new OpenRouterRequestRejectedError(
    response.status,
    confirmedUnsent,
    response.headers.get('x-generation-id'),
  );
}

export async function executeSweepRequest(
  request: SweepRequest,
  apiKey: string,
  fetchImpl: typeof fetch,
): Promise<SweepResponse> {
  const response = await fetchImpl(chatUrl, {
    body: JSON.stringify({
      max_tokens: request.max_output_tokens,
      messages: request.messages,
      model: request.model,
      provider: route(request),
      stream: false,
    }),
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'X-OpenRouter-Metadata': 'enabled',
    },
    method: 'POST',
  });
  if (!response.ok) throw await rejectedError(response);
  const raw: unknown = await response.json();
  const parsed = responseSchema.parse(raw);
  const provider = selectedProvider(parsed);
  if (provider !== request.provider_name) throw new Error(`provider mismatch: ${provider}`);
  return {
    cost: await actualCost(parsed, request.provider_name, apiKey, fetchImpl),
    provider,
    raw,
    responseId: parsed.id,
  };
}
