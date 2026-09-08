import { z } from 'zod';

const digest = z.string().regex(/^[a-f0-9]{64}$/);
const scope = z.enum(['user', 'project']);
const baseline = z.record(z.string().min(1), digest);

export const derivationSchema = z
  .object({
    schema_version: z.literal(1),
    source: z
      .object({
        identity: z.string().min(1),
        scope,
        version: z.string().min(1),
        digest,
        baseline,
      })
      .strict(),
    target_scope: scope,
    target_project: z.string().min(1).nullable(),
    adaptations: z.array(z.string().min(1)).min(1),
    requirements: z.array(z.string().min(1)).min(1),
    compatibility: z.string().min(1),
    plan_digest: digest,
    candidate_digest: digest,
    target_baseline: baseline,
  })
  .strict()
  .superRefine((record, context) => {
    if (record.source.scope === record.target_scope) {
      context.addIssue({ code: 'custom', message: 'variant scopes must differ' });
    }
    if ((record.target_scope === 'project') !== (record.target_project !== null)) {
      context.addIssue({
        code: 'custom',
        message: 'only a project variant binds a target project',
      });
    }
  });
