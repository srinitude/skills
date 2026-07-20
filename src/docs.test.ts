import { access, readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const requiredDocs = [
  'README.md',
  'CONTRIBUTING.md',
  'SECURITY.md',
  'SUPPORT.md',
  'CHANGELOG.md',
  'adapters/aider/README.md',
  'adapters/continue/README.md',
  'adapters/hermes-agent/README.md',
  'adapters/openclaw/README.md',
];

async function readable(path: string): Promise<string> {
  return readFile(join(root, path), 'utf8');
}

test('documents every supported client and tested local command', async () => {
  await Promise.all(requiredDocs.map((path) => access(join(root, path))));
  const readme = await readable('README.md');
  for (const client of [
    'Aider',
    'ChatGPT',
    'Claude Code',
    'Codex',
    'Continue',
    'Cursor',
    'Gemini CLI',
    'Hermes Agent',
    'OpenClaw',
    'opencode',
  ]) {
    expect(readme).toContain(client);
  }
  for (const command of [
    'npm ci --include=dev',
    'mise run ci',
    'npm run build:mcp',
    'npm run skills -- eval starting-point --transport fixture',
  ]) {
    expect(readme).toContain(command);
  }
});

test('keeps every relative Markdown link resolvable', async () => {
  for (const path of requiredDocs) {
    const source = await readable(path);
    for (const match of source.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
      const target = match[1]!;
      if (/^(https?:|#|mailto:)/.test(target)) continue;
      const clean = target.split('#')[0]!;
      await expect(access(resolve(root, dirname(path), clean))).resolves.toBeUndefined();
    }
  }
});

test('keeps the root guide concise and the Aider route portable', async () => {
  const readme = await readable('README.md');
  const aider = await readable('adapters/aider/README.md');
  expect(readme.split('\n').length).toBeLessThan(150);
  expect(aider).toContain(
    'aider --read /absolute/path/to/skills/skills/starting-point/SKILL.md',
  );
});
