import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { loadCatalog } from './catalog.js';

const roots: string[] = [];

async function addSkill(root: string, name: string, description: string): Promise<void> {
  const skill = join(root, 'skills', name);
  await mkdir(skill, { recursive: true });
  await writeFile(
    join(skill, 'SKILL.md'),
    `---\nname: ${name}\ndescription: "${description}"\nmetadata:\n  version: "0.1.0"\n---\n\n# ${name}\n`,
  );
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

test('discovers skills in name order with public metadata', async () => {
  const root = await mkdtemp(join(tmpdir(), 'skills-catalog-'));
  roots.push(root);
  await addSkill(root, 'zeta-skill', 'Use when zeta work is requested.');
  await addSkill(root, 'alpha-skill', 'Use when alpha work is requested.');

  await expect(loadCatalog(root)).resolves.toEqual([
    {
      description: 'Use when alpha work is requested.',
      name: 'alpha-skill',
      path: 'skills/alpha-skill/SKILL.md',
      version: '0.1.0',
    },
    {
      description: 'Use when zeta work is requested.',
      name: 'zeta-skill',
      path: 'skills/zeta-skill/SKILL.md',
      version: '0.1.0',
    },
  ]);
});
