import { createHash } from 'node:crypto';
import { lstat, readFile, readdir, realpath } from 'node:fs/promises';
import { join, posix, resolve, sep } from 'node:path';

import {
  sourceArchiveSchema,
  type ManifestFile,
  type PublicClaim,
  type SourceClaim,
} from './source-evidence-schema.js';

export function digest(data: Buffer | string): string {
  return createHash('sha256').update(data).digest('hex');
}

export function comparePath(left: { path: string }, right: { path: string }): number {
  return left.path < right.path ? -1 : left.path > right.path ? 1 : 0;
}

export function canonicalPacketDigest(files: SourceClaim[]): string {
  return digest(files.map((entry) => `${entry.path}\0${entry.sha256}\n`).join(''));
}

function inside(root: string, candidate: string): boolean {
  return candidate === root || candidate.startsWith(root + sep);
}

export async function repositoryFiles(directory: string, prefix = ''): Promise<string[]> {
  const found: string[] = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const relative = prefix ? posix.join(prefix, entry.name) : entry.name;
    if (entry.isDirectory()) {
      found.push(...(await repositoryFiles(join(directory, entry.name), relative)));
    } else if (entry.isFile()) {
      found.push(relative);
    } else {
      throw new Error(`public skill contains a symlink or unsupported entry: ${relative}`);
    }
  }
  return found.sort();
}

export async function readBoundFile(root: string, path: string): Promise<Buffer> {
  const rootAbsolute = resolve(root);
  const absolute = resolve(rootAbsolute, path);
  if (!inside(rootAbsolute, absolute)) {
    throw new Error(`source evidence path escapes root: ${path}`);
  }
  const stat = await lstat(absolute);
  if (!stat.isFile()) throw new Error(`source evidence is not a regular file: ${path}`);
  const rootReal = await realpath(rootAbsolute);
  const fileReal = await realpath(absolute);
  if (!inside(rootReal, fileReal)) {
    throw new Error(`source evidence resolves outside root: ${path}`);
  }
  return readFile(fileReal);
}

export async function readArchiveEntry(
  portRoot: string,
  skillName: string,
  entry: ManifestFile,
): Promise<Buffer> {
  const archiveRaw = await readBoundFile(portRoot, entry.location_path);
  const archive = sourceArchiveSchema.parse(JSON.parse(archiveRaw.toString('utf8')));
  if (archive.skill !== skillName) throw new Error('source archive skill name differs');
  const matches = archive.files.filter((candidate) => candidate.path === entry.source_path);
  if (matches.length !== 1) {
    throw new Error(
      `source archive must contain exactly one entry for ${entry.source_path}`,
    );
  }
  const candidate = matches[0]!;
  const data = Buffer.from(candidate.base64, 'base64');
  if (data.length !== candidate.bytes || digest(data) !== candidate.sha256) {
    throw new Error(`source archive entry is corrupt: ${entry.source_path}`);
  }
  return data;
}

export function validatePublicMappings(
  publicFiles: PublicClaim[],
  sourceFiles: SourceClaim[],
): string[] {
  const allowed = new Set([
    ...sourceFiles.map((entry) => entry.path),
    'target-scaffolding',
  ]);
  return publicFiles.flatMap((entry) =>
    entry.source_paths
      .filter((sourcePath) => !allowed.has(sourcePath))
      .map(
        (sourcePath) => `public lineage references an unknown source path: ${sourcePath}`,
      ),
  );
}
