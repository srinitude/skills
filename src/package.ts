import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { mkdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { promisify } from 'node:util';

import { buildMcp } from '../scripts/build-mcp.js';

const execFileAsync = promisify(execFile);

interface PackOutput {
  filename: string;
}

export interface PackageResult {
  entries: string[];
  mcp_sha256: string;
  sha256: string;
  symlinks: string[];
  tarball: string;
}

function sha256(bytes: Buffer): string {
  return createHash('sha256').update(bytes).digest('hex');
}

function lines(source: string): string[] {
  return source
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

function validateEntries(entries: string[]): void {
  for (const entry of entries) {
    const segments = entry.split('/');
    if (!entry.startsWith('package/') || segments.includes('..')) {
      throw new Error(`unsafe package entry: ${entry}`);
    }
  }
  if (new Set(entries).size !== entries.length)
    throw new Error('duplicate package entries');
}

async function tarEntries(tarball: string): Promise<string[]> {
  const result = await execFileAsync('tar', ['-tf', tarball]);
  const entries = lines(result.stdout).sort();
  validateEntries(entries);
  return entries;
}

async function tarSymlinks(tarball: string): Promise<string[]> {
  const result = await execFileAsync('tar', ['-tvf', tarball]);
  return result.stdout
    .split('\n')
    .filter((line) => line.startsWith('l'))
    .map((line) => line.trim());
}

async function npmPack(root: string, destination: string): Promise<string> {
  const result = await execFileAsync(
    'npm',
    ['pack', '--json', '--pack-destination', destination],
    { cwd: root, env: { ...process.env, NODE_ENV: 'development' } },
  );
  const payload = JSON.parse(result.stdout) as PackOutput[];
  const first = payload[0];
  if (!first?.filename) throw new Error('npm pack did not return a filename');
  return join(destination, first.filename);
}

export async function buildPackage(
  root: string,
  destination: string,
): Promise<PackageResult> {
  await mkdir(destination, { recursive: true });
  const bundle = join(root, 'mcp', 'dist', 'server.mjs');
  await buildMcp({ outfile: bundle, root });
  const mcpHash = sha256(await readFile(bundle));
  const tarball = await npmPack(root, destination);
  return {
    entries: await tarEntries(tarball),
    mcp_sha256: mcpHash,
    sha256: sha256(await readFile(tarball)),
    symlinks: await tarSymlinks(tarball),
    tarball,
  };
}
