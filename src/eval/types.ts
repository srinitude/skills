import type { ScoreResult } from './scoring.js';
import type { EvalCase, TriggerCases } from './schema.js';

export type Condition = 'with_skill' | 'without_skill';
export type TerminalStatus = 'BLOCKED' | 'FAIL' | 'PASS';

export interface Usage {
  input_tokens: number;
  output_tokens: number;
}

export interface CompletionRequest {
  case: EvalCase;
  condition: Condition;
  replica: number;
  skill: string;
}

export interface CompletionResponse {
  model: string;
  provider: string;
  text: string;
  usage: Usage;
}

export interface TriggerRequest {
  replica: number;
  skill: string;
  test: TriggerCases['cases'][number];
}

export interface TriggerResponse {
  model: string;
  provider: string;
  triggered: boolean;
  usage: Usage;
}

export interface CompletionTransport {
  readonly name: string;
  classifyTrigger?(request: TriggerRequest): Promise<TriggerResponse>;
  complete(request: CompletionRequest): Promise<CompletionResponse>;
}

export interface EvalRecord {
  case_id: string;
  condition: Condition;
  duration_ms: number;
  error?: string;
  input_sha256: string;
  model: string;
  output_sha256: string;
  provider: string;
  record_id: string;
  replica: number;
  retry_count: number;
  score?: ScoreResult;
  status: TerminalStatus;
  usage: Usage;
}

export interface TriggerRecord {
  duration_ms: number;
  expected: boolean;
  id: string;
  replica: number;
  status: TerminalStatus;
  triggered?: boolean;
}

export interface EvalReport {
  judge_packets: Array<{ order: 'forward' | 'reverse'; record_ids: string[] }>;
  records: EvalRecord[];
  schema_version: 1;
  skill: string;
  status: TerminalStatus;
  test_classes: string[];
  transport: string;
  trigger_records: TriggerRecord[];
}

export class RetryableTransportError extends Error {}
