import { readFile } from 'node:fs/promises';

import { parse } from 'yaml';
import { z } from 'zod';

const metadataSchema = z
  .object({
    author: z.literal('Kiren Srinivasan'),
    version: z.string().regex(/^\d+\.\d+\.\d+$/),
  })
  .strict();

const skillHeaderSchema = z
  .object({
    description: z.string().min(1).max(1024),
    license: z.literal('MIT'),
    metadata: metadataSchema,
    name: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  })
  .strict();

export interface SkillDocument {
  body: string;
  description: string;
  license: 'MIT';
  metadata: { author: 'Kiren Srinivasan'; version: string };
  name: string;
  source: string;
}

function splitFrontmatter(source: string): { body: string; yaml: string } {
  if (!source.startsWith('---\n'))
    throw new Error('SKILL.md must start with YAML frontmatter');
  const end = source.indexOf('\n---\n', 4);
  if (end < 0) throw new Error('SKILL.md frontmatter is not closed');
  return { body: source.slice(end + 5), yaml: source.slice(4, end) };
}

export async function readSkillDocument(path: string): Promise<SkillDocument> {
  const source = await readFile(path, 'utf8');
  const parts = splitFrontmatter(source);
  const header = skillHeaderSchema.parse(parse(parts.yaml));
  return { ...header, body: parts.body, source };
}
