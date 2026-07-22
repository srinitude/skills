import { rm } from 'node:fs/promises';
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
      'skill://skill-factory/SKILL.md',
      'skill://starting-point/SKILL.md',
    ]);
  } finally {
    await client.close();
  }
});
