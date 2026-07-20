import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

import { z } from 'zod';

export const evalCaseSchema = z
  .object({
    decision: z.string().min(1),
    group: z.string().min(1),
    id: z.string().regex(/^SP-\d{3}$/),
    pressures: z.array(z.string()),
    prompt: z.string().min(1),
    required: z.array(z.string().min(1)).min(1),
    source_id: z.string().regex(/^SP-\d{3}$/),
    title: z.string().min(1),
    veto: z.array(z.string().min(1)).min(1),
  })
  .strict();

export const casesSchema = z
  .object({
    cases: z.array(evalCaseSchema).min(1),
    decision_labels: z.array(z.string().min(1)).min(1),
    groups: z.array(z.string().min(1)).min(1),
    schema_version: z.literal(1),
    skill: z.string().min(1),
  })
  .strict();

const testClassesSchema = z.tuple([
  z.literal('positive_activation'),
  z.literal('rejection'),
  z.literal('behavior'),
  z.literal('failure_handling'),
  z.literal('recovery'),
  z.literal('speed'),
]);

export const evalManifestSchema = z
  .object({
    case_source: z.literal('cases.json'),
    conditions: z.tuple([z.literal('with_skill'), z.literal('without_skill')]),
    contract: z.literal('contract.md'),
    repetitions: z.literal(2),
    rubric: z.literal('rubric.md'),
    schema_version: z.literal(1),
    skill: z.string().min(1),
    speed_budgets: z.literal('speed-budgets.json'),
    test_classes: testClassesSchema,
    trigger_source: z.literal('trigger-cases.json'),
  })
  .strict();

const triggerCaseSchema = z
  .object({
    id: z.string().regex(/^TR-\d{3}$/),
    kind: z.enum(['hard_negative', 'near_neighbor', 'positive']),
    pair_id: z.string().min(1).optional(),
    prompt: z.string().min(1),
    should_trigger: z.boolean(),
  })
  .strict();

const triggerCasesSchema = z
  .object({
    cases: z.array(triggerCaseSchema).min(1),
    schema_version: z.literal(1),
    skill: z.string().min(1),
  })
  .strict();

const speedBudgetsSchema = z
  .object({
    failure_rule: z.literal('BLOCKED'),
    fixture: z
      .object({
        case_p95_ms_max: z.number().positive(),
        cold_start_ms_max: z.number().positive(),
        full_run_ms_max: z.number().positive(),
        warm_start_ms_max: z.number().positive(),
      })
      .strict(),
    live: z
      .object({
        activation_p95_ms_max: z.number().positive(),
        minimum_samples: z.number().int().min(2),
        response_p95_ms_max: z.number().positive(),
      })
      .strict(),
    schema_version: z.literal(1),
    skill: z.string().min(1),
  })
  .strict();

export type EvalCase = z.infer<typeof evalCaseSchema>;
export type EvalCases = z.infer<typeof casesSchema>;
export type EvalManifest = z.infer<typeof evalManifestSchema>;
export type TriggerCases = z.infer<typeof triggerCasesSchema>;
export type SpeedBudgets = z.infer<typeof speedBudgetsSchema>;

export interface EvalDefinition {
  budgets: SpeedBudgets;
  cases: EvalCases;
  manifest: EvalManifest;
  triggers: TriggerCases;
}

async function parseJsonFile<T>(path: string, schema: z.ZodType<T>): Promise<T> {
  const source = await readFile(path, 'utf8');
  return schema.parse(JSON.parse(source));
}

export async function loadEvalDefinition(
  root: string,
  skill: string,
): Promise<EvalDefinition> {
  const directory = join(root, 'skills', skill, 'evals');
  const [manifest, cases, triggers, budgets] = await Promise.all([
    parseJsonFile(join(directory, 'manifest.json'), evalManifestSchema),
    parseJsonFile(join(directory, 'cases.json'), casesSchema),
    parseJsonFile(join(directory, 'trigger-cases.json'), triggerCasesSchema),
    parseJsonFile(join(directory, 'speed-budgets.json'), speedBudgetsSchema),
  ]);
  return { budgets, cases, manifest, triggers };
}
