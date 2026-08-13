import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

import {
  canonicalPacketDigest,
  comparePath,
  digest,
  readArchiveEntry,
  readBoundFile,
  repositoryFiles,
  validatePublicMappings,
} from './source-evidence-files.js';
import {
  sourceManifestSchema,
  type SourceEvidenceInput,
  type SourceManifest,
} from './source-evidence-schema.js';

export type { SourceEvidenceInput } from './source-evidence-schema.js';

async function loadManifest(portRoot: string): Promise<SourceManifest> {
  return sourceManifestSchema.parse(
    JSON.parse(await readFile(join(portRoot, 'source-manifest.json'), 'utf8')),
  );
}

function validateManifestIdentity(
  manifest: SourceManifest,
  skillName: string,
  input: SourceEvidenceInput,
): string[] {
  const errors: string[] = [];
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
  return errors;
}

function validateSourceKind(manifest: SourceManifest): string[] {
  const kinds = new Set(manifest.files.map((entry) => entry.location_kind));
  const hasArchivedEvidence = kinds.has('archive') || kinds.has('evidence');
  if (manifest.source_kind === 'archived_source' && kinds.has('repository')) {
    return ['archived source evidence must not use repository locations'];
  }
  if (manifest.source_kind === 'repository_baseline' && kinds.size !== 1) {
    return ['repository baseline evidence must use repository locations only'];
  }
  if (manifest.source_kind === 'repository_baseline' && !kinds.has('repository')) {
    return ['repository baseline evidence must use repository locations only'];
  }
  if (
    manifest.source_kind === 'hybrid_archived_and_repository_baseline' &&
    (!hasArchivedEvidence || !kinds.has('repository'))
  ) {
    return [
      'hybrid source evidence must include archived evidence and repository locations',
    ];
  }
  return [];
}

async function validateManifestFiles(
  root: string,
  portRoot: string,
  skillName: string,
  manifest: SourceManifest,
): Promise<string[]> {
  const errors: string[] = [];
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
  return errors;
}

async function validatePublicInventory(
  root: string,
  skillName: string,
  input: SourceEvidenceInput,
): Promise<string[]> {
  const actual = (await repositoryFiles(join(root, 'skills', skillName))).filter(
    (path) => path !== 'evals/source-lineage.json',
  );
  const claimed = input.publicFiles.map((entry) => entry.path).sort();
  const errors =
    JSON.stringify(actual) === JSON.stringify(claimed)
      ? []
      : ['public file inventory does not match lineage'];
  return [...errors, ...validatePublicMappings(input.publicFiles, input.sourceFiles)];
}

export async function validateSourceEvidence(
  root: string,
  skillName: string,
  input: SourceEvidenceInput,
): Promise<string[]> {
  const portRoot = join(root, 'evidence', 'ports', skillName);
  let manifest: SourceManifest;
  try {
    manifest = await loadManifest(portRoot);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return [`missing or invalid source evidence manifest: ${message}`];
  }
  return [
    ...validateManifestIdentity(manifest, skillName, input),
    ...validateSourceKind(manifest),
    ...(await validateManifestFiles(root, portRoot, skillName, manifest)),
    ...(await validatePublicInventory(root, skillName, input)),
  ];
}
