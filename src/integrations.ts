import { execFile } from 'node:child_process';
import { access, readFile, realpath } from 'node:fs/promises';
import { isAbsolute, relative, resolve } from 'node:path';
import { promisify } from 'node:util';

import { parse } from 'yaml';
import { z } from 'zod';

const run = promisify(execFile);
const clients = [
  'Aider',
  'ChatGPT',
  'Claude Code',
  'Codex',
  'Continue',
  'Cursor',
  'Gemini CLI',
  'Hermes Agent',
  'OpenClaw',
  'opencode',
] as const;

const requiredPaths = [
  '.agents/plugins/marketplace.json',
  '.aider.conf.yml',
  '.claude-plugin/plugin.json',
  '.codex-plugin/plugin.json',
  '.cursor-plugin/plugin.json',
  '.mcp.json',
  'adapters/continue/README.md',
  'gemini-extension.json',
  'mcp/dist/server.mjs',
  'openclaw.plugin.json',
  'opencode.json',
  'plugin.yaml',
  'skills.sh.json',
] as const;

const openClawSchema = z
  .object({
    configSchema: z.object({ type: z.literal('object') }).passthrough(),
    id: z.literal('srinitude-skills'),
    skills: z.array(z.string()).min(1),
  })
  .passthrough();

export interface IntegrationCheck {
  error?: string;
  id: string;
  status: 'FAIL' | 'PASS';
}

export interface IntegrationReport {
  checks: IntegrationCheck[];
  clients: string[];
  status: 'FAIL' | 'PASS';
}

function inside(parent: string, child: string): boolean {
  const path = relative(parent, child);
  return path === '' || (!path.startsWith('..') && !isAbsolute(path));
}

async function check(id: string, action: () => Promise<void>): Promise<IntegrationCheck> {
  try {
    await action();
    return { id, status: 'PASS' };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : String(error),
      id,
      status: 'FAIL',
    };
  }
}

async function checkRequiredPaths(root: string): Promise<void> {
  await Promise.all(requiredPaths.map((path) => access(resolve(root, path))));
  for (const path of requiredPaths.filter((entry) => entry.endsWith('.json'))) {
    JSON.parse(await readFile(resolve(root, path), 'utf8'));
  }
  parse(await readFile(resolve(root, 'plugin.yaml'), 'utf8'));
}

async function checkOpenClaw(root: string): Promise<void> {
  const manifest = openClawSchema.parse(
    JSON.parse(await readFile(resolve(root, 'openclaw.plugin.json'), 'utf8')),
  );
  const realRoot = await realpath(root);
  for (const path of manifest.skills) {
    const target = await realpath(resolve(root, path));
    if (!inside(realRoot, target))
      throw new Error(`OpenClaw skill path escapes root: ${path}`);
  }
}

async function checkPythonPlugin(root: string): Promise<void> {
  const script = [
    'import importlib.util,json,pathlib,sys',
    'root=pathlib.Path(sys.argv[1])',
    'spec=importlib.util.spec_from_file_location("srinitude_skills",root/"__init__.py")',
    'module=importlib.util.module_from_spec(spec)',
    'spec.loader.exec_module(module)',
    'class Context:',
    '  def __init__(self): self.skills=[]',
    '  def register_skill(self,name,path,description=""): self.skills.append({"name":name,"path":str(path)})',
    'ctx=Context()',
    'module.register(ctx)',
    'print(json.dumps(ctx.skills))',
  ].join('\n');
  const result = await run('python3', ['-c', script, root], {
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  const registered = z
    .array(z.object({ name: z.string(), path: z.string() }).strict())
    .parse(JSON.parse(result.stdout));
  if (registered.length === 0) throw new Error('Python plugin registers no skills');
  const realRoot = await realpath(root);
  for (const entry of registered) {
    if (!inside(realRoot, await realpath(entry.path))) {
      throw new Error(`Python plugin path escapes root: ${entry.path}`);
    }
  }
}

export async function checkIntegrations(root: string): Promise<IntegrationReport> {
  const checks = await Promise.all([
    check('required-paths', () => checkRequiredPaths(root)),
    check('openclaw-paths', () => checkOpenClaw(root)),
    check('python-plugin', () => checkPythonPlugin(root)),
  ]);
  return {
    checks,
    clients: [...clients],
    status: checks.every((entry) => entry.status === 'PASS') ? 'PASS' : 'FAIL',
  };
}
