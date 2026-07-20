import { z } from 'zod';

const modelSchema = z
  .object({
    architecture: z
      .object({
        input_modalities: z.array(z.string()),
        modality: z.string().nullable().optional(),
        output_modalities: z.array(z.string()),
        tokenizer: z.string().nullable().optional(),
      })
      .passthrough(),
    context_length: z.number().int().nonnegative(),
    created: z.number().int().nonnegative(),
    id: z.string().min(1),
    name: z.string().min(1),
    pricing: z
      .object({
        completion: z.string(),
        prompt: z.string(),
        request: z.string().optional(),
      })
      .passthrough(),
    supported_parameters: z.array(z.string()).optional().default([]),
  })
  .passthrough();

const responseSchema = z.object({ data: z.array(modelSchema) }).passthrough();

export interface RankedModel {
  architecture: {
    input_modalities: string[];
    modality?: null | string;
    output_modalities: string[];
    tokenizer?: null | string;
  };
  context_length: number;
  created: number;
  id: string;
  name: string;
  pricing: { completion: string; prompt: string; request?: string };
  rank: number;
  supported_parameters: string[];
}

export interface OpenRouterInventory {
  captured_at: string;
  filter: {
    input_modalities: 'text';
    output_modalities: 'text';
    sort: 'top-weekly';
  };
  models: RankedModel[];
  schema_version: 1;
  source_url: string;
}

interface InventoryOptions {
  capturedAt: string;
  fetchImpl?: typeof fetch;
}

const sourceUrl =
  'https://openrouter.ai/api/v1/models?input_modalities=text&output_modalities=text&sort=top-weekly';

function rankedModel(model: z.infer<typeof modelSchema>, index: number): RankedModel {
  return {
    architecture: model.architecture,
    context_length: model.context_length,
    created: model.created,
    id: model.id,
    name: model.name,
    pricing: model.pricing,
    rank: index + 1,
    supported_parameters: model.supported_parameters,
  };
}

export async function fetchOpenRouterInventory(
  options: InventoryOptions,
): Promise<OpenRouterInventory> {
  const response = await (options.fetchImpl ?? fetch)(sourceUrl, {
    headers: { accept: 'application/json' },
  });
  if (!response.ok) throw new Error(`model inventory request failed: ${response.status}`);
  const parsed = responseSchema.parse(await response.json());
  return {
    captured_at: options.capturedAt,
    filter: {
      input_modalities: 'text',
      output_modalities: 'text',
      sort: 'top-weekly',
    },
    models: parsed.data.map(rankedModel),
    schema_version: 1,
    source_url: sourceUrl,
  };
}

function price(value: string, model: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) throw new Error(`invalid price for ${model}`);
  return parsed;
}

export function estimateInventoryCost(
  inventory: OpenRouterInventory,
  inputTokensPerModel: number,
  outputTokensPerModel: number,
): number {
  if (inputTokensPerModel < 0 || outputTokensPerModel < 0)
    throw new Error('tokens must be nonnegative');
  return inventory.models.reduce(
    (total, model) =>
      total +
      price(model.pricing.prompt, model.id) * inputTokensPerModel +
      price(model.pricing.completion, model.id) * outputTokensPerModel,
    0,
  );
}
