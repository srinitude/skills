import { readFile, readdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { expect, test } from 'vitest';

const directory = dirname(fileURLToPath(import.meta.url));

test('keeps the MCP source local, read-only, and credential-free', async () => {
  const files = (await readdir(directory)).filter(
    (name) => name.endsWith('.ts') && !name.includes('.test.'),
  );
  const source = (
    await Promise.all(files.map((name) => readFile(join(directory, name), 'utf8')))
  ).join('\n');

  expect(source).not.toMatch(/node:(?:http|https|net|tls|dgram)/);
  expect(source).not.toMatch(/\bfetch\s*\(/);
  expect(source).not.toMatch(/process\.env/);
  expect(source).not.toMatch(/credential|telemetry/i);
  expect(source).not.toMatch(/register(?:Prompt|Tool)\([^]*?(?:write|delete|update)/i);
  expect(source).toContain('StdioServerTransport');
});
