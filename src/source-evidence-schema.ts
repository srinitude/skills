import { z } from 'zod';

const sha256 = z.string().regex(/^[a-f0-9]{64}$/);

export const sourceManifestSchema = z
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
    source_kind: z.enum([
      'archived_source',
      'repository_baseline',
      'hybrid_archived_and_repository_baseline',
    ]),
  })
  .strict();

export const sourceArchiveSchema = z
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

export type SourceManifest = z.infer<typeof sourceManifestSchema>;
export type ManifestFile = SourceManifest['files'][number];
export type SourceClaim = { path: string; sha256: string };
export type PublicClaim = { path: string; source_paths: string[] };

export interface SourceEvidenceInput {
  nativeManifestSha256: string;
  publicFiles: PublicClaim[];
  sourceFiles: SourceClaim[];
}
