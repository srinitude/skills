import { readFile } from 'node:fs/promises';

import { z } from 'zod';

import { loadCatalog } from './catalog.js';
import { validateSkill, type SkillValidationReport } from './skill-validation.js';

const expectedPages = new Set([
  'https://agentskills.io/client-implementation/adding-skills-support.md',
  'https://agentskills.io/clients.md',
  'https://agentskills.io/home.md',
  'https://agentskills.io/skill-creation/best-practices.md',
  'https://agentskills.io/skill-creation/evaluating-skills.md',
  'https://agentskills.io/skill-creation/optimizing-descriptions.md',
  'https://agentskills.io/skill-creation/quickstart.md',
  'https://agentskills.io/skill-creation/using-scripts.md',
  'https://agentskills.io/specification.md',
]);

const evidenceSchema = z
  .object({
    captured_at: z.string().date(),
    pages: z.array(
      z
        .object({
          bytes: z.number().int().positive(),
          sha256: z.string().regex(/^[a-f0-9]{64}$/),
          url: z.string().url(),
        })
        .strict(),
    ),
    schema: z.literal('agentskills-pages/v1'),
    source: z.literal('https://agentskills.io/sitemap.xml'),
  })
  .strict();

const packageSchema = z
  .object({
    version: z.string().regex(/^\d+\.\d+\.\d+$/),
  })
  .passthrough();

export interface RepositoryValidationReport {
  errors: string[];
  skillCount: number;
  skills: SkillValidationReport[];
  sourcePageCount: number;
  status: 'BLOCKED' | 'FAIL' | 'PASS';
  version: string;
}

function validatePageSet(urls: string[]): string[] {
  const actual = new Set(urls);
  const errors: string[] = [];
  if (actual.size !== urls.length) errors.push('specification page URLs must be unique');
  for (const url of expectedPages) {
    if (!actual.has(url)) errors.push(`missing specification page: ${url}`);
  }
  for (const url of actual) {
    if (!expectedPages.has(url)) errors.push(`unexpected specification page: ${url}`);
  }
  return errors;
}

function blocked(error: unknown): RepositoryValidationReport {
  return {
    errors: [error instanceof Error ? error.message : String(error)],
    skillCount: 0,
    skills: [],
    sourcePageCount: 0,
    status: 'BLOCKED',
    version: '',
  };
}

export async function validateRepository(
  root: string,
): Promise<RepositoryValidationReport> {
  try {
    const [evidenceRaw, packageRaw, catalog] = await Promise.all([
      readFile(`${root}/evidence/agentskills-pages.json`, 'utf8'),
      readFile(`${root}/package.json`, 'utf8'),
      loadCatalog(root),
    ]);
    const evidence = evidenceSchema.parse(JSON.parse(evidenceRaw));
    const packageData = packageSchema.parse(JSON.parse(packageRaw));
    const skills = await Promise.all(
      catalog.map((entry) => validateSkill(root, entry.name)),
    );
    const errors = validatePageSet(evidence.pages.map((page) => page.url));
    for (const entry of catalog) {
      if (entry.version !== packageData.version) {
        errors.push(`${entry.name} version does not match package version`);
      }
    }
    for (const report of skills) {
      if (report.status !== 'PASS')
        errors.push(`${report.name} validation is ${report.status}`);
    }
    const status = errors.length === 0 ? 'PASS' : 'FAIL';
    return {
      errors,
      skillCount: catalog.length,
      skills,
      sourcePageCount: evidence.pages.length,
      status,
      version: packageData.version,
    };
  } catch (error) {
    return blocked(error);
  }
}
