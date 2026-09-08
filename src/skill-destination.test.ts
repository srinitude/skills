import { execFile } from 'node:child_process';
import { access, mkdir, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

const run = promisify(execFile);
const root = dirname(dirname(fileURLToPath(import.meta.url)));
const adapter = join(root, 'adapters/shared-skills/check_destination.py');
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(temporary.splice(0).map((path) => rm(path, { recursive: true })));
});

async function fixture() {
  const base = await mkdtemp(join(tmpdir(), 'skill-destination-'));
  temporary.push(base);
  return base;
}

function args(base: string, scope: string, target: string) {
  return [
    adapter,
    '--scope',
    scope,
    '--name',
    'inventory-variant',
    '--dest',
    target,
    '--home',
    join(base, 'person'),
    '--project',
    join(base, 'project'),
  ];
}

test('shared integration resolves both scopes without installing', async () => {
  const base = await fixture();
  for (const [scope, owner] of [
    ['user', 'person'],
    ['project', 'project'],
  ]) {
    const parent = join(base, owner!, '.agents/skills');
    await mkdir(parent, { recursive: true });
    const target = join(parent, 'inventory-variant');
    const { stdout } = await run('python3', args(base, scope!, target));
    expect(JSON.parse(stdout).scope).toBe(scope);
    await expect(access(target)).rejects.toMatchObject({ code: 'ENOENT' });
  }
});

test('shared integration refuses same-name shadowing without writes', async () => {
  const base = await fixture();
  const existing = join(base, 'person/.agents/skills/inventory-variant');
  const target = join(base, 'project/.agents/skills/inventory-variant');
  await mkdir(existing, { recursive: true });
  await mkdir(dirname(target), { recursive: true });
  await expect(run('python3', args(base, 'project', target))).rejects.toMatchObject({
    code: 1,
  });
  await expect(access(target)).rejects.toMatchObject({ code: 'ENOENT' });
  await expect(access(existing)).resolves.toBeUndefined();
});
