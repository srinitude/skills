import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import Ajv2020 from 'ajv/dist/2020.js';

const AgentPluginAjv = Ajv2020.default;

export interface AgentPluginFinding {
  code: string;
  message: string;
  path: string;
}

interface SchemaSource {
  path: string;
  sha256: string;
  url: string;
}

const schemaPaths = {
  mcp: 'schemas/agent-plugins/1.0.0/mcp.schema.json',
  plugin: 'schemas/agent-plugins/1.0.0/plugin.schema.json',
} as const;

const schemaUrls = {
  mcp: 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
  plugin: 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
} as const;

function object(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

export function addFinding(
  findings: AgentPluginFinding[],
  code: string,
  path: string,
  message: string,
): void {
  findings.push({ code, message, path });
}

function sha256(bytes: Buffer): string {
  return createHash('sha256').update(bytes).digest('hex');
}

export async function readAgentPluginJson(
  root: string,
  path: string,
  findings: AgentPluginFinding[],
): Promise<unknown> {
  try {
    return JSON.parse(await readFile(resolve(root, path), 'utf8')) as unknown;
  } catch (error) {
    addFinding(
      findings,
      'JSON_READ',
      path,
      error instanceof Error ? error.message : String(error),
    );
    return undefined;
  }
}

function sourceRows(value: unknown): SchemaSource[] {
  if (!object(value) || !Array.isArray(value.sources)) return [];
  return value.sources.filter(
    (row): row is SchemaSource =>
      object(row) &&
      typeof row.path === 'string' &&
      typeof row.sha256 === 'string' &&
      typeof row.url === 'string',
  );
}

async function loadSchema(
  root: string,
  source: SchemaSource | undefined,
  findings: AgentPluginFinding[],
): Promise<Record<string, unknown> | undefined> {
  if (!source) return undefined;
  try {
    const bytes = await readFile(resolve(root, source.path));
    if (sha256(bytes) !== source.sha256)
      addFinding(
        findings,
        'SCHEMA_DIGEST',
        source.path,
        'schema digest does not match source record',
      );
    const schema = JSON.parse(bytes.toString('utf8')) as unknown;
    if (!object(schema)) throw new Error('schema root must be an object');
    return schema;
  } catch (error) {
    addFinding(
      findings,
      'SCHEMA_READ',
      source.path,
      error instanceof Error ? error.message : String(error),
    );
    return undefined;
  }
}

async function schemas(
  root: string,
  findings: AgentPluginFinding[],
): Promise<Record<'mcp' | 'plugin', Record<string, unknown> | undefined>> {
  const record = await readAgentPluginJson(
    root,
    'evidence/agent-plugins-v1.json',
    findings,
  );
  const rows = sourceRows(record);
  const result = {} as Record<'mcp' | 'plugin', Record<string, unknown> | undefined>;
  for (const name of ['mcp', 'plugin'] as const) {
    const source = rows.find(
      (row) => row.path === schemaPaths[name] && row.url === schemaUrls[name],
    );
    if (!source)
      addFinding(
        findings,
        'SCHEMA_SOURCE',
        schemaPaths[name],
        'canonical source is missing',
      );
    result[name] = await loadSchema(root, source, findings);
  }
  return result;
}

function validateDocument(
  code: string,
  path: string,
  schema: Record<string, unknown> | undefined,
  document: unknown,
  findings: AgentPluginFinding[],
): void {
  if (!schema || document === undefined) return;
  const ajv = new AgentPluginAjv({ allErrors: true, strict: true });
  const validate = ajv.compile(schema);
  if (!validate(document))
    addFinding(findings, code, path, ajv.errorsText(validate.errors));
}

export async function validateAgentPluginDocuments(
  root: string,
  plugin: unknown,
  mcp: unknown,
  findings: AgentPluginFinding[],
): Promise<void> {
  const loaded = await schemas(root, findings);
  validateDocument('PLUGIN_SCHEMA', 'plugin.json', loaded.plugin, plugin, findings);
  validateDocument('MCP_SCHEMA', 'mcp.json', loaded.mcp, mcp, findings);
}
