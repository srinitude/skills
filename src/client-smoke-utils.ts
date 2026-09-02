import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';

const run = promisify(execFile);

function environment(home: string): NodeJS.ProcessEnv {
  const keep = ['LANG', 'LC_ALL', 'PATH', 'SHELL', 'TERM', 'TMPDIR'];
  const env: NodeJS.ProcessEnv = { CI: '1', HOME: home };
  for (const name of keep) if (process.env[name]) env[name] = process.env[name];
  env.NO_COLOR = '1';
  env.NPM_CONFIG_CACHE =
    process.env.NPM_CONFIG_CACHE ?? join(process.env.HOME ?? home, '.npm');
  env.PATH = `${dirname(process.execPath)}:${env.PATH ?? ''}`;
  env.PYTHONDONTWRITEBYTECODE = '1';
  env.UV_CACHE_DIR =
    process.env.UV_CACHE_DIR ?? join(process.env.HOME ?? home, '.cache', 'uv');
  env.XDG_CONFIG_HOME = join(home, '.config');
  return env;
}

export async function isolatedHome(prefix: string): Promise<string> {
  return mkdtemp(join(tmpdir(), `${prefix}-`));
}

export async function command(
  executable: string,
  args: string[],
  cwd: string,
  home: string,
): Promise<string> {
  const result = await run(executable, args, {
    cwd,
    encoding: 'utf8',
    env: environment(home),
    maxBuffer: 16 * 1024 * 1024,
    timeout: 180_000,
  });
  return `${result.stdout}\n${result.stderr}`;
}

export function requireText(source: string, value: string, label: string): void {
  if (!source.toLowerCase().includes(value.toLowerCase())) {
    throw new Error(`${label} did not report ${value}`);
  }
}

export async function sha256(path: string): Promise<string> {
  const bytes = await readFile(path);
  return createHash('sha256').update(bytes).digest('hex');
}

export async function skillTreeSha(root: string, names: string[]): Promise<string> {
  const hash = createHash('sha256');
  for (const name of names) {
    hash.update(name).update('\0');
    hash.update(await readFile(join(root, 'skills', name, 'SKILL.md'))).update('\0');
  }
  return hash.digest('hex');
}
