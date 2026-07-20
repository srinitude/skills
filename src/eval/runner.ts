import { createHash } from 'node:crypto';
import { performance } from 'node:perf_hooks';

import { buildEvalReport } from './report.js';
import { scoreFixtureResponse } from './scoring.js';
import type { EvalDefinition } from './schema.js';
import { runTriggers } from './trigger-runner.js';
import {
  RetryableTransportError,
  type CompletionRequest,
  type CompletionResponse,
  type CompletionTransport,
  type EvalRecord,
  type EvalReport,
} from './types.js';

export { RetryableTransportError } from './types.js';
export type { CompletionRequest, CompletionTransport } from './types.js';

function sha256(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function completeWithRetry(
  transport: CompletionTransport,
  request: CompletionRequest,
): Promise<{ response?: CompletionResponse; retry: number; error?: Error }> {
  try {
    return { response: await transport.complete(request), retry: 0 };
  } catch (error) {
    if (!(error instanceof RetryableTransportError)) {
      return { error: error instanceof Error ? error : new Error(String(error)), retry: 0 };
    }
  }
  try {
    return { response: await transport.complete(request), retry: 1 };
  } catch (error) {
    return { error: error instanceof Error ? error : new Error(String(error)), retry: 1 };
  }
}

function blockedRecord(
  request: CompletionRequest,
  duration: number,
  error: Error,
): EvalRecord {
  return {
    case_id: request.case.id,
    condition: request.condition,
    duration_ms: duration,
    error: error.message,
    input_sha256: sha256(JSON.stringify(request)),
    model: '',
    output_sha256: '',
    provider: '',
    record_id: `${request.case.id}:${request.condition}:${request.replica}`,
    replica: request.replica,
    retry_count: 0,
    status: 'BLOCKED',
    usage: { input_tokens: 0, output_tokens: 0 },
  };
}

async function runCompletion(
  transport: CompletionTransport,
  request: CompletionRequest,
): Promise<EvalRecord> {
  const started = performance.now();
  const result = await completeWithRetry(transport, request);
  const duration = performance.now() - started;
  if (!result.response) {
    const record = blockedRecord(request, duration, result.error!);
    record.retry_count = result.retry;
    return record;
  }
  const score = scoreFixtureResponse(request.case, result.response.text);
  return {
    case_id: request.case.id,
    condition: request.condition,
    duration_ms: duration,
    input_sha256: sha256(JSON.stringify(request)),
    model: result.response.model,
    output_sha256: sha256(result.response.text),
    provider: result.response.provider,
    record_id: `${request.case.id}:${request.condition}:${request.replica}`,
    replica: request.replica,
    retry_count: result.retry,
    score,
    status: score.status,
    usage: result.response.usage,
  };
}

async function runBehavior(
  definition: EvalDefinition,
  transport: CompletionTransport,
): Promise<EvalRecord[]> {
  const records: EvalRecord[] = [];
  for (const testCase of definition.cases.cases) {
    for (const condition of definition.manifest.conditions) {
      for (let replica = 1; replica <= definition.manifest.repetitions; replica += 1) {
        records.push(
          await runCompletion(transport, {
            case: testCase,
            condition,
            replica,
            skill: definition.manifest.skill,
          }),
        );
      }
    }
  }
  return records;
}

export async function runEvaluation(
  definition: EvalDefinition,
  transport: CompletionTransport,
): Promise<EvalReport> {
  const records = await runBehavior(definition, transport);
  const triggerRecords = await runTriggers(definition, transport);
  return buildEvalReport(definition, transport, records, triggerRecords);
}
