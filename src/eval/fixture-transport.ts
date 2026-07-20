import type {
  CompletionRequest,
  CompletionResponse,
  CompletionTransport,
  TriggerRequest,
  TriggerResponse,
} from './types.js';

export class FixtureTransport implements CompletionTransport {
  readonly name = 'fixture';

  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    const text =
      request.condition === 'with_skill'
        ? request.case.required.join('\n')
        : `Synthetic baseline fixture for ${request.case.id}.`;
    return {
      model: 'synthetic-fixture',
      provider: 'local',
      text,
      usage: { input_tokens: 0, output_tokens: 0 },
    };
  }

  async classifyTrigger(request: TriggerRequest): Promise<TriggerResponse> {
    return {
      model: 'synthetic-fixture',
      provider: 'local',
      triggered: request.test.should_trigger,
      usage: { input_tokens: 0, output_tokens: 0 },
    };
  }
}
