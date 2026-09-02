import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

type Document = Record<string, Record<string, Record<string, unknown>>>;

export interface McpConfig {
  args: string[];
  command: string;
  cwd: string;
  id: string;
}

export interface McpProbe {
  annotationsValid: boolean;
  resourceCount: number;
  resources: McpResourceProof[];
  toolNames: string[];
}

export interface McpResourceProof {
  description?: string;
  mimeType?: string;
  text: string;
  title?: string;
  uri: string;
}

async function json(root: string, path: string): Promise<Document> {
  return JSON.parse(await readFile(join(root, path), 'utf8')) as Document;
}

function expand(value: string, root: string): string {
  return value
    .replaceAll('${PLUGIN_ROOT}', root)
    .replaceAll('${CLAUDE_PLUGIN_ROOT}', root)
    .replaceAll('${extensionPath}', root);
}

function entry(document: Document, section: string, name: string): Record<string, unknown> {
  const value = document[section]?.[name];
  if (!value) throw new Error(`missing ${section}.${name}`);
  return value;
}

function normalConfig(id: string, value: Record<string, unknown>, root: string): McpConfig {
  return {
    args: (value.args as string[]).map((item) => expand(item, root)),
    command: value.command as string,
    cwd: expand((value.cwd as string | undefined) ?? root, root),
    id,
  };
}

export async function loadMcpConfigs(root: string): Promise<McpConfig[]> {
  const portable = await json(root, 'mcp.json');
  const shared = await json(root, '.mcp.json');
  const gemini = await json(root, 'gemini-extension.json');
  const opencode = await json(root, 'opencode.json');
  const open = entry(opencode, 'mcp', 'srinitude-skills');
  const command = open.command as string[];
  return [
    normalConfig(
      'agent-plugins-v1',
      entry(portable, 'mcpServers', 'srinitude-skills'),
      root,
    ),
    normalConfig(
      'claude-codex-shared',
      entry(shared, 'mcpServers', 'srinitude-skills'),
      root,
    ),
    normalConfig('gemini-extension', entry(gemini, 'mcpServers', 'srinitude-skills'), root),
    normalConfig(
      'opencode',
      { ...open, args: command.slice(1), command: command[0] },
      root,
    ),
  ];
}

function annotationsValid(tool: { annotations?: Record<string, unknown> }): boolean {
  return (
    tool.annotations?.readOnlyHint === true &&
    tool.annotations.destructiveHint === false &&
    tool.annotations.idempotentHint === true &&
    tool.annotations.openWorldHint === false
  );
}

async function callEveryTool(client: Client): Promise<void> {
  const calls = [
    client.callTool({ name: 'list_skills' }),
    client.callTool({ arguments: { query: 'skill' }, name: 'search_skills' }),
    client.callTool({ arguments: { name: 'starting-point' }, name: 'get_skill' }),
    client.callTool({
      arguments: { reference: 'core-loop.md', skill: 'starting-point' },
      name: 'get_reference',
    }),
    client.callTool({
      arguments: { skill: 'starting-point' },
      name: 'get_eval_manifest',
    }),
    client.callTool({ arguments: { name: 'starting-point' }, name: 'validate_skill' }),
  ];
  const results = await Promise.all(calls);
  if (results.some((result) => result.isError)) {
    throw new Error('an MCP tool returned an error during the archive probe');
  }
}

async function resourceProof(
  client: Client,
  resource: { description?: string; mimeType?: string; title?: string; uri: string },
): Promise<McpResourceProof> {
  const result = await client.readResource({ uri: resource.uri });
  const content = result.contents.find((item) => 'text' in item);
  if (!content || typeof content.text !== 'string') {
    throw new Error(`resource has no text content: ${resource.uri}`);
  }
  return { ...resource, text: content.text };
}

export async function probeMcp(config: McpConfig): Promise<McpProbe> {
  const transport = new StdioClientTransport({ ...config, stderr: 'pipe' });
  const client = new Client({ name: `probe-${config.id}`, version: '0.1.0' });
  try {
    await client.connect(transport);
    const tools = await client.listTools();
    const resources = await client.listResources();
    const proofs = await Promise.all(
      resources.resources.map((resource) => resourceProof(client, resource)),
    );
    await callEveryTool(client);
    return {
      annotationsValid: tools.tools.every(annotationsValid),
      resourceCount: resources.resources.length,
      resources: proofs,
      toolNames: tools.tools.map((tool) => tool.name).sort(),
    };
  } finally {
    await client.close();
  }
}
