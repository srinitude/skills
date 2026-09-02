import { execFile } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { promisify } from 'node:util';

import { loadCatalog } from './catalog.js';
import { routeProofs } from './client-smoke-routes.js';
import type {
  ClientRouteResult,
  ClientRouteSpec,
  ClientSmokeReport,
  SmokeContext,
} from './client-smoke-types.js';
import { skillTreeSha } from './client-smoke-utils.js';
import { buildPackage } from './package.js';

const run = promisify(execFile);

export function clientRouteSpecs(): ClientRouteSpec[] {
  return [
    {
      id: 'agent-plugins-v1',
      route_type: 'portable package',
      mcp: 'required',
      command: 'validate extracted plugin.json and mcp.json',
    },
    {
      id: 'aider',
      route_type: 'read-only context adapter',
      mcp: 'not claimed',
      command: 'uvx aider --show-prompts from extracted archive',
    },
    {
      id: 'claude-code',
      route_type: 'native plugin marketplace',
      mcp: 'required',
      command: 'claude plugin validate, install, and list',
    },
    {
      id: 'codex',
      route_type: 'native plugin marketplace',
      mcp: 'required',
      command: 'npx @openai/codex@latest plugin add and list',
    },
    {
      id: 'codex-shared-plugin',
      route_type: 'shared Agent Plugin',
      mcp: 'required',
      command: 'validate shared plugin.json and mcp.json',
    },
    {
      id: 'continue',
      route_type: 'skills installer',
      mcp: 'not claimed',
      command: 'npx skills@latest add for Continue and compare bytes',
    },
    {
      id: 'cursor',
      route_type: 'local Agent Plugin',
      mcp: 'required',
      command: 'current Cursor local-plugin cold load with visual receipt',
    },
    {
      id: 'gemini-cli',
      route_type: 'native extension',
      mcp: 'required',
      command: 'gemini extensions validate, install, and list',
    },
    {
      id: 'hermes-agent',
      route_type: 'native Python plugin',
      mcp: 'not claimed',
      command: 'hermes plugins doctor --ci on extracted archive',
    },
    {
      id: 'openclaw',
      route_type: 'Codex-compatible bundle',
      mcp: 'required',
      command: 'npx openclaw@latest plugins install and inspect',
    },
    {
      id: 'opencode',
      route_type: 'project config',
      mcp: 'required',
      command: 'npx opencode-ai@latest mcp list from extracted archive',
    },
  ];
}

async function prove(
  spec: ClientRouteSpec,
  context: SmokeContext,
): Promise<ClientRouteResult> {
  try {
    const evidence = await routeProofs[spec.id]!(context);
    return { ...spec, evidence, status: 'PASS' };
  } catch (error) {
    const evidence = error instanceof Error ? error.message : String(error);
    return { ...spec, evidence, status: 'BLOCKED' };
  }
}

export async function smokeClients(
  root: string,
  output: string,
  cursorReceipt?: string,
): Promise<ClientSmokeReport> {
  const temporaryRoot = await mkdtemp(join(tmpdir(), 'skills-clients-'));
  try {
    const built = await buildPackage(root, output);
    await run('tar', ['-xzf', built.tarball, '-C', temporaryRoot]);
    const archiveRoot = join(temporaryRoot, 'package');
    const names = (await loadCatalog(archiveRoot)).map((entry) => entry.name);
    const skillsSha256 = await skillTreeSha(archiveRoot, names);
    const context: SmokeContext = {
      archiveRoot,
      archiveSha256: built.sha256,
      cursorReceipt,
      names,
      skillsSha256,
      tarball: built.tarball,
      temporaryRoot,
    };
    const routes = await Promise.all(
      clientRouteSpecs().map((spec) => prove(spec, context)),
    );
    return {
      archive_sha256: built.sha256,
      routes,
      schema_version: 1,
      skill_count: names.length,
      skills_sha256: skillsSha256,
      status: routes.every((route) => route.status === 'PASS') ? 'PASS' : 'BLOCKED',
    };
  } finally {
    await rm(temporaryRoot, { force: true, recursive: true });
  }
}
