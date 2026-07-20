import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

import { type CatalogEntry } from '../../src/catalog.js';
import { validateSkill } from '../../src/skill-validation.js';
import { PathPolicyError, readSkillFile } from './path-policy.js';

const annotations = {
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
  readOnlyHint: true,
};

function textResult(text: string) {
  return { content: [{ text, type: 'text' as const }] };
}

function jsonResult(value: unknown) {
  return textResult(JSON.stringify(value));
}

function errorResult(error: unknown) {
  const payload =
    error instanceof PathPolicyError
      ? { code: error.code, message: error.message }
      : { code: 'INTERNAL_ERROR', message: 'request failed' };
  return { ...jsonResult(payload), isError: true };
}

async function safeRead(action: () => Promise<string>) {
  try {
    return textResult(await action());
  } catch (error) {
    return errorResult(error);
  }
}

function listedEntry(entry: CatalogEntry) {
  return {
    description: entry.description,
    name: entry.name,
    version: entry.version,
  };
}

function registerList(server: McpServer, catalog: CatalogEntry[]): void {
  server.registerTool(
    'list_skills',
    { annotations, description: 'List canonical skills and their metadata.' },
    async () => jsonResult({ skills: catalog.map(listedEntry) }),
  );
}

function registerSearch(server: McpServer, catalog: CatalogEntry[]): void {
  server.registerTool(
    'search_skills',
    {
      annotations,
      description: 'Search canonical skill names and descriptions.',
      inputSchema: z.object({ query: z.string().min(1) }).strict(),
    },
    async ({ query }) => {
      const terms = query.toLowerCase().trim().split(/\s+/);
      const matches = catalog.filter((entry) => {
        const value = `${entry.name} ${entry.description}`.toLowerCase();
        return terms.every((term) => value.includes(term));
      });
      return jsonResult({ skills: matches.map(listedEntry) });
    },
  );
}

function registerGetSkill(server: McpServer, root: string): void {
  server.registerTool(
    'get_skill',
    {
      annotations,
      description: 'Read one canonical SKILL.md file.',
      inputSchema: z.object({ name: z.string().min(1) }).strict(),
    },
    async ({ name }) => safeRead(() => readSkillFile(root, name, 'SKILL.md')),
  );
}

function referencePath(reference: string): string {
  const portable = reference.replaceAll('\\', '/');
  if (portable.split('/').includes('..')) return `references/${portable}`;
  if (portable.includes('/')) {
    throw new PathPolicyError('INVALID_PATH', 'nested references are forbidden');
  }
  return `references/${portable}`;
}

function registerGetReference(server: McpServer, root: string): void {
  server.registerTool(
    'get_reference',
    {
      annotations,
      description: 'Read one first-level reference from a canonical skill.',
      inputSchema: z
        .object({ reference: z.string().min(1), skill: z.string().min(1) })
        .strict(),
    },
    async ({ reference, skill }) =>
      safeRead(async () => readSkillFile(root, skill, referencePath(reference))),
  );
}

function registerGetManifest(server: McpServer, root: string): void {
  server.registerTool(
    'get_eval_manifest',
    {
      annotations,
      description: 'Read one canonical evaluation manifest.',
      inputSchema: z.object({ skill: z.string().min(1) }).strict(),
    },
    async ({ skill }) => safeRead(() => readSkillFile(root, skill, 'evals/manifest.json')),
  );
}

function registerValidate(server: McpServer, root: string): void {
  server.registerTool(
    'validate_skill',
    {
      annotations,
      description: 'Run deterministic validation for one canonical skill.',
      inputSchema: z.object({ name: z.string().min(1) }).strict(),
    },
    async ({ name }) => jsonResult(await validateSkill(root, name)),
  );
}

export function registerTools(
  server: McpServer,
  root: string,
  catalog: CatalogEntry[],
): void {
  registerGetManifest(server, root);
  registerGetReference(server, root);
  registerGetSkill(server, root);
  registerList(server, catalog);
  registerSearch(server, catalog);
  registerValidate(server, root);
}
