import { execFile } from 'node:child_process';
import { copyFile, mkdir, readFile, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { afterEach, expect, test } from 'vitest';

import { buildMcp } from '../../scripts/build-mcp.js';
import { loadCatalog } from '../../src/catalog.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const run = promisify(execFile);
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
    const catalog = await loadCatalog(root);
    expect(resources.resources.map((resource) => resource.uri)).toEqual(
      catalog.map((entry) => `skill://${entry.name}/SKILL.md`),
    );
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

test('keeps dependency debug output off the MCP stdout channel', async () => {
  await buildMcp({ outfile: outputFile, root });
  const transport = new StdioClientTransport({
    args: [outputFile],
    command: process.execPath,
    cwd: root,
    env: { LOG_STREAM: '1', LOG_TOKENS: '1' },
    stderr: 'pipe',
  });
  const client = new Client({ name: 'stdio-debug-smoke', version: '0.1.0' });

  try {
    await client.connect(transport);
    const tools = await client.listTools();
    expect(tools.tools).toHaveLength(6);
  } finally {
    await client.close();
  }
});

test('keeps startup diagnostics off the protocol channel', async () => {
  await buildMcp({ outfile: outputFile, root });
  const brokenRoot = join(outputDirectory, 'missing-skills');
  const brokenBundle = join(brokenRoot, 'mcp', 'dist', 'server.mjs');
  await mkdir(dirname(brokenBundle), { recursive: true });
  await copyFile(outputFile, brokenBundle);

  try {
    await run(process.execPath, [brokenBundle], { cwd: brokenRoot });
    throw new Error('broken MCP startup unexpectedly succeeded');
  } catch (error) {
    const result = error as { stderr?: string; stdout?: string };
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain('mcp startup failed:');
  }
});
