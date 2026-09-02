import { mkdir, mkdtemp, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { afterEach, expect, test } from 'vitest';

import { createSkillServer } from './server.js';

const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const cleanup: Array<() => Promise<void>> = [];

afterEach(async () => {
  await Promise.all(cleanup.splice(0).map((close) => close()));
});

async function connectedClient(serverRoot = root): Promise<Client> {
  const server = await createSkillServer(serverRoot);
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: 'tool-errors', version: '0.1.0' });
  await server.connect(serverTransport);
  await client.connect(clientTransport);
  cleanup.push(async () => {
    await client.close();
    await server.close();
  });
  return client;
}

function resultText(result: Awaited<ReturnType<Client['callTool']>>): string {
  const content = Array.isArray(result.content) ? result.content : [];
  const item = content.find(
    (entry): entry is { text: string; type: 'text' } =>
      typeof entry === 'object' &&
      entry !== null &&
      'type' in entry &&
      entry.type === 'text' &&
      'text' in entry &&
      typeof entry.text === 'string',
  );
  if (!item) throw new Error('tool result has no text');
  return item.text;
}

async function errorPayload(
  client: Client,
  name: string,
  args: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const result = await client.callTool({ arguments: args, name });
  expect(result.isError).toBe(true);
  return JSON.parse(resultText(result)) as Record<string, unknown>;
}

test.each([
  ['get_skill', { name: '../starting-point' }, 'INVALID_SKILL_NAME'],
  ['get_skill', { name: 'missing-skill' }, 'NOT_FOUND'],
  ['get_reference', { reference: '../LICENSE', skill: 'starting-point' }, 'PATH_TRAVERSAL'],
  ['get_reference', { reference: '/etc/passwd', skill: 'starting-point' }, 'ABSOLUTE_PATH'],
  [
    'get_reference',
    { reference: 'nested/file.md', skill: 'starting-point' },
    'INVALID_PATH',
  ],
  [
    'get_reference',
    { reference: 'nested\\file.md', skill: 'starting-point' },
    'INVALID_PATH',
  ],
  [
    'get_reference',
    { reference: './core-loop.md', skill: 'starting-point' },
    'PATH_TRAVERSAL',
  ],
  ['get_reference', { reference: '.hidden', skill: 'starting-point' }, 'HIDDEN_PATH'],
])('returns a stable error for %s %#', async (name, args, code) => {
  const client = await connectedClient();
  await expect(errorPayload(client, name, args)).resolves.toMatchObject({ code });
});

test('rejects malformed tool input through the MCP schema', async () => {
  const client = await connectedClient();
  const result = await client.callTool({
    arguments: { extra: true, name: 'starting-point' },
    name: 'get_skill',
  });

  expect(result.isError).toBe(true);
  expect(resultText(result)).toContain('MCP error -32602');
});

test('rejects a reference symlink that leaves a skill root', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'skills-tool-errors-'));
  cleanup.push(() => rm(fixture, { force: true, recursive: true }));
  const skill = join(fixture, 'skills', 'example');
  await mkdir(join(skill, 'references'), { recursive: true });
  await writeFile(
    join(skill, 'SKILL.md'),
    '---\nname: example\ndescription: Use when testing.\nmetadata:\n  version: 0.1.0\n---\n',
  );
  const outside = join(fixture, 'outside.md');
  await writeFile(outside, '# Outside\n');
  await symlink(outside, join(skill, 'references', 'escape.md'));
  const client = await connectedClient(fixture);

  await expect(
    errorPayload(client, 'get_reference', {
      reference: 'escape.md',
      skill: 'example',
    }),
  ).resolves.toMatchObject({ code: 'SYMLINK_ESCAPE' });
});

test('blocks traversal-shaped validate requests before filesystem access', async () => {
  const client = await connectedClient();
  const result = await client.callTool({
    arguments: { name: '../AGENTS' },
    name: 'validate_skill',
  });

  expect(JSON.parse(resultText(result))).toMatchObject({
    errors: ['skill name is invalid'],
    status: 'BLOCKED',
  });
});
