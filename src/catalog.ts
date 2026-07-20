import { readdir, readFile } from 'node:fs/promises';
import { join, posix } from 'node:path';

import { parse } from 'yaml';
import { z } from 'zod';

const frontmatterSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  metadata: z.object({ version: z.string().min(1) }),
});

export interface CatalogEntry {
  description: string;
  name: string;
  path: string;
  version: string;
}

function parseFrontmatter(source: string): z.infer<typeof frontmatterSchema> {
  if (!source.startsWith('---\n'))
    throw new Error('SKILL.md must start with YAML frontmatter');
  const end = source.indexOf('\n---\n', 4);
  if (end < 0) throw new Error('SKILL.md frontmatter is not closed');
  return frontmatterSchema.parse(parse(source.slice(4, end)));
}

async function readEntry(root: string, directory: string): Promise<CatalogEntry> {
  const relative = posix.join('skills', directory, 'SKILL.md');
  const metadata = parseFrontmatter(await readFile(join(root, relative), 'utf8'));
  return {
    description: metadata.description,
    name: metadata.name,
    path: relative,
    version: metadata.metadata.version,
  };
}

export async function loadCatalog(root: string): Promise<CatalogEntry[]> {
  const entries = await readdir(join(root, 'skills'), { withFileTypes: true });
  const names = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  const catalog = await Promise.all(names.map((name) => readEntry(root, name)));
  return catalog.sort((left, right) => left.name.localeCompare(right.name));
}
