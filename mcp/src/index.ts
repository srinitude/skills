import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

import { createSkillServer } from './server.js';

function repositoryRoot(): string {
  return resolve(dirname(fileURLToPath(import.meta.url)), '../..');
}

async function main(): Promise<void> {
  const server = await createSkillServer(repositoryRoot());
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : 'unknown error';
  process.stderr.write(`mcp startup failed: ${message}\n`);
  process.exitCode = 1;
});
