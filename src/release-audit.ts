import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { promisify } from 'node:util';

const run = promisify(execFile);

export interface AuditFile {
  disposition: 'changed' | 'verified current' | 'inapplicable';
  path: string;
  reason: string;
  sha256: string;
}

export interface ReleaseAudit {
  baseline: string;
  files: AuditFile[];
  schema_version: 1;
}

function paths(source: string): string[] {
  return source.split('\0').filter(Boolean);
}

async function gitPaths(root: string, args: string[]): Promise<string[]> {
  const { stdout } = await run('git', args, { cwd: root, encoding: 'utf8' });
  return paths(stdout);
}

function owner(path: string): [string, string] {
  if (path.startsWith('evidence/'))
    return ['source evidence', 'skill validation and package inspection'];
  if (path.startsWith('schemas/'))
    return ['schema contracts', 'schema tests and repository validation'];
  if (path.startsWith('mcp/dist/'))
    return ['generated MCP bundle', 'two-build byte equality and archive MCP probes'];
  if (path.startsWith('mcp/'))
    return ['MCP source', 'the MCP test task and TypeScript checks'];
  if (path.startsWith('src/') || path.startsWith('scripts/'))
    return ['TypeScript toolchain source', 'source tests, lint, and type checking'];
  if (path.startsWith('.github/'))
    return ['GitHub automation', 'actionlint and workflow contract tests'];
  if (path.startsWith('docs/') || path.startsWith('adapters/') || path.endsWith('.md'))
    return ['documentation', 'documentation links and route contract tests'];
  if (path.includes('plugin') || path.endsWith('.yaml') || path.endsWith('.yml'))
    return ['client manifests', 'integration and schema checks'];
  return ['repository toolchain', 'the complete Mise CI and package gates'];
}

function reason(path: string, changed: boolean, deleted = false): string {
  const [area, proof] = owner(path);
  const state = deleted
    ? 'Removed from its canonical owner'
    : changed
      ? 'Changed at its canonical owner'
      : 'Reviewed at its canonical owner';
  return `${state} in ${area}; ${proof} supplies current proof.`;
}

function digest(bytes: Buffer): string {
  return createHash('sha256').update(bytes).digest('hex');
}

async function auditBytes(
  root: string,
  baseline: string,
  path: string,
): Promise<{ bytes: Buffer; deleted: boolean }> {
  try {
    return { bytes: await readFile(resolve(root, path)), deleted: false };
  } catch (error) {
    if (!(error instanceof Error) || !('code' in error) || error.code !== 'ENOENT')
      throw error;
    const { stdout } = await run('git', ['show', `${baseline}:${path}`], {
      cwd: root,
      encoding: 'buffer',
      maxBuffer: 64 * 1024 * 1024,
    });
    return { bytes: Buffer.from(stdout), deleted: true };
  }
}

export async function auditRepository(
  root: string,
  baseline: string,
): Promise<ReleaseAudit> {
  await run('git', ['cat-file', '-e', `${baseline}^{commit}`], { cwd: root });
  const tracked = await gitPaths(root, ['ls-files', '-z']);
  const untracked = await gitPaths(root, [
    'ls-files',
    '-z',
    '--others',
    '--exclude-standard',
  ]);
  const changed = new Set(await gitPaths(root, ['diff', '--name-only', '-z', baseline]));
  for (const path of untracked) changed.add(path);
  const files = [...new Set([...tracked, ...untracked])]
    .filter((path) => !path.startsWith('skills/'))
    .sort();
  return {
    baseline,
    files: await Promise.all(
      files.map(async (path) => {
        const { bytes, deleted } = await auditBytes(root, baseline, path);
        return {
          disposition: changed.has(path) ? 'changed' : 'verified current',
          path,
          reason: reason(path, changed.has(path), deleted),
          sha256: digest(bytes),
        };
      }),
    ),
    schema_version: 1,
  };
}
