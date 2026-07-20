import { z } from 'zod';

const approvalSchema = z
  .object({
    approved_at: z.string().datetime({ offset: true }),
    approved_by: z.literal('user'),
    cap_usd: z.number().positive(),
    manifest_sha256: z.string().regex(/^[a-f0-9]{64}$/),
    schema_version: z.literal(1),
    unknown_price_cap_usd: z.number().nonnegative(),
  })
  .strict();

export type SweepApproval = z.infer<typeof approvalSchema>;

export interface ApprovalBinding {
  capUsd: number;
  manifestSha256: string;
  unknownPriceCapUsd: number;
}

export function parseSweepApproval(input: unknown): SweepApproval {
  return approvalSchema.parse(input);
}

export function verifySweepApproval(
  approval: SweepApproval,
  binding: ApprovalBinding,
): void {
  if (approval.manifest_sha256 !== binding.manifestSha256) {
    throw new Error('approval manifest mismatch');
  }
  if (approval.cap_usd !== binding.capUsd) throw new Error('approval cap mismatch');
  if (approval.unknown_price_cap_usd !== binding.unknownPriceCapUsd) {
    throw new Error('approval unknown-price cap mismatch');
  }
}
