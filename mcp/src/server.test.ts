import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { afterEach, expect, test } from 'vitest';
import { z } from 'zod';

import { createSkillServer } from './server.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const cleanup: Array<() => Promise<void>> = [];

afterEach(async () => {
  await Promise.all(cleanup.splice(0).map((close) => close()));
});

const toolResultSchema = z
  .object({
    content: z.array(
      z.object({ text: z.string().optional(), type: z.string() }).passthrough(),
    ),
  })
  .passthrough();

function text(result: unknown): string {
  const parsed = toolResultSchema.parse(result);
  const value = parsed.content.find((item) => item.type === 'text')?.text;
  if (value === undefined) throw new Error('tool response has no text content');
  return value;
}

async function connectedClient() {
  const server = await createSkillServer(root);
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client(
    { name: 'skills-test', version: '0.1.0' },
    { capabilities: {} },
  );
  await server.connect(serverTransport);
  await client.connect(clientTransport);
  cleanup.push(async () => {
    await client.close();
    await server.close();
  });
  return client;
}

test('exposes canonical skill bytes as a fixed read-only resource', async () => {
  const client = await connectedClient();
  const resources = await client.listResources();
  expect(resources.resources.map((resource) => resource.uri)).toEqual([
    'skill://starting-point/SKILL.md',
  ]);

  const result = await client.readResource({ uri: 'skill://starting-point/SKILL.md' });
  const expected = await readFile(
    join(root, 'skills', 'starting-point', 'SKILL.md'),
    'utf8',
  );
  expect(result.contents).toEqual([
    {
      mimeType: 'text/markdown',
      text: expected,
      uri: 'skill://starting-point/SKILL.md',
    },
  ]);
});

test('exposes only the approved read-only tools', async () => {
  const client = await connectedClient();
  const tools = await client.listTools();
  expect(tools.tools.map((tool) => tool.name).sort()).toEqual([
    'get_eval_manifest',
    'get_reference',
    'get_skill',
    'list_skills',
    'search_skills',
    'validate_skill',
  ]);
  expect(tools.tools.every((tool) => tool.annotations?.readOnlyHint === true)).toBe(true);

  const listed = await client.callTool({ name: 'list_skills' });
  expect(JSON.parse(text(listed))).toMatchObject({ skills: [{ name: 'starting-point' }] });

  const searched = await client.callTool({
    arguments: { query: 'outcome hidden' },
    name: 'search_skills',
  });
  expect(JSON.parse(text(searched))).toMatchObject({
    skills: [{ name: 'starting-point' }],
  });

  const read = await client.callTool({
    arguments: { name: 'starting-point' },
    name: 'get_skill',
  });
  expect(text(read)).toContain('# Starting point');

  const reference = await client.callTool({
    arguments: { reference: 'core-loop.md', skill: 'starting-point' },
    name: 'get_reference',
  });
  expect(text(reference)).toContain('# Bounded path check');

  const manifest = await client.callTool({
    arguments: { skill: 'starting-point' },
    name: 'get_eval_manifest',
  });
  expect(JSON.parse(text(manifest))).toMatchObject({ skill: 'starting-point' });

  const validated = await client.callTool({
    arguments: { name: 'starting-point' },
    name: 'validate_skill',
  });
  expect(JSON.parse(text(validated))).toMatchObject({ status: 'PASS' });
});

test('returns a stable tool error for a traversal attempt', async () => {
  const client = await connectedClient();
  const result = await client.callTool({
    arguments: { reference: '../LICENSE', skill: 'starting-point' },
    name: 'get_reference',
  });

  expect(result.isError).toBe(true);
  expect(JSON.parse(text(result))).toEqual({
    code: 'PATH_TRAVERSAL',
    message: 'path traversal is forbidden',
  });
});
