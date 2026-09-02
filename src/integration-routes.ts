import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { isDeepStrictEqual } from 'node:util';

import { parse } from 'yaml';

import { loadCatalog } from './catalog.js';

export interface RouteAction {
  action: () => Promise<void>;
  id: string;
}

async function json(root: string, path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(resolve(root, path), 'utf8')) as Record<string, unknown>;
}

function same(actual: unknown, expected: unknown, label: string): void {
  if (!isDeepStrictEqual(actual, expected)) {
    throw new Error(`${label} differs from its canonical route`);
  }
}

async function aider(root: string, paths: string[]): Promise<void> {
  const source = parse(await readFile(resolve(root, '.aider.conf.yml'), 'utf8')) as {
    read?: string[];
  };
  same(source.read, paths, 'Aider inventory');
}

async function plugin(root: string, directory: string): Promise<void> {
  const manifest = await json(root, `${directory}/plugin.json`);
  same(manifest.skills, './skills/', `${directory} skill path`);
  same(manifest.mcpServers, './.mcp.json', `${directory} MCP path`);
}

async function continueAdapter(root: string): Promise<void> {
  const source = await readFile(resolve(root, 'adapters/continue/README.md'), 'utf8');
  if (!source.includes('npx skills add srinitude/skills')) {
    throw new Error('Continue canonical install route is missing');
  }
}

async function cursor(root: string): Promise<void> {
  const manifest = await json(root, '.cursor-plugin/plugin.json');
  if (manifest.skills !== undefined || manifest.mcpServers !== undefined) {
    throw new Error('Cursor automatic discovery has a duplicate path owner');
  }
}

async function gemini(root: string): Promise<void> {
  const manifest = await json(root, 'gemini-extension.json');
  same(
    manifest.mcpServers,
    {
      'srinitude-skills': {
        args: ['${extensionPath}/mcp/dist/server.mjs'],
        command: 'node',
        cwd: '${extensionPath}',
      },
    },
    'Gemini MCP config',
  );
}

async function openclaw(root: string): Promise<void> {
  await plugin(root, '.codex-plugin');
}

async function opencode(root: string): Promise<void> {
  const manifest = (await json(root, 'opencode.json')) as {
    mcp?: Record<string, unknown>;
  };
  same(
    manifest.mcp?.['srinitude-skills'],
    {
      command: ['node', 'mcp/dist/server.mjs'],
      cwd: '.',
      enabled: true,
      type: 'local',
    },
    'opencode MCP config',
  );
}

async function sharedMcp(root: string): Promise<void> {
  const manifest = await json(root, '.mcp.json');
  same(
    manifest,
    {
      mcpServers: {
        'srinitude-skills': {
          args: ['${CLAUDE_PLUGIN_ROOT}/mcp/dist/server.mjs'],
          command: 'node',
        },
      },
    },
    'shared MCP config',
  );
}

async function skillsHub(root: string, names: string[]): Promise<void> {
  const manifest = (await json(root, 'skills.sh.json')) as {
    groupings?: Array<{ skills?: string[] }>;
  };
  const grouped = (manifest.groupings ?? []).flatMap((group) => group.skills ?? []).sort();
  same(grouped, names, 'skills.sh inventory');
}

export async function routeActions(root: string): Promise<RouteAction[]> {
  const catalog = await loadCatalog(root);
  const names = catalog.map((entry) => entry.name);
  const paths = catalog.map((entry) => entry.path);
  return [
    { action: () => aider(root, paths), id: 'aider-catalog' },
    { action: () => plugin(root, '.claude-plugin'), id: 'claude-plugin' },
    { action: () => plugin(root, '.codex-plugin'), id: 'codex-plugin' },
    { action: () => continueAdapter(root), id: 'continue-adapter' },
    { action: () => cursor(root), id: 'cursor-plugin' },
    { action: () => gemini(root), id: 'gemini-extension' },
    { action: () => openclaw(root), id: 'openclaw-plugin' },
    { action: () => opencode(root), id: 'opencode-config' },
    { action: () => sharedMcp(root), id: 'shared-mcp-config' },
    { action: () => skillsHub(root, names), id: 'skills-hub-catalog' },
  ];
}
