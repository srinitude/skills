import { readFile } from 'node:fs/promises';

import { z } from 'zod';

import { loadCatalog } from './catalog.js';
import { validateSkill, type SkillValidationReport } from './skill-validation.js';

const expectedAgentSkillsPages = new Set([
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

const expectedSkillsShPages = new Set([
  'https://www.skills.sh/docs',
  'https://www.skills.sh/docs/cli',
  'https://www.skills.sh/docs/api',
  'https://www.skills.sh/docs/faq',
]);

const pageSchema = z
  .object({
    bytes: z.number().int().positive(),
    url: z.string().url(),
  })
  .strict();

const evidenceSchema = z
  .object({
    captured_at: z.string().date(),
    pages: z.array(
      pageSchema.extend({
        sha256: z.string().regex(/^[a-f0-9]{64}$/),
      }),
    ),
    schema: z.literal('agentskills-pages/v1'),
    source: z.literal('https://agentskills.io/sitemap.xml'),
  })
  .strict();

const skillsShEvidenceSchema = z
  .object({
    captured_at: z.string().date(),
    pages: z.array(pageSchema),
    schema: z.literal('skills-sh-pages/v1'),
    source: z.literal('https://www.skills.sh/sitemap-misc.xml'),
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

function validatePageSet(urls: string[], expected: Set<string>, label: string): string[] {
  const actual = new Set(urls);
  const errors: string[] = [];
  if (actual.size !== urls.length) errors.push(`${label} page URLs must be unique`);
  for (const url of expected) {
    if (!actual.has(url)) errors.push(`missing ${label} page: ${url}`);
  }
  for (const url of actual) {
    if (!expected.has(url)) errors.push(`unexpected ${label} page: ${url}`);
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
    const [evidenceRaw, skillsShEvidenceRaw, packageRaw, catalog] = await Promise.all([
      readFile(`${root}/evidence/agentskills-pages.json`, 'utf8'),
      readFile(`${root}/evidence/skills-sh-pages.json`, 'utf8'),
      readFile(`${root}/package.json`, 'utf8'),
      loadCatalog(root),
    ]);
    const evidence = evidenceSchema.parse(JSON.parse(evidenceRaw));
    const skillsShEvidence = skillsShEvidenceSchema.parse(JSON.parse(skillsShEvidenceRaw));
    const packageData = packageSchema.parse(JSON.parse(packageRaw));
    const skills = await Promise.all(
      catalog.map((entry) => validateSkill(root, entry.name)),
    );
    const errors = [
      ...validatePageSet(
        evidence.pages.map((page) => page.url),
        expectedAgentSkillsPages,
        'specification',
      ),
      ...validatePageSet(
        skillsShEvidence.pages.map((page) => page.url),
        expectedSkillsShPages,
        'skills.sh documentation',
      ),
    ];
    for (const report of skills) {
      if (report.status !== 'PASS')
        errors.push(`${report.name} validation is ${report.status}`);
    }
    const status = errors.length === 0 ? 'PASS' : 'FAIL';
    return {
      errors,
      skillCount: catalog.length,
      skills,
      sourcePageCount: evidence.pages.length + skillsShEvidence.pages.length,
      status,
      version: packageData.version,
    };
  } catch (error) {
    return blocked(error);
  }
}
