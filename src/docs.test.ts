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
    'mise run bootstrap',
    'mise run ci',
    'mise run build-mcp',
    'mise run eval -- --skill "$SKILL_NAME"',
  ]) {
    expect(readme).toContain(command);
  }
  expect(readme).not.toMatch(/npm (?:ci|run|test|pack)\b/);
  const sweep = await readable('docs/openrouter-sweeps.md');
  expect(sweep).toContain('mise run sweep -- --phase dry-run');
  expect(sweep).not.toMatch(/npm (?:ci|run|test|pack)\b/);
  expect(sweep).toContain('--approval');
});

test('keeps the root guide skill-neutral', async () => {
  const readme = await readable('README.md');

  expect(readme).not.toContain('starting-point');
});

test('records the release while keeping a fresh Unreleased section', async () => {
  const changelog = await readable('CHANGELOG.md');
  const release = changelog.split('## GitHub release 0.1.4')[0]!;
  expect(release).toContain('## Unreleased');
  expect(release).toContain('## GitHub release 0.1.5');
  for (const skill of ['goal-prompt', 'meaning-preserving-rewrite', 'simplify-skill']) {
    expect(release).toContain(`\`${skill}\``);
  }
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
  const hermes = await readable('adapters/hermes-agent/README.md');
  expect(readme.split('\n').length).toBeLessThan(150);
  expect(aider).toContain('--read /absolute/path/to/skills/skills/<skill-name>/SKILL.md');
  expect(aider).not.toContain('always-current-datetime/SKILL.md\n');
  expect(hermes).toContain('hermes skills install srinitude/skills/<skill-name>');
  expect(hermes.match(/hermes skills install/g)).toHaveLength(1);
});

test('keeps release tags distinct from plugin versions in install guidance', async () => {
  const openclaw = await readable('adapters/openclaw/README.md');

  expect(openclaw).toContain('git:github.com/srinitude/skills@<release-tag>');
  expect(openclaw).not.toContain('skills@v0.1.0');
  expect(openclaw).toContain('Codex-compatible bundle');
  expect(openclaw).toContain('`.codex-plugin/plugin.json` takes precedence');
  expect(openclaw).toContain('`.mcp.json`');
  expect(openclaw).not.toContain('native plugin manifest');
});

test('keeps contributor and Cursor claims aligned with their owners', async () => {
  const contributing = await readable('CONTRIBUTING.md');
  const readme = await readable('README.md');
  const cursor = readme.split('\n').find((line) => line.startsWith('| Cursor')) ?? '';

  expect(contributing).toContain('at most 1024 characters');
  expect(contributing).not.toContain('shorter than 60 characters');
  expect(cursor).toContain('| Agent Plugins bundle');
  expect(cursor).toContain('| Yes');
  expect(readme).toContain('root Agent Plugin');
});
