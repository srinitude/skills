import { mkdir, rm } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { build } from 'esbuild';

interface BuildMcpOptions {
  outfile: string;
  root: string;
}

const currentFile = fileURLToPath(import.meta.url);
const defaultRoot = resolve(dirname(currentFile), '..');

export async function buildMcp(options: BuildMcpOptions): Promise<void> {
  await mkdir(dirname(options.outfile), { recursive: true });
  await rm(`${options.outfile}.map`, { force: true });
  await build({
    banner: {
      js: "import { createRequire as __createRequire } from 'node:module'; const require = __createRequire(import.meta.url);",
    },
    bundle: true,
    entryPoints: [resolve(options.root, 'mcp', 'src', 'index.ts')],
    format: 'esm',
    logLevel: 'silent',
    minifyWhitespace: true,
    outfile: options.outfile,
    packages: 'bundle',
    platform: 'node',
    target: 'node24',
  });
}

async function main(): Promise<void> {
  await buildMcp({
    outfile: resolve(defaultRoot, 'mcp', 'dist', 'server.mjs'),
    root: defaultRoot,
  });
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : '';
if (invokedPath === currentFile) {
  main().catch((error: unknown) => {
    const message = error instanceof Error ? error.message : 'unknown error';
    process.stderr.write(`MCP build failed: ${message}\n`);
    process.exitCode = 1;
  });
}
