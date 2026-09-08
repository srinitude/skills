import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { readSkillDocument } from './skill-document.js';

const roots: string[] = [];

async function skillFile(description: string): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'skill-document-'));
  roots.push(root);
  const path = join(root, 'SKILL.md');
  await writeFile(
    path,
    `---\nname: test-skill\ndescription: "${description}"\nlicense: MIT\nmetadata:\n  author: Kiren Srinivasan\n  version: "0.1.0"\n---\n\n# Test\n`,
  );
  return path;
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

test('accepts a description with exactly 1024 characters', async () => {
  const description = `Use when ${'x'.repeat(1015)}`;
  const skill = await readSkillDocument(await skillFile(description));
  expect(skill.description).toBe(description);
});

test('rejects a description with 1025 characters', async () => {
  const description = `Use when ${'x'.repeat(1016)}`;
  await expect(readSkillDocument(await skillFile(description))).rejects.toThrow();
});

test.each(['user', 'project'])(
  'retains %s scope and metadata extensions',
  async (scope) => {
    const path = await skillFile('Use when checking scopes.');
    const source = await readFile(path, 'utf8');
    await writeFile(
      path,
      source.replace(
        '  version:',
        `  scope: "${scope}"\n  project-id: "example/repo"\n  version:`,
      ),
    );
    expect((await readSkillDocument(path)).metadata).toMatchObject({
      scope,
      'project-id': 'example/repo',
    });
  },
);

test.each(['global', 'null', 'true', '1', '[user]', 'user\n  scope: project'])(
  'rejects malformed scope %s',
  async (value) => {
    const path = await skillFile('Use when checking scopes.');
    const source = await readFile(path, 'utf8');
    await writeFile(path, source.replace('  version:', `  scope: ${value}\n  version:`));
    await expect(readSkillDocument(path)).rejects.toThrow();
  },
);
