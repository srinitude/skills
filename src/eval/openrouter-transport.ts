import { z } from 'zod';

import {
  RetryableTransportError,
  type CompletionRequest,
  type CompletionResponse,
  type CompletionTransport,
  type TriggerRequest,
  type TriggerResponse,
  type Usage,
} from './types.js';

const apiUrl = 'https://openrouter.ai/api/v1/chat/completions';
const retryableStatuses = new Set([408, 429, 500, 502, 503, 524, 529]);

const responseSchema = z
  .object({
    choices: z
      .array(
        z.object({
          message: z
            .object({ content: z.string().nullable(), role: z.string() })
            .passthrough(),
        }),
      )
      .min(1),
    model: z.string().min(1),
    usage: z
      .object({
        completion_tokens: z.number().int().nonnegative(),
        prompt_tokens: z.number().int().nonnegative(),
        total_tokens: z.number().int().nonnegative(),
      })
      .passthrough()
      .optional(),
  })
  .passthrough();

const triggerSchema = z.object({ triggered: z.boolean() }).strict();

interface OpenRouterOptions {
  apiKey: string;
  fetchImpl?: typeof fetch;
  model: string;
  skillDescription: string;
  skillSource: string;
}

export class OpenRouterTransport implements CompletionTransport {
  readonly name: string;
  private readonly apiKey: string;
  private readonly fetchImpl: typeof fetch;
  private readonly model: string;
  private readonly skillDescription: string;
  private readonly skillSource: string;

  constructor(options: OpenRouterOptions) {
    if (!options.apiKey) throw new Error('OpenRouter API key is required');
    this.apiKey = options.apiKey;
    this.fetchImpl = options.fetchImpl ?? fetch;
    this.model = options.model;
    this.name = `openrouter:${options.model}`;
    this.skillDescription = options.skillDescription;
    this.skillSource = options.skillSource;
  }

  private async post(body: Record<string, unknown>) {
    const response = await this.fetchImpl(apiUrl, {
      body: JSON.stringify(body),
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/srinitude/skills',
        'X-OpenRouter-Title': 'srinitude/skills evals',
      },
      method: 'POST',
    });
    if (!response.ok) {
      const message = `OpenRouter request failed: ${response.status}`;
      if (retryableStatuses.has(response.status))
        throw new RetryableTransportError(message);
      throw new Error(message);
    }
    return responseSchema.parse(await response.json());
  }

  private usage(response: z.infer<typeof responseSchema>): Usage {
    return {
      input_tokens: response.usage?.prompt_tokens ?? 0,
      output_tokens: response.usage?.completion_tokens ?? 0,
    };
  }

  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    const system = [
      'Answer the user request in no more than 350 words.',
      request.condition === 'with_skill'
        ? `Apply this Agent Skill:\n${this.skillSource}`
        : '',
    ]
      .filter(Boolean)
      .join('\n\n');
    const response = await this.post({
      max_tokens: 512,
      messages: [
        { content: system, role: 'system' },
        { content: request.case.prompt, role: 'user' },
      ],
      model: this.model,
      stream: false,
    });
    const text = response.choices[0]?.message.content;
    if (!text) throw new Error('OpenRouter returned empty completion content');
    return {
      model: response.model,
      provider: 'openrouter',
      text,
      usage: this.usage(response),
    };
  }

  async classifyTrigger(request: TriggerRequest): Promise<TriggerResponse> {
    const response = await this.post({
      messages: [
        {
          content:
            'Decide whether the skill description should activate for the user prompt. Return only the schema.',
          role: 'system',
        },
        {
          content: `Skill description: ${this.skillDescription}\n\nUser prompt: ${request.test.prompt}`,
          role: 'user',
        },
      ],
      model: this.model,
      provider: { require_parameters: true },
      response_format: {
        json_schema: {
          name: 'skill_activation',
          schema: {
            additionalProperties: false,
            properties: { triggered: { type: 'boolean' } },
            required: ['triggered'],
            type: 'object',
          },
          strict: true,
        },
        type: 'json_schema',
      },
      stream: false,
    });
    const content = response.choices[0]?.message.content;
    if (!content) throw new Error('OpenRouter returned empty trigger content');
    return {
      model: response.model,
      provider: 'openrouter',
      triggered: triggerSchema.parse(JSON.parse(content)).triggered,
      usage: this.usage(response),
    };
  }
}
