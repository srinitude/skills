import { expect, test } from 'vitest';

import { parseSweepManifest, planSweep } from './sweep-manifest.js';

function manifest() {
  return {
    requests: [
      {
        id: 'candidate-001',
        kind: 'candidate',
        max_input_tokens: 100,
        max_output_tokens: 20,
        messages: [{ content: 'Evaluate the cases.', role: 'user' }],
        model: 'vendor/model',
        pricing: {
          completion_usd_per_token: 0.002,
          prompt_usd_per_token: 0.001,
          request_usd: 0,
        },
        provider: 'provider/route',
        provider_name: 'Provider Label',
        reservation_usd: 0.14,
      },
    ],
    run_id: 'run-2026-07-20',
    schema_version: 1,
  };
}

test('plans one fixed route under separate total and unknown-price caps', () => {
  const plan = planSweep(parseSweepManifest(manifest()), {
    capUsd: 1,
    unknownPriceCapUsd: 0,
  });

  expect(plan).toMatchObject({
    known_price_requests: 1,
    request_count: 1,
    reservation_usd: 0.14,
    unknown_price_requests: 0,
    unknown_price_reservation_usd: 0,
  });
});

test('rejects duplicate request IDs and missing provider routes', () => {
  const duplicate = manifest();
  duplicate.requests.push({ ...duplicate.requests[0]! });
  expect(() => parseSweepManifest(duplicate)).toThrow('duplicate request id');

  const missingRoute = manifest() as Record<string, unknown>;
  delete (missingRoute.requests as Array<Record<string, unknown>>)[0]?.provider;
  expect(() => parseSweepManifest(missingRoute)).toThrow();
});

test('rejects reservations below the known worst-case token cost', () => {
  const underReserved = manifest();
  underReserved.requests[0]!.reservation_usd = 0.139;

  expect(() =>
    planSweep(parseSweepManifest(underReserved), { capUsd: 1, unknownPriceCapUsd: 0 }),
  ).toThrow('reservation is below worst-case cost');
});

test('includes a fixed request charge in the reservation', () => {
  const withRequestCharge = manifest();
  withRequestCharge.requests[0]!.pricing.request_usd = 0.1;
  withRequestCharge.requests[0]!.reservation_usd = 0.23;

  expect(() =>
    planSweep(parseSweepManifest(withRequestCharge), { capUsd: 1, unknownPriceCapUsd: 0 }),
  ).toThrow('reservation is below worst-case cost');
});

test('permits a verified zero-cost route with no reservation', () => {
  const zeroCost = manifest();
  zeroCost.requests[0]!.pricing = {
    completion_usd_per_token: 0,
    prompt_usd_per_token: 0,
    request_usd: 0,
  };
  zeroCost.requests[0]!.reservation_usd = 0;

  expect(
    planSweep(parseSweepManifest(zeroCost), { capUsd: 1, unknownPriceCapUsd: 0 }),
  ).toMatchObject({ reservation_usd: 0 });
});

test('rejects an input token bound below the UTF-8 request bytes', () => {
  const understated = manifest();
  understated.requests[0]!.messages[0]!.content = 'x'.repeat(101);
  understated.requests[0]!.reservation_usd = 1;

  expect(() =>
    planSweep(parseSweepManifest(understated), { capUsd: 1, unknownPriceCapUsd: 0 }),
  ).toThrow('input token bound is below UTF-8 byte bound');
});

test('rejects total and unknown-price reservation cap overruns', () => {
  expect(() =>
    planSweep(parseSweepManifest(manifest()), { capUsd: 0.13, unknownPriceCapUsd: 0 }),
  ).toThrow('total reservation exceeds cap');

  const unknown = manifest() as Record<string, unknown>;
  (unknown.requests as Array<Record<string, unknown>>)[0]!.pricing = {
    completion_usd_per_token: null,
    prompt_usd_per_token: null,
    request_usd: 0,
  };
  expect(() =>
    planSweep(parseSweepManifest(unknown), { capUsd: 1, unknownPriceCapUsd: 0 }),
  ).toThrow('unknown-price reservation exceeds cap');
});
