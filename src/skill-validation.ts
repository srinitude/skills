import { access, readFile } from 'node:fs/promises';
import { join, posix } from 'node:path';

import { z } from 'zod';

import { casesSchema, type EvalCases } from './eval/schema.js';
import { readSkillDocument, type SkillDocument } from './skill-document.js';

const sha256 = z.string().regex(/^[a-f0-9]{64}$/);
const lineageSchema = z
  .object({
    native_manifest_sha256: sha256,
    native_version: z.string().min(1),
    public_files: z
      .array(
        z
          .object({
            path: z.string().min(1),
            source_paths: z.array(z.string().min(1)).min(1),
          })
          .strict(),
      )
      .min(1),
    public_version: z.string().regex(/^\d+\.\d+\.\d+$/),
    schema_version: z.literal(1),
    source_case_ids: z.array(z.string().min(1)).min(1),
    source_files: z.array(z.object({ path: z.string().min(1), sha256 }).strict()).min(1),
  })
  .strict();

type Lineage = z.infer<typeof lineageSchema>;

export interface SkillValidationReport {
  caseCount: number;
  errors: string[];
  manifestSha256: string;
  name: string;
  skillPath: string;
  status: 'BLOCKED' | 'FAIL' | 'PASS';
  version: string;
}

function duplicateValues(values: string[]): string[] {
  return [...new Set(values.filter((value, index) => values.indexOf(value) !== index))];
}

function validateRelations(
  skill: SkillDocument,
  lineage: Lineage,
  cases: EvalCases,
): string[] {
  const errors: string[] = [];
  if (!skill.description.startsWith('Use when ')) {
    errors.push('skill description must start with Use when');
  }
  if (skill.name !== cases.skill) errors.push('skill name does not match eval cases');
  if (skill.metadata.version !== lineage.public_version)
    errors.push('public versions differ');
  const ids = cases.cases.map((entry) => entry.id);
  const sources = cases.cases.map((entry) => entry.source_id).sort();
  if (duplicateValues(ids).length > 0) errors.push('eval case IDs must be unique');
  if (duplicateValues(sources).length > 0) errors.push('source case IDs must be unique');
  if (sources.join('\n') !== [...lineage.source_case_ids].sort().join('\n')) {
    errors.push('source case IDs do not match lineage');
  }
  if (skill.source.trimEnd().split('\n').length >= 200)
    errors.push('SKILL.md must stay below 200 lines');
  return errors;
}

function referencedFiles(skill: SkillDocument): string[] {
  const matches = skill.body.matchAll(/\((references\/[^)#]+)\)/g);
  return [...new Set([...matches].map((match) => match[1]).filter(Boolean) as string[])];
}

async function validateReferences(
  skillDir: string,
  skill: SkillDocument,
): Promise<string[]> {
  const errors: string[] = [];
  for (const relative of referencedFiles(skill)) {
    try {
      await access(join(skillDir, relative));
    } catch {
      errors.push(`missing reference: ${relative}`);
    }
  }
  return errors;
}

function blocked(name: string, skillPath: string, error: unknown): SkillValidationReport {
  const message = error instanceof Error ? error.message : String(error);
  return {
    caseCount: 0,
    errors: [message],
    manifestSha256: '',
    name,
    skillPath,
    status: 'BLOCKED',
    version: '',
  };
}

export async function validateSkill(
  root: string,
  name: string,
): Promise<SkillValidationReport> {
  const skillPath = posix.join('skills', name, 'SKILL.md');
  const skillDir = join(root, 'skills', name);
  try {
    const [skill, lineageRaw, casesRaw] = await Promise.all([
      readSkillDocument(join(root, skillPath)),
      readFile(join(skillDir, 'evals', 'source-lineage.json'), 'utf8'),
      readFile(join(skillDir, 'evals', 'cases.json'), 'utf8'),
    ]);
    const lineage = lineageSchema.parse(JSON.parse(lineageRaw));
    const cases = casesSchema.parse(JSON.parse(casesRaw));
    const errors = [...validateRelations(skill, lineage, cases)];
    if (skill.name !== name) errors.push('skill name does not match its directory');
    errors.push(...(await validateReferences(skillDir, skill)));
    return {
      caseCount: cases.cases.length,
      errors,
      manifestSha256: lineage.native_manifest_sha256,
      name,
      skillPath,
      status: errors.length === 0 ? 'PASS' : 'FAIL',
      version: skill.metadata.version,
    };
  } catch (error) {
    return blocked(name, skillPath, error);
  }
}
