import { mkdir, mkdtemp, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { PathPolicyError, readSkillFile } from './path-policy.js';

const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), 'skills-mcp-'));
  temporary.push(root);
  const skill = join(root, 'skills', 'example');
  await mkdir(join(skill, 'references'), { recursive: true });
  await writeFile(join(skill, 'SKILL.md'), '# Example\n');
  await writeFile(join(skill, '.secret'), 'hidden');
  const outside = join(root, 'outside.txt');
  await writeFile(outside, 'outside');
  await symlink(outside, join(skill, 'references', 'escape.md'));
  return { root };
}

async function errorCode(operation: Promise<unknown>) {
  try {
    await operation;
    return '';
  } catch (error) {
    expect(error).toBeInstanceOf(PathPolicyError);
    return (error as PathPolicyError).code;
  }
}

test('reads a regular file inside a canonical skill root', async () => {
  const { root } = await fixture();
  await expect(readSkillFile(root, 'example', 'SKILL.md')).resolves.toBe('# Example\n');
});

test('rejects invalid names, absolute paths, traversal, and hidden segments', async () => {
  const { root } = await fixture();

  await expect(errorCode(readSkillFile(root, '../example', 'SKILL.md'))).resolves.toBe(
    'INVALID_SKILL_NAME',
  );
  await expect(errorCode(readSkillFile(root, 'example', '/etc/passwd'))).resolves.toBe(
    'ABSOLUTE_PATH',
  );
  await expect(errorCode(readSkillFile(root, 'example', '../outside.txt'))).resolves.toBe(
    'PATH_TRAVERSAL',
  );
  await expect(errorCode(readSkillFile(root, 'example', '.secret'))).resolves.toBe(
    'HIDDEN_PATH',
  );
});

test('rejects a symlink whose real target leaves the skill root', async () => {
  const { root } = await fixture();
  await expect(
    errorCode(readSkillFile(root, 'example', 'references/escape.md')),
  ).resolves.toBe('SYMLINK_ESCAPE');
});
