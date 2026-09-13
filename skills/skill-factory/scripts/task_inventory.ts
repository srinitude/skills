/** Native Mise discovery shared by task tools and workflow evidence. */
import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { lstat, readFile, realpath, readdir } from 'node:fs/promises';
import { isAbsolute, join, relative, sep } from 'node:path';
import { z } from 'zod';

export const digest = (raw: Uint8Array) => createHash('sha256').update(raw).digest('hex');

export async function bound(file: string, expected?: string) {
  const metadata = await lstat(file);
  if (!metadata.isFile() || metadata.isSymbolicLink()) throw Error('Expected a regular bound input');
  const raw = await readFile(file), sha256 = digest(raw);
  if (expected !== undefined && sha256 !== expected) throw Error('Changed workflow input: ' + file);
  return { raw, sha256 };
}

const nativeTask = z.object({ name: z.string().min(1), description: z.string(),
  source: z.string().refine(isAbsolute), config_sources: z.array(z.string()).default([]),
  depends: z.array(z.unknown()).default([]) }).passthrough();
export type Task = z.infer<typeof nativeTask>;
export type Snapshot = { tasks: Task[]; revision: string };

function inside(root: string, path: string) {
  const part = relative(root, path);
  return part !== '..' && !part.startsWith('..' + sep) && !isAbsolute(part);
}

async function nativeTasks(root: string, env: NodeJS.ProcessEnv) {
  const { stdout } = await promisify(execFile)('mise', ['-C', root, 'tasks', 'ls', '--hidden', '--json'],
    { env, maxBuffer: 16 * 1024 * 1024, timeout: 30000 });
  return z.array(nativeTask).parse(JSON.parse(stdout)).filter(task => inside(root, task.source))
    .sort((a, b) => a.name < b.name ? -1 : Number(a.name > b.name));
}

export async function taskSnapshot(root: string, env = process.env): Promise<Snapshot> {
  root = await realpath(root);
  const tasks = await nativeTasks(root, env);
  const sources = [...new Set([join(root, 'mise.toml'),
    ...tasks.flatMap(task => [task.source, ...task.config_sources])])].sort();
  for (const source of sources)
    if (!inside(root, await realpath(source))) throw Error('Task source escapes this skill');
  const identities = await Promise.all(sources.map(async source => [source, (await bound(source)).sha256] as const));
  if (JSON.stringify(tasks) !== JSON.stringify(await nativeTasks(root, env))) throw Error('Tasks changed during discovery');
  for (const [source, sha256] of identities) await bound(source, sha256);
  return { tasks, revision: digest(Buffer.from(JSON.stringify([tasks, identities]))) };
}

async function runtimeFiles(directory: string): Promise<string[]> {
  const files: string[] = [];
  for (const item of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, item.name);
    if (item.name === '__pycache__') continue;
    if (item.isDirectory()) files.push(...await runtimeFiles(path));
    else if (/\.(?:[cm]?[jt]s|tsx|py)$/.test(item.name)) files.push(path);
  }
  return files.sort();
}

export async function runtimeIdentity(root: string) {
  const files = [...await runtimeFiles(join(root, 'scripts')), ...['package.json', 'package-lock.json', 'tsconfig.json',
    'runtime/standardization/package.json', 'runtime/standardization/package-lock.json'].map(file => join(root, file))];
  const runtime = Object.fromEntries(await Promise.all(files.map(async file => {
    if (await realpath(file) !== file) throw Error('Use real runtime input paths');
    return [file, (await bound(file)).sha256];
  })));
  runtime['$process'] = digest(Buffer.from(JSON.stringify({ node: process.version, platform: process.platform,
    arch: process.arch, python: process.env.UV_PYTHON, locale: process.env.LC_ALL ?? process.env.LANG })));
  return runtime;
}
