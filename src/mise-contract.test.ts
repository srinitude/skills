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
