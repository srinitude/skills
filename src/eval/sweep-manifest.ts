import { createHash } from 'node:crypto';

import { z } from 'zod';

const pricingSchema = z
  .object({
    completion_usd_per_token: z.number().nonnegative().nullable(),
    prompt_usd_per_token: z.number().nonnegative().nullable(),
    request_usd: z.number().nonnegative(),
  })
  .strict()
  .superRefine((pricing, context) => {
    const bothKnown =
      pricing.prompt_usd_per_token !== null && pricing.completion_usd_per_token !== null;
    const bothUnknown =
      pricing.prompt_usd_per_token === null && pricing.completion_usd_per_token === null;
    if (!bothKnown && !bothUnknown) {
      context.addIssue({
        code: 'custom',
        message: 'pricing must be wholly known or unknown',
      });
    }
  });

const messageSchema = z
  .object({
    content: z.string().min(1),
    role: z.enum(['assistant', 'system', 'user']),
  })
  .strict();

const requestSchema = z
  .object({
    id: z.string().regex(/^[a-z0-9][a-z0-9._-]*$/),
    kind: z.enum(['candidate', 'judge', 'trigger']),
    max_input_tokens: z.number().int().positive(),
    max_output_tokens: z.number().int().positive(),
    messages: z.array(messageSchema).min(1),
    model: z.string().min(1),
    pricing: pricingSchema,
    provider: z.string().min(1),
    provider_name: z.string().min(1),
    reservation_usd: z.number().nonnegative(),
  })
  .strict();

const manifestSchema = z
  .object({
    requests: z.array(requestSchema).min(1),
    run_id: z.string().regex(/^[a-z0-9][a-z0-9._-]*$/),
    schema_version: z.literal(1),
  })
  .strict()
  .superRefine((manifest, context) => {
    const ids = new Set<string>();
    for (const [index, request] of manifest.requests.entries()) {
      if (ids.has(request.id)) {
        context.addIssue({
          code: 'custom',
          message: `duplicate request id: ${request.id}`,
          path: ['requests', index, 'id'],
        });
      }
      ids.add(request.id);
    }
  });

export type SweepManifest = z.infer<typeof manifestSchema>;
export type SweepRequest = z.infer<typeof requestSchema>;

export interface SweepCaps {
  capUsd: number;
  unknownPriceCapUsd: number;
}

export interface SweepPlan {
  cap_usd: number;
  known_price_requests: number;
  request_count: number;
  reservation_usd: number;
  unknown_price_cap_usd: number;
  unknown_price_requests: number;
  unknown_price_reservation_usd: number;
}

function isKnown(request: SweepRequest): boolean {
  return request.pricing.prompt_usd_per_token !== null;
}

function worstCase(request: SweepRequest): number {
  if (!isKnown(request)) return request.reservation_usd;
  return (
    request.pricing.request_usd +
    request.max_input_tokens * request.pricing.prompt_usd_per_token! +
    request.max_output_tokens * request.pricing.completion_usd_per_token!
  );
}

function clean(value: number): number {
  return Number(value.toFixed(12));
}

export function parseSweepManifest(input: unknown): SweepManifest {
  return manifestSchema.parse(input);
}

export function sweepManifestHash(manifest: SweepManifest): string {
  return createHash('sha256').update(JSON.stringify(manifest)).digest('hex');
}

export function planSweep(manifest: SweepManifest, caps: SweepCaps): SweepPlan {
  const capUsd = z.number().positive().parse(caps.capUsd);
  const unknownPriceCapUsd = z.number().nonnegative().parse(caps.unknownPriceCapUsd);
  let reservation = 0;
  let unknownReservation = 0;
  let unknownCount = 0;

  for (const request of manifest.requests) {
    if (
      request.max_input_tokens < Buffer.byteLength(JSON.stringify(request.messages), 'utf8')
    ) {
      throw new Error(`input token bound is below UTF-8 byte bound: ${request.id}`);
    }
    if (request.reservation_usd + 1e-12 < worstCase(request)) {
      throw new Error(`reservation is below worst-case cost: ${request.id}`);
    }
    reservation += request.reservation_usd;
    if (!isKnown(request)) {
      unknownCount += 1;
      unknownReservation += request.reservation_usd;
    }
  }
  if (reservation > capUsd + 1e-12) throw new Error('total reservation exceeds cap');
  if (unknownReservation > unknownPriceCapUsd + 1e-12) {
    throw new Error('unknown-price reservation exceeds cap');
  }

  return {
    cap_usd: capUsd,
    known_price_requests: manifest.requests.length - unknownCount,
    request_count: manifest.requests.length,
    reservation_usd: clean(reservation),
    unknown_price_cap_usd: unknownPriceCapUsd,
    unknown_price_requests: unknownCount,
    unknown_price_reservation_usd: clean(unknownReservation),
  };
}
