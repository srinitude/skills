import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { parse } from 'yaml';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

async function yaml(path: string): Promise<Record<string, unknown>> {
  return parse(await readFile(join(root, path), 'utf8')) as Record<string, unknown>;
}

test('defines local and release GitHub Actions gates', async () => {
  const ci = await yaml('.github/workflows/ci.yml');
  expect(ci).toMatchObject({ permissions: { contents: 'read' } });
  expect(ci.jobs).toHaveProperty('ci');

  const release = await yaml('.github/workflows/release.yml');
  expect(release).toMatchObject({ permissions: { contents: 'write' } });
  expect(release.jobs).toHaveProperty('release');
});

test('makes tag release reruns recoverable', async () => {
  const workflow = await readFile(join(root, '.github/workflows/release.yml'), 'utf8');

  expect(workflow).toContain('gh release view "$GITHUB_REF_NAME"');
  expect(workflow).toContain('gh release upload "$GITHUB_REF_NAME"');
  expect(workflow).toContain('--clobber');
  expect(workflow).toContain('gh release create "$GITHUB_REF_NAME"');
});

test('uses Node 24 GitHub actions', async () => {
  for (const path of ['.github/workflows/ci.yml', '.github/workflows/release.yml']) {
    const workflow = await readFile(join(root, path), 'utf8');
    expect(workflow).toContain('actions/checkout@v7');
    expect(workflow).toContain('jdx/mise-action@v4');
    expect(workflow).not.toContain('actions/checkout@v4');
    expect(workflow).not.toContain('jdx/mise-action@v3');
  }
});

test('provides issue and pull request templates', async () => {
  await Promise.all(
    [
      '.github/ISSUE_TEMPLATE/bug.yml',
      '.github/ISSUE_TEMPLATE/skill.yml',
      '.github/PULL_REQUEST_TEMPLATE.md',
    ].map((path) => access(join(root, path))),
  );
  const bug = await yaml('.github/ISSUE_TEMPLATE/bug.yml');
  const skill = await yaml('.github/ISSUE_TEMPLATE/skill.yml');
  expect(bug).toMatchObject({ name: 'Bug report' });
  expect(skill).toMatchObject({ name: 'Skill proposal' });
});

test('marks the generated MCP bundle as semantic whitespace', async () => {
  const attributes = await readFile(join(root, '.gitattributes'), 'utf8');

  expect(attributes).toContain('mcp/dist/server.mjs whitespace=-blank-at-eol');
});
