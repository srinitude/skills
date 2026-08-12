import type { EvalDefinition } from './schema.js';
import type {
  CompletionTransport,
  EvalRecord,
  EvalReport,
  TerminalStatus,
  TriggerRecord,
} from './types.js';

function reportStatus(
  definition: EvalDefinition,
  records: EvalRecord[],
  triggers: TriggerRecord[],
): TerminalStatus {
  const expectedRecords =
    definition.cases.cases.length *
    definition.manifest.conditions.length *
    definition.manifest.repetitions;
  const expectedTriggers =
    definition.triggers.cases.length * definition.manifest.repetitions;
  if (expectedRecords === 0 || expectedTriggers === 0) return 'BLOCKED';
  if (records.length !== expectedRecords || triggers.length !== expectedTriggers)
    return 'BLOCKED';
  const expectedRecordKeys = new Set<string>();
  for (const testCase of definition.cases.cases) {
    for (const condition of definition.manifest.conditions) {
      for (let replica = 1; replica <= definition.manifest.repetitions; replica += 1) {
        expectedRecordKeys.add(`${testCase.id}\0${condition}\0${replica}`);
      }
    }
  }
  const actualRecordKeys = new Set(
    records.map((record) => `${record.case_id}\0${record.condition}\0${record.replica}`),
  );
  const expectedTriggerKeys = new Set<string>();
  for (const testCase of definition.triggers.cases) {
    for (let replica = 1; replica <= definition.manifest.repetitions; replica += 1) {
      expectedTriggerKeys.add(`${testCase.id}\0${replica}`);
    }
  }
  const actualTriggerKeys = new Set(
    triggers.map((record) => `${record.id}\0${record.replica}`),
  );
  if (
    actualRecordKeys.size !== expectedRecordKeys.size ||
    actualTriggerKeys.size !== expectedTriggerKeys.size ||
    [...expectedRecordKeys].some((key) => !actualRecordKeys.has(key)) ||
    [...expectedTriggerKeys].some((key) => !actualTriggerKeys.has(key))
  ) {
    return 'BLOCKED';
  }
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
  const fixture = transport.name === 'fixture';
  return {
    claim_limit: fixture
      ? 'Deterministic fixture output checks repository contracts and does not prove skill effectiveness.'
      : 'Live output records show case-level behavior for this run only.',
    evidence_class: fixture ? 'deterministic_contract_check' : 'live_behavior_evaluation',
    judge_packets: judgePackets(records),
    records,
    schema_version: 1,
    skill: definition.manifest.skill,
    status: reportStatus(definition, records, triggers),
    test_classes: [...definition.manifest.test_classes],
    transport: transport.name,
    trigger_records: triggers,
  };
}
