import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

import { validateAgentPlugin } from './agent-plugin.js';
import { agentRouteProofs } from './client-smoke-agent-routes.js';
import type { SmokeContext } from './client-smoke-types.js';
import { command, isolatedHome, requireText, skillTreeSha } from './client-smoke-utils.js';

async function agentPlugins(context: SmokeContext): Promise<string> {
  const report = await validateAgentPlugin(context.archiveRoot);
  if (report.status !== 'PASS') throw new Error('Agent Plugins validation failed');
  return 'Agent Plugins 1.0.0 schema and confined archive paths passed';
}

async function aider(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-aider');
  const output = await command(
    'uvx',
    [
      '--python',
      '3.12',
      '--from',
      'aider-chat==0.86.2',
      'aider',
      '--no-git',
      '--no-pretty',
      '--no-check-update',
      '--no-show-model-warnings',
      '--yes-always',
      '--show-prompts',
      '--model',
      'openai/gpt-4o-mini',
    ],
    context.archiveRoot,
    home,
  );
  for (const name of context.names) requireText(output, `skills/${name}/SKILL.md`, 'Aider');
  return `Aider loaded ${context.names.length} canonical read-only skill files`;
}

async function continueRoute(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-continue');
  await command(
    'npx',
    [
      '-y',
      'skills@latest',
      'add',
      context.archiveRoot,
      '--agent',
      'continue',
      '--skill',
      '*',
      '--copy',
      '--yes',
    ],
    home,
    home,
  );
  const installed = join(home, '.continue');
  if ((await skillTreeSha(installed, context.names)) !== context.skillsSha256)
    throw new Error('Continue installed skill bytes differ');
  return `Continue installed ${context.names.length} byte-exact canonical skills`;
}

interface CursorReceipt {
  archive_sha256?: string;
  client_version?: string;
  mcp_resource_count?: number;
  mcp_servers?: string[];
  mcp_tools?: string[];
  observed_rules?: number;
  observed_skills?: number;
  skills_sha256?: string;
  status?: string;
}

async function cursor(context: SmokeContext): Promise<string> {
  if (!context.cursorReceipt) throw new Error('current Cursor UI receipt is required');
  const receipt = JSON.parse(
    await readFile(context.cursorReceipt, 'utf8'),
  ) as CursorReceipt;
  if (receipt.status !== 'PASS' || receipt.archive_sha256 !== context.archiveSha256)
    throw new Error('Cursor receipt does not match the accepted archive');
  if (
    receipt.skills_sha256 !== context.skillsSha256 ||
    receipt.observed_skills !== context.names.length
  )
    throw new Error('Cursor receipt does not prove the canonical skill tree');
  const tools = [
    'get_eval_manifest',
    'get_reference',
    'get_skill',
    'list_skills',
    'search_skills',
    'validate_skill',
  ];
  if (
    receipt.observed_rules !== context.names.length ||
    receipt.mcp_resource_count !== context.names.length
  )
    throw new Error('Cursor receipt has incomplete plugin discovery');
  if (JSON.stringify(receipt.mcp_tools) !== JSON.stringify(tools))
    throw new Error('Cursor receipt has the wrong MCP tool surface');
  if (!receipt.mcp_servers?.includes('srinitude-skills') || !receipt.client_version)
    throw new Error('Cursor receipt lacks current MCP and client evidence');
  return `Cursor ${receipt.client_version} visually confirmed ${receipt.observed_skills} skills and MCP`;
}

export const routeProofs: Record<string, (context: SmokeContext) => Promise<string>> = {
  ...agentRouteProofs,
  'agent-plugins-v1': agentPlugins,
  aider,
  'codex-shared-plugin': agentPlugins,
  continue: continueRoute,
  cursor,
};
