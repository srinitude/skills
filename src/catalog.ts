import { lstat, readdir, readFile } from 'node:fs/promises';
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

interface CatalogCandidate extends CatalogEntry {
  directory: string;
}

export function isSkillName(value: string): boolean {
  return value.length <= 64 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value);
}

function parseFrontmatter(source: string): z.infer<typeof frontmatterSchema> {
  if (!source.startsWith('---\n'))
    throw new Error('SKILL.md must start with YAML frontmatter');
  const end = source.indexOf('\n---\n', 4);
  if (end < 0) throw new Error('SKILL.md frontmatter is not closed');
  return frontmatterSchema.parse(parse(source.slice(4, end)));
}

async function readEntry(root: string, directory: string): Promise<CatalogCandidate> {
  const relative = posix.join('skills', directory, 'SKILL.md');
  const absolute = join(root, relative);
  if (!(await lstat(absolute)).isFile()) {
    throw new Error(`catalog entry is not a regular file: ${relative}`);
  }
  const metadata = parseFrontmatter(await readFile(absolute, 'utf8'));
  return {
    description: metadata.description,
    directory,
    name: metadata.name,
    path: relative,
    version: metadata.metadata.version,
  };
}

export async function loadCatalog(root: string): Promise<CatalogEntry[]> {
  const entries = await readdir(join(root, 'skills'), { withFileTypes: true });
  const names = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  const catalog = await Promise.all(names.map((name) => readEntry(root, name)));
  for (const entry of catalog) {
    if (!isSkillName(entry.directory)) {
      throw new Error(`skill directory name is invalid: ${entry.directory}`);
    }
    if (entry.name !== entry.directory) {
      throw new Error(
        `skill directory ${entry.directory} does not match name ${entry.name}`,
      );
    }
  }
  const declaredNames = catalog.map((entry) => entry.name);
  if (new Set(declaredNames).size !== declaredNames.length) {
    throw new Error('skill names must be unique');
  }
  return catalog
    .map((entry) => ({
      description: entry.description,
      name: entry.name,
      path: entry.path,
      version: entry.version,
    }))
    .sort((left, right) => left.name.localeCompare(right.name));
}
