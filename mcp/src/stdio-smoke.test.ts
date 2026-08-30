import { readFile, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { afterEach, expect, test } from 'vitest';

import { buildMcp } from '../../scripts/build-mcp.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const outputDirectory = join(root, '.artifacts', 'mcp-test');
const outputFile = join(outputDirectory, 'server.mjs');

afterEach(async () => {
  await rm(outputDirectory, { force: true, recursive: true });
});

test('builds a stdio server that a spawned MCP client can initialize', async () => {
  await buildMcp({ outfile: outputFile, root });
  const transport = new StdioClientTransport({
    args: [outputFile],
    command: process.execPath,
    cwd: root,
    stderr: 'pipe',
  });
  const client = new Client(
    { name: 'stdio-smoke', version: '0.1.0' },
    { capabilities: {} },
  );

  try {
    await client.connect(transport);
    const tools = await client.listTools();
    const resources = await client.listResources();
    expect(tools.tools.map((tool) => tool.name)).toContain('get_skill');
    expect(resources.resources.map((resource) => resource.uri)).toEqual([
      'skill://always-current-datetime/SKILL.md',
      'skill://by-design/SKILL.md',
      'skill://dedupe/SKILL.md',
      'skill://design-like-im-5/SKILL.md',
      'skill://dtcg-tokens/SKILL.md',
      'skill://goal-prompt/SKILL.md',
      'skill://logic-audit/SKILL.md',
      'skill://meaning-preserving-rewrite/SKILL.md',
      'skill://mobile-first-website-design/SKILL.md',
      'skill://only-one-interpretation/SKILL.md',
      'skill://outcome-bounded-work/SKILL.md',
      'skill://prompt-enhancer/SKILL.md',
      'skill://reify/SKILL.md',
      'skill://simplify-skill/SKILL.md',
      'skill://skill-factory/SKILL.md',
      'skill://starting-point/SKILL.md',
      'skill://timebox/SKILL.md',
      'skill://tool-call-configuration-for/SKILL.md',
      'skill://visual-design-system-extractor/SKILL.md',
      'skill://would-agents-actually/SKILL.md',
      'skill://would-humans-actually/SKILL.md',
    ]);
  } finally {
    await client.close();
  }
});

test('starts through the portable Agent Plugins MCP configuration', async () => {
  const config = JSON.parse(await readFile(join(root, 'mcp.json'), 'utf8')) as {
    mcpServers: Record<
      string,
      { args: string[]; command: string; cwd: string; type: string }
    >;
  };
  const server = config.mcpServers['srinitude-skills'];
  expect(server).toBeDefined();
  if (!server) throw new Error('portable MCP server is missing');
  const transport = new StdioClientTransport({
    args: server.args.map((arg) => arg.replace('${PLUGIN_ROOT}', root)),
    command: server.command,
    cwd: server.cwd.replace('${PLUGIN_ROOT}', root),
    stderr: 'pipe',
  });
  const client = new Client(
    { name: 'portable-config-smoke', version: '0.1.0' },
    { capabilities: {} },
  );

  expect(server.type).toBe('stdio');
  try {
    await client.connect(transport);
    const tools = await client.listTools();
    expect(tools.tools.map((tool) => tool.name).sort()).toEqual([
      'get_eval_manifest',
      'get_reference',
      'get_skill',
      'list_skills',
      'search_skills',
      'validate_skill',
    ]);
  } finally {
    await client.close();
  }
});
