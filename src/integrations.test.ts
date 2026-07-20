import { execFile } from 'node:child_process';
import { access, readFile, realpath, rm } from 'node:fs/promises';
import { dirname, isAbsolute, relative, resolve } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import { parse } from 'yaml';
import { expect, test } from 'vitest';
import { z } from 'zod';

import { checkIntegrations } from './integrations.js';

const run = promisify(execFile);
const root = dirname(dirname(fileURLToPath(import.meta.url)));

const openClawManifestSchema = z
  .object({
    configSchema: z
      .object({
        additionalProperties: z.literal(false),
        properties: z.record(z.string(), z.unknown()),
        type: z.literal('object'),
      })
      .strict(),
    description: z.string().min(1),
    id: z.string().min(1),
    name: z.string().min(1),
    skills: z.array(z.string()).min(1),
    version: z.literal('0.1.0'),
  })
  .strict();

const pluginManifestSchema = z
  .object({
    author: z.literal('Kiren Srinivasan'),
    description: z.string().min(1),
    kind: z.literal('standalone'),
    manifest_version: z.literal(1),
    name: z.literal('srinitude-skills'),
    provides_hooks: z.array(z.string()),
    provides_tools: z.array(z.string()),
    version: z.literal('0.1.0'),
  })
  .strict();

function inside(parent: string, child: string): boolean {
  const path = relative(parent, child);
  return path === '' || (!path.startsWith('..') && !isAbsolute(path));
}

test('the OpenClaw plugin loads the canonical skills directory', async () => {
  const source = await readFile(resolve(root, 'openclaw.plugin.json'), 'utf8');
  const manifest = openClawManifestSchema.parse(JSON.parse(source));
  const realRoot = await realpath(root);

  expect(manifest.id).toBe('srinitude-skills');
  for (const skillRoot of manifest.skills) {
    expect(inside(realRoot, await realpath(resolve(root, skillRoot)))).toBe(true);
  }
});

test('the repository-root Python plugin registers canonical skill bytes', async () => {
  const source = await readFile(resolve(root, 'plugin.yaml'), 'utf8');
  pluginManifestSchema.parse(parse(source));
  const script = [
    'import importlib.util,json,pathlib,sys',
    'root=pathlib.Path(sys.argv[1])',
    'spec=importlib.util.spec_from_file_location("srinitude_skills",root/"__init__.py")',
    'module=importlib.util.module_from_spec(spec)',
    'spec.loader.exec_module(module)',
    'class Context:',
    '  def __init__(self): self.skills=[]',
    '  def register_skill(self,name,path,description=""): self.skills.append({"name":name,"path":str(path),"description":description})',
    'ctx=Context()',
    'module.register(ctx)',
    'print(json.dumps(ctx.skills))',
  ].join('\n');
  const { stdout } = await run('python3', ['-c', script, root], {
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  const skills = z
    .array(
      z.object({ description: z.string(), name: z.string(), path: z.string() }).strict(),
    )
    .parse(JSON.parse(stdout));

  expect(skills).toEqual([
    {
      description: 'Use when an outcome is stated, inferred, or hidden.',
      name: 'starting-point',
      path: resolve(root, 'skills', 'starting-point', 'SKILL.md'),
    },
  ]);
});

test('integration checks do not leave Python bytecode in the repository', async () => {
  const cache = resolve(root, '__pycache__');
  await rm(cache, { force: true, recursive: true });
  expect((await checkIntegrations(root)).status).toBe('PASS');
  await expect(access(cache)).rejects.toMatchObject({ code: 'ENOENT' });
});
