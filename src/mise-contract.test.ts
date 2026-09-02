import { readFile, readdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

function task(source: string, name: string): string {
  const match = source.match(
    new RegExp(`\\[tasks\\.${name}\\]([\\s\\S]*?)(?=\\n\\[tasks\\.|$)`),
  );
  if (!match) throw new Error(`missing mise task: ${name}`);
  return match[1]!;
}

test('registry tasks discover every canonical skill directory', async () => {
  const source = await readFile(`${root}/mise.toml`, 'utf8');
  const skills = (await readdir(`${root}/skills`, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  for (const name of ['validate-skills', 'eval-offline', 'benchmark-offline']) {
    const body = task(source, name);
    expect(body).toContain('set -eu;');
    expect(body).toContain('skills/*');
    for (const skill of skills) expect(body).not.toContain(skill);
  }
});

test('gives public operations one non-circular Mise path', async () => {
  const source = await readFile(`${root}/mise.toml`, 'utf8');
  const ci = task(source, 'ci');
  const bootstrapConsumers = [
    'audit-dependencies',
    'audit-release',
    'benchmark',
    'build-mcp',
    'eval',
    'format',
    'format-write',
    'lint',
    'refresh-source-evidence',
    'test-focus',
    'typecheck',
    'validate',
  ];

  for (const name of ['benchmark', 'eval', 'sweep', 'test-mcp', 'validate']) {
    expect(task(source, name)).not.toContain('mise run');
  }
  for (const name of bootstrapConsumers) {
    expect(task(source, name)).toContain('depends = ["bootstrap"]');
  }
  expect(task(source, 'test')).toContain('depends = ["build-mcp"]');
  expect(task(source, 'test-mcp')).toContain('depends = ["test"]');
  expect(task(source, 'package')).toContain('depends = ["test-mcp"]');
  expect(task(source, 'check-integrations')).toContain('depends = ["package"]');
  expect(task(source, 'smoke-clients')).toContain('depends = ["build-mcp"]');
  expect(task(source, 'test')).toContain('src/*.test.ts src/eval/*.test.ts');
  for (const name of ['validate-skills', 'eval-offline', 'benchmark-offline']) {
    expect(task(source, name)).toContain('depends = ["check-integrations"]');
    expect(ci).toContain(`"${name}"`);
  }
  for (const name of ['test', 'test-mcp', 'package']) {
    expect(ci).not.toContain(`"${name}"`);
  }
  expect(ci).not.toContain('"check-integrations"');
  expect(ci).not.toContain('"bootstrap"');
  expect(ci).not.toContain('"build-mcp"');
  expect(ci).toContain('"audit-dependencies"');
  expect(task(source, 'audit-dependencies')).toContain('npm audit --audit-level=high');
  expect(task(source, 'release-github')).toContain('depends = ["ci"]');
  expect(task(source, 'release-github')).toContain('gh release view');
  expect(task(source, 'release-github')).toContain('gh release upload');
  expect(task(source, 'release-github')).toContain('--clobber');
  expect(ci).not.toContain('"release-github"');
  expect(source).not.toContain('[tasks.check-copy]');
});
