import { createHash } from 'node:crypto';
import { lstat, readFile, readdir, realpath } from 'node:fs/promises';
import { join, posix, resolve, sep } from 'node:path';

import { z } from 'zod';

const sha256 = z.string().regex(/^[a-f0-9]{64}$/);

const sourceManifestSchema = z
  .object({
    evidence_packet_sha256: sha256,
    files: z
      .array(
        z
          .object({
            bytes: z.number().int().positive(),
            location_kind: z.enum(['archive', 'evidence', 'repository']),
            location_path: z.string().min(1),
            sha256,
            source_path: z.string().min(1),
          })
          .strict(),
      )
      .min(1),
    native_manifest_sha256: sha256,
    schema: z.literal('source-evidence/v1'),
    skill: z.string().min(1),
    source_kind: z.enum(['archived_source', 'repository_baseline']),
  })
  .strict();

type SourceClaim = { path: string; sha256: string };
type PublicClaim = { path: string; source_paths: string[] };
type ManifestFile = z.infer<typeof sourceManifestSchema>['files'][number];

const sourceArchiveSchema = z
  .object({
    files: z
      .array(
        z
          .object({
            base64: z.string().min(1),
            bytes: z.number().int().positive(),
            path: z.string().min(1),
            sha256,
          })
          .strict(),
      )
      .min(1),
    schema: z.literal('source-archive/v1'),
    skill: z.string().min(1),
  })
  .strict();

export interface SourceEvidenceInput {
  nativeManifestSha256: string;
  publicFiles: PublicClaim[];
  sourceFiles: SourceClaim[];
}

function digest(data: Buffer | string): string {
  return createHash('sha256').update(data).digest('hex');
}

function comparePath(left: { path: string }, right: { path: string }): number {
  return left.path < right.path ? -1 : left.path > right.path ? 1 : 0;
}

function canonicalPacketDigest(files: SourceClaim[]): string {
  return digest(files.map((entry) => `${entry.path}\0${entry.sha256}\n`).join(''));
}

function inside(root: string, candidate: string): boolean {
  return candidate === root || candidate.startsWith(root + sep);
}

async function repositoryFiles(directory: string, prefix = ''): Promise<string[]> {
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

async function readBoundFile(root: string, path: string): Promise<Buffer> {
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

async function readArchiveEntry(
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

export async function validateSourceEvidence(
  root: string,
  skillName: string,
  input: SourceEvidenceInput,
): Promise<string[]> {
  const errors: string[] = [];
  const portRoot = join(root, 'evidence', 'ports', skillName);
  let manifest: z.infer<typeof sourceManifestSchema>;
  try {
    manifest = sourceManifestSchema.parse(
      JSON.parse(await readFile(join(portRoot, 'source-manifest.json'), 'utf8')),
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return [`missing or invalid source evidence manifest: ${message}`];
  }
  if (manifest.skill !== skillName) errors.push('source evidence skill name differs');
  if (manifest.native_manifest_sha256 !== input.nativeManifestSha256) {
    errors.push('source evidence manifest hash does not match lineage');
  }
  const expected = [...input.sourceFiles].sort(comparePath);
  const actual = manifest.files
    .map((entry) => ({ path: entry.source_path, sha256: entry.sha256 }))
    .sort(comparePath);
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    errors.push('source evidence files do not match lineage claims');
  }
  if (
    manifest.evidence_packet_sha256 !== input.nativeManifestSha256 &&
    manifest.evidence_packet_sha256 !== canonicalPacketDigest(expected)
  ) {
    errors.push('source evidence packet digest differs');
  }
  for (const entry of manifest.files) {
    try {
      const data =
        entry.location_kind === 'archive'
          ? await readArchiveEntry(portRoot, skillName, entry)
          : await readBoundFile(
              entry.location_kind === 'evidence' ? portRoot : root,
              entry.location_path,
            );
      if (data.length !== entry.bytes) {
        errors.push(`source evidence byte count differs for ${entry.source_path}`);
      }
      if (digest(data) !== entry.sha256) {
        errors.push(`source evidence bytes differ for ${entry.source_path}`);
      }
    } catch (error) {
      errors.push(error instanceof Error ? error.message : String(error));
    }
  }
  const skillDir = join(root, 'skills', skillName);
  const publicActual = (await repositoryFiles(skillDir)).filter(
    (path) => path !== 'evals/source-lineage.json',
  );
  const publicClaimed = input.publicFiles.map((entry) => entry.path).sort();
  if (JSON.stringify(publicActual) !== JSON.stringify(publicClaimed)) {
    errors.push('public file inventory does not match lineage');
  }
  const allowedSources = new Set([
    ...input.sourceFiles.map((entry) => entry.path),
    'target-scaffolding',
  ]);
  for (const entry of input.publicFiles) {
    for (const sourcePath of entry.source_paths) {
      if (!allowedSources.has(sourcePath)) {
        errors.push(`public lineage references an unknown source path: ${sourcePath}`);
      }
    }
  }
  return errors;
}
