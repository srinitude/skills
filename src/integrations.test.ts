import { execFile } from 'node:child_process';
import { access, readFile, readdir, rm } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import { parse } from 'yaml';
import { expect, test } from 'vitest';
import { z } from 'zod';

import { validateAgentPlugin } from './agent-plugin.js';
import { checkIntegrations } from './integrations.js';

const run = promisify(execFile);
const root = dirname(dirname(fileURLToPath(import.meta.url)));

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

test('OpenClaw uses the portable bundle without a false native manifest', async () => {
  await expect(access(resolve(root, 'openclaw.plugin.json'))).rejects.toMatchObject({
    code: 'ENOENT',
  });
  const report = await validateAgentPlugin(root);
  expect(report.status).toBe('PASS');
  expect(report.skills).toHaveLength(22);
});

async function registeredPluginSkills() {
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
  return z
    .array(
      z.object({ description: z.string(), name: z.string(), path: z.string() }).strict(),
    )
    .parse(JSON.parse(stdout));
}

async function canonicalPluginSkills() {
  const entries = await readdir(resolve(root, 'skills'), { withFileTypes: true });
  const names = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
  return Promise.all(
    names.map(async (name) => {
      const path = resolve(root, 'skills', name, 'SKILL.md');
      const frontmatter = parse((await readFile(path, 'utf8')).split('---', 3)[1] ?? '');
      return { description: z.string().parse(frontmatter.description), name, path };
    }),
  );
}

test('the repository-root Python plugin registers every canonical skill', async () => {
  expect(await registeredPluginSkills()).toEqual(await canonicalPluginSkills());
});

test('the Python plugin derives its inventory from canonical skill files', async () => {
  const source = await readFile(resolve(root, '__init__.py'), 'utf8');

  expect(source).not.toContain('_SKILLS =');
  expect(source).not.toContain('"always-current-datetime"');
  expect(source).toContain('glob("*/SKILL.md")');
});

test('integration checks do not leave Python bytecode in the repository', async () => {
  const cache = resolve(root, '__pycache__');
  await rm(cache, { force: true, recursive: true });
  const report = await checkIntegrations(root);
  expect(report.status).toBe('PASS');
  expect(report.checks.map((entry) => entry.id)).toEqual([
    'agent-plugins-v1',
    'aider-catalog',
    'claude-plugin',
    'codex-plugin',
    'continue-adapter',
    'cursor-plugin',
    'gemini-extension',
    'hermes-plugin',
    'openclaw-plugin',
    'opencode-config',
    'required-paths',
    'shared-mcp-config',
    'skills-hub-catalog',
  ]);
  await expect(access(cache)).rejects.toMatchObject({ code: 'ENOENT' });
});
