import { performance } from 'node:perf_hooks';

import { loadCatalog } from '../catalog.js';
import { runEvaluation } from './runner.js';
import { loadEvalDefinition, type EvalDefinition } from './schema.js';
import type { CompletionRequest, CompletionTransport, TerminalStatus } from './types.js';

export interface SpeedReport {
  case_p95_ms: number;
  cold_start_ms: number;
  discovery_ms: number;
  full_load_ms: number;
  full_run_ms: number;
  samples: number;
  skill: string;
  status: TerminalStatus;
  transport: string;
  warm_start_p50_ms: number;
  warm_start_p95_ms: number;
}

export function percentile(values: number[], quantile: number): number {
  if (values.length === 0) throw new Error('percentile requires at least one value');
  if (quantile < 0 || quantile > 1)
    throw new Error('quantile must be between zero and one');
  const sorted = [...values].sort((left, right) => left - right);
  const rank = Math.max(1, Math.ceil(quantile * sorted.length));
  return sorted[rank - 1]!;
}

async function measure<T>(
  operation: () => Promise<T>,
): Promise<{ duration: number; value: T }> {
  const started = performance.now();
  const value = await operation();
  return { duration: performance.now() - started, value };
}

function firstRequest(definition: EvalDefinition): CompletionRequest {
  const testCase = definition.cases.cases[0];
  if (!testCase) throw new Error('benchmark requires at least one case');
  return {
    case: testCase,
    condition: 'with_skill',
    replica: 1,
    skill: definition.manifest.skill,
  };
}

async function measureWarmCalls(
  transport: CompletionTransport,
  request: CompletionRequest,
  samples: number,
): Promise<number[]> {
  const durations: number[] = [];
  for (let index = 0; index < samples; index += 1) {
    const result = await measure(() => transport.complete(request));
    durations.push(result.duration);
  }
  return durations;
}

function speedStatus(
  report: Omit<SpeedReport, 'status'>,
  definition: EvalDefinition,
): TerminalStatus {
  const budget = definition.budgets.fixture;
  const pass =
    report.cold_start_ms <= budget.cold_start_ms_max &&
    report.warm_start_p95_ms <= budget.warm_start_ms_max &&
    report.case_p95_ms <= budget.case_p95_ms_max &&
    report.full_run_ms <= budget.full_run_ms_max;
  return pass ? 'PASS' : 'FAIL';
}

export async function runSkillBenchmark(
  root: string,
  skill: string,
  transport: CompletionTransport,
  samples: number,
): Promise<SpeedReport> {
  if (!Number.isInteger(samples) || samples < 2)
    throw new Error('samples must be at least two');
  const discovery = await measure(() => loadCatalog(root));
  if (!discovery.value.some((entry) => entry.name === skill))
    throw new Error(`unknown skill: ${skill}`);
  const fullLoad = await measure(() => loadEvalDefinition(root, skill));
  const request = firstRequest(fullLoad.value);
  const cold = await measure(() => transport.complete(request));
  const warm = await measureWarmCalls(transport, request, samples);
  const fullRun = await measure(() => runEvaluation(fullLoad.value, transport));
  const report = {
    case_p95_ms: percentile(warm, 0.95),
    cold_start_ms: cold.duration,
    discovery_ms: discovery.duration,
    full_load_ms: fullLoad.duration,
    full_run_ms: fullRun.duration,
    samples,
    skill,
    transport: transport.name,
    warm_start_p50_ms: percentile(warm, 0.5),
    warm_start_p95_ms: percentile(warm, 0.95),
  };
  return { ...report, status: speedStatus(report, fullLoad.value) };
}
