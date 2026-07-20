import type { EvalDefinition } from './schema.js';
import type {
  CompletionTransport,
  EvalRecord,
  EvalReport,
  TerminalStatus,
  TriggerRecord,
} from './types.js';

function reportStatus(records: EvalRecord[], triggers: TriggerRecord[]): TerminalStatus {
  const required = records.filter((record) => record.condition === 'with_skill');
  const statuses = [...required, ...triggers].map((record) => record.status);
  if (statuses.includes('BLOCKED')) return 'BLOCKED';
  if (statuses.includes('FAIL')) return 'FAIL';
  return 'PASS';
}

function judgePackets(records: EvalRecord[]): EvalReport['judge_packets'] {
  const ids = records
    .filter((record) => record.condition === 'with_skill')
    .map((record) => record.record_id);
  return [
    { order: 'forward', record_ids: ids },
    { order: 'reverse', record_ids: [...ids].reverse() },
  ];
}

export function buildEvalReport(
  definition: EvalDefinition,
  transport: CompletionTransport,
  records: EvalRecord[],
  triggers: TriggerRecord[],
): EvalReport {
  return {
    judge_packets: judgePackets(records),
    records,
    schema_version: 1,
    skill: definition.manifest.skill,
    status: reportStatus(records, triggers),
    test_classes: [...definition.manifest.test_classes],
    transport: transport.name,
    trigger_records: triggers,
  };
}
