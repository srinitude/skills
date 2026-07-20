import { expect, test } from 'vitest';

import { parseSweepApproval, verifySweepApproval } from './sweep-approval.js';

function approval() {
  return parseSweepApproval({
    approved_at: '2026-07-20T21:00:00Z',
    approved_by: 'user',
    cap_usd: 1,
    manifest_sha256: 'a'.repeat(64),
    schema_version: 1,
    unknown_price_cap_usd: 0,
  });
}

test('accepts an explicit user approval bound to one manifest and both caps', () => {
  expect(() =>
    verifySweepApproval(approval(), {
      capUsd: 1,
      manifestSha256: 'a'.repeat(64),
      unknownPriceCapUsd: 0,
    }),
  ).not.toThrow();
});

test('rejects manifest or cap drift after approval', () => {
  expect(() =>
    verifySweepApproval(approval(), {
      capUsd: 2,
      manifestSha256: 'a'.repeat(64),
      unknownPriceCapUsd: 0,
    }),
  ).toThrow('approval cap mismatch');
  expect(() =>
    verifySweepApproval(approval(), {
      capUsd: 1,
      manifestSha256: 'b'.repeat(64),
      unknownPriceCapUsd: 0,
    }),
  ).toThrow('approval manifest mismatch');
  expect(() =>
    verifySweepApproval(approval(), {
      capUsd: 1,
      manifestSha256: 'a'.repeat(64),
      unknownPriceCapUsd: 0.01,
    }),
  ).toThrow('approval unknown-price cap mismatch');
});
