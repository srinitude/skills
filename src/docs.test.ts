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
  'docs/skills-sh.md',
  'docs/openrouter-sweeps.md',
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
    'npm run skills -- eval --skill "$SKILL_NAME" --transport fixture',
  ]) {
    expect(readme).toContain(command);
  }
  const sweep = await readable('docs/openrouter-sweeps.md');
  expect(sweep).toContain('npm run skills -- sweep --phase dry-run');
  expect(sweep).toContain('--approval');
});

test('keeps the root guide skill-neutral', async () => {
  const readme = await readable('README.md');

  expect(readme).not.toContain('starting-point');
});

test('publishes the canonical skills.sh source and applicable guidance', async () => {
  const readme = await readable('README.md');
  const guidance = await readable('docs/skills-sh.md');
  const sweep = await readable('docs/openrouter-sweeps.md');
  const evidence = JSON.parse(await readable('evidence/skills-sh-pages.json')) as {
    pages: Array<{ url: string }>;
  };

  expect(readme).toContain(
    '[![Install with skills.sh](https://img.shields.io/badge/skills.sh-install-111111)](https://www.skills.sh/srinitude)',
  );
  expect(readme).not.toContain('https://skills.sh/b/srinitude/skills');
  expect(readme).not.toContain('https://skills.sh/srinitude/skills');
  expect(readme).toContain('npx skills add srinitude/skills');
  expect(readme).toContain('[skills.sh publishing notes](docs/skills-sh.md)');
  expect(evidence.pages.map(({ url }) => url)).toEqual([
    'https://www.skills.sh/docs',
    'https://www.skills.sh/docs/cli',
    'https://www.skills.sh/docs/api',
    'https://www.skills.sh/docs/faq',
  ]);
  expect(guidance).toContain('DISABLE_TELEMETRY=1');
  expect(guidance).toContain('VERCEL_OIDC_TOKEN');
  expect(guidance).toContain('github.com/vercel-labs/skills');
  expect(guidance).not.toContain('https://skills.sh/api/v1/');
  expect(sweep).toContain('https://openrouter.ai/docs/api_reference/errors-and-debugging');
  expect(sweep).not.toContain(
    'https://openrouter.ai/docs/api-reference/errors-and-debugging',
  );
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
