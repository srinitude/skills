import { expect, test } from 'vitest';

import { clientRouteSpecs } from './client-smoke.js';

test('owns one live proof route for every promised client surface', () => {
  const specs = clientRouteSpecs();
  expect(specs.map((route) => route.id)).toEqual([
    'agent-plugins-v1',
    'aider',
    'claude-code',
    'codex',
    'codex-shared-plugin',
    'continue',
    'cursor',
    'gemini-cli',
    'hermes-agent',
    'openclaw',
    'opencode',
  ]);
  expect(new Set(specs.map((route) => route.id)).size).toBe(specs.length);
  expect(specs.every((route) => route.command.length > 10)).toBe(true);
  expect(specs.every((route) => route.route_type.length > 4)).toBe(true);
  expect(specs.find((route) => route.id === 'openclaw')?.route_type).toBe(
    'Codex-compatible bundle',
  );
});

test('keeps model execution out of cold-load proofs', () => {
  for (const route of clientRouteSpecs()) {
    expect(route.command).not.toMatch(/(?:^|\s)(?:chat|generate|--prompt)(?:\s|$)/i);
  }
});
