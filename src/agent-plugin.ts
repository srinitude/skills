import { lstat, readdir, realpath } from 'node:fs/promises';
import { isAbsolute, relative, resolve } from 'node:path';

import {
  addFinding,
  type AgentPluginFinding,
  readAgentPluginJson,
  validateAgentPluginDocuments,
} from './agent-plugin-schema.js';

export interface AgentPluginReport {
  findings: AgentPluginFinding[];
  schema_version: '1.0.0';
  servers: string[];
  skills: string[];
  status: 'FAIL' | 'PASS';
}

const portableDocuments = [
  'plugin.json',
  'mcp.json',
  'evidence/agent-plugins-v1.json',
  'schemas/agent-plugins/1.0.0/plugin.schema.json',
  'schemas/agent-plugins/1.0.0/mcp.schema.json',
] as const;

function object(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function inside(parent: string, child: string): boolean {
  const path = relative(parent, child);
  return path === '' || (!path.startsWith('..') && !isAbsolute(path));
}

async function confined(
  realRoot: string,
  path: string,
  findings: AgentPluginFinding[],
): Promise<boolean> {
  try {
    const target = await realpath(path);
    if (inside(realRoot, target)) return true;
    addFinding(
      findings,
      'PATH_ESCAPE',
      path,
      `resolved path escapes plugin root: ${target}`,
    );
  } catch (error) {
    addFinding(
      findings,
      'PATH_MISSING',
      path,
      error instanceof Error ? error.message : String(error),
    );
  }
  return false;
}

async function discoverSkills(
  root: string,
  realRoot: string,
  findings: AgentPluginFinding[],
): Promise<string[]> {
  const skillsRoot = resolve(root, 'skills');
  if (!(await confined(realRoot, skillsRoot, findings))) return [];
  const entries = await readdir(skillsRoot, { withFileTypes: true });
  const skills: string[] = [];
  for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
    if (!entry.isDirectory()) continue;
    const document = resolve(skillsRoot, entry.name, 'SKILL.md');
    try {
      if (!(await lstat(document)).isFile())
        throw new Error('SKILL.md is not a regular file');
      if (await confined(realRoot, document, findings)) skills.push(entry.name);
    } catch (error) {
      addFinding(
        findings,
        'SKILL_DOCUMENT_MISSING',
        relative(root, document),
        error instanceof Error ? error.message : String(error),
      );
    }
  }
  return skills;
}

function serverRows(document: unknown): Array<[string, Record<string, unknown>]> {
  if (!object(document) || !object(document.mcpServers)) return [];
  return Object.entries(document.mcpServers).filter(
    (row): row is [string, Record<string, unknown>] => object(row[1]),
  );
}

function pluginRootPath(root: string, value: string): string | undefined {
  if (value === '${PLUGIN_ROOT}') return root;
  if (value.startsWith('${PLUGIN_ROOT}/'))
    return resolve(root, value.slice('${PLUGIN_ROOT}/'.length));
  if (value.startsWith('./')) return resolve(root, value);
  return undefined;
}

async function validateServerPaths(
  root: string,
  realRoot: string,
  document: unknown,
  findings: AgentPluginFinding[],
): Promise<string[]> {
  const rows = serverRows(document);
  for (const [name, server] of rows) {
    if (server.type !== 'stdio' || !Array.isArray(server.args)) continue;
    if (typeof server.cwd === 'string') {
      const cwd = pluginRootPath(root, server.cwd);
      if (cwd) await confined(realRoot, cwd, findings);
      else
        addFinding(
          findings,
          'PATH_ESCAPE',
          `mcp.json#/mcpServers/${name}/cwd`,
          'working directory is not rooted at ${PLUGIN_ROOT}',
        );
    }
    for (const arg of server.args.filter(
      (value): value is string => typeof value === 'string',
    )) {
      const path = pluginRootPath(root, arg);
      if (path) await confined(realRoot, path, findings);
    }
  }
  return rows.map(([name]) => name).sort();
}

export async function validateAgentPlugin(root: string): Promise<AgentPluginReport> {
  const findings: AgentPluginFinding[] = [];
  const realRoot = await realpath(root);
  for (const path of portableDocuments)
    await confined(realRoot, resolve(root, path), findings);
  const plugin = await readAgentPluginJson(root, 'plugin.json', findings);
  const mcp = await readAgentPluginJson(root, 'mcp.json', findings);
  await validateAgentPluginDocuments(root, plugin, mcp, findings);
  const skills = await discoverSkills(root, realRoot, findings);
  const servers = await validateServerPaths(root, realRoot, mcp, findings);
  return {
    findings,
    schema_version: '1.0.0',
    servers,
    skills,
    status: findings.length === 0 ? 'PASS' : 'FAIL',
  };
}
