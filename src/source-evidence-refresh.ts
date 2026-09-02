import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

import { z } from 'zod';

import { canonicalPacketDigest, digest, readBoundFile } from './source-evidence-files.js';

const sha256 = z.string().regex(/^[a-f0-9]{64}$/);
const lineageSchema = z.object({
  native_manifest_sha256: sha256,
  source_files: z.array(z.object({ path: z.string().min(1), sha256 }).strict()).min(1),
});

export interface RefreshResult {
  files: number;
  path: string;
}

async function assertRepositoryBaseline(path: string): Promise<void> {
  try {
    const current = JSON.parse(await readFile(path, 'utf8')) as { source_kind?: unknown };
    if (current.source_kind !== 'repository_baseline') {
      throw new Error('existing source evidence is not a repository baseline');
    }
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
  }
}

async function evidenceFile(
  root: string,
  skill: string,
  claim: { path: string; sha256: string },
) {
  const locationPath = `skills/${skill}/${claim.path}`;
  const data = await readBoundFile(root, locationPath);
  if (digest(data) !== claim.sha256) throw new Error(`source hash differs: ${claim.path}`);
  return {
    bytes: data.length,
    location_kind: 'repository' as const,
    location_path: locationPath,
    sha256: claim.sha256,
    source_path: claim.path,
  };
}

export async function refreshRepositoryBaseline(
  root: string,
  skill: string,
): Promise<RefreshResult> {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(skill)) throw new Error('invalid skill name');
  const lineagePath = join(root, 'skills', skill, 'evals', 'source-lineage.json');
  const lineage = lineageSchema.parse(JSON.parse(await readFile(lineagePath, 'utf8')));
  const target = join(root, 'evidence', 'ports', skill, 'source-manifest.json');
  await assertRepositoryBaseline(target);
  const files = await Promise.all(
    lineage.source_files.map((claim) => evidenceFile(root, skill, claim)),
  );
  const packet = canonicalPacketDigest(lineage.source_files);
  const document = {
    schema: 'source-evidence/v1',
    skill,
    source_kind: 'repository_baseline',
    native_manifest_sha256: lineage.native_manifest_sha256,
    evidence_packet_sha256: packet,
    files,
  };
  await mkdir(dirname(target), { recursive: true });
  const temporary = `${target}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(document, null, 2)}\n`);
  await rename(temporary, target);
  return { files: files.length, path: target };
}
