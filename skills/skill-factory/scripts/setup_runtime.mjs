/** Reuse checked installs; retain old and failed trees during a rebuild. */
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { closeSync, lstatSync, mkdirSync, mkdtempSync, openSync, readFileSync,
  realpathSync, renameSync, unlinkSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const hash = value => createHash('sha256').update(value).digest('hex');
const receiptName = '.skill-runtime.json';

function present(path, kind) {
  try {
    const stat = lstatSync(path);
    if (stat.isSymbolicLink() || !(kind === 'file' ? stat.isFile() : stat.isDirectory()))
      throw Error('Expected a real ' + kind + ': ' + path);
    return true;
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
}

function bytes(path) {
  if (!present(path, 'file')) throw Error('Missing input: ' + path);
  return readFileSync(path);
}

function npm(root, args, required = true) {
  // Windows needs its command launcher; every argument here is a fixed literal.
  const result = spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', args,
    { cwd: root, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024,
      shell: process.platform === 'win32' });
  if (result.error) throw result.error;
  if (result.status !== 0) process.stderr.write((result.stdout ?? '') + (result.stderr ?? ''));
  if (required && result.status !== 0) throw Error('npm ' + args.join(' ') + ' failed: ' + result.status);
  return result;
}

function identity(root, mode) {
  return hash(JSON.stringify({ package: hash(bytes(join(root, 'package.json'))),
    lock: hash(bytes(join(root, 'package-lock.json'))),
    owner: hash(bytes(fileURLToPath(import.meta.url))), mode,
    node: process.version, platform: process.platform, arch: process.arch,
    npm: npm(root, ['--version']).stdout.trim(),
    config: hash(npm(root, ['config', 'list', '--json']).stdout) }));
}

function checked(root, mode, required = true) {
  // Storage resolves peers from the checked root; npm's nested tree cannot see them.
  const storage = mode === '--omit=peer';
  const args = ['ls', storage ? '--depth=0' : '--all', '--json', mode];
  if (npm(root, args, required).status !== 0) return false;
  if (!storage) return true;
  const probe = "const m=await import('@mastra/libsql'); "
    + "if(typeof m.LibSQLStore!=='function') throw Error('Missing LibSQLStore');";
  return npm(root, ['exec', '--no', '--', 'node', '--input-type=module', '--eval', probe], required).status === 0;
}

function reusable(root, mode, expected) {
  const modules = join(root, 'node_modules'), path = join(modules, receiptName);
  if (!present(modules, 'directory') || !present(path, 'file')) return false;
  let saved;
  try { saved = JSON.parse(bytes(path)); }
  catch (error) { if (error instanceof SyntaxError) return false; throw error; }
  if (saved?.identity !== expected) return false;
  if (!checked(root, mode, false)) return false;
  if (identity(root, mode) !== expected) throw Error('Runtime inputs changed during reuse');
  return true;
}

function recover(modules, backup, hadPrevious) {
  if (present(modules, 'directory')) renameSync(modules, join(backup, 'failed'));
  if (hadPrevious) renameSync(join(backup, 'prior'), modules);
}

function rebuild(root, mode, expected, artifacts) {
  const modules = join(root, 'node_modules'), backup = mkdtempSync(join(artifacts, 'runtime-'));
  const hadPrevious = present(modules, 'directory');
  if (hadPrevious) renameSync(modules, join(backup, 'prior'));
  try {
    const result = npm(root, ['ci', mode, '--ignore-scripts'], false);
    writeFileSync(join(backup, 'install.stdout'), result.stdout);
    writeFileSync(join(backup, 'install.stderr'), result.stderr);
    if (result.status !== 0) throw Error('npm ci failed: ' + result.status);
    checked(root, mode);
    if (identity(root, mode) !== expected) throw Error('Runtime inputs changed during install');
    if (!present(modules, 'directory')) mkdirSync(modules);
    writeFileSync(join(modules, receiptName), JSON.stringify({ identity: expected }) + '\n', { flag: 'wx', mode: 0o600 });
  } catch (error) {
    recover(modules, backup, hadPrevious);
    writeFileSync(join(backup, 'failure.txt'), String(error) + '\n');
    throw Error('Runtime install failed; previous tree restored, evidence retained at ' + backup, { cause: error });
  }
  return backup;
}

function prepare(root, mode, artifacts) {
  if (realpathSync(root) !== root) throw Error('Runtime path must not use symlinks');
  const expected = identity(root, mode);
  const reused = reusable(root, mode, expected);
  const backup = reused ? null : rebuild(root, mode, expected, artifacts);
  return { root, reused, identity: expected, backup, package_check: 'passed' };
}

function main() {
  if (process.env.MISE_TASK_NAME !== 'setup-runtime' || process.argv.length !== 3
      || process.argv[2] !== 'runtime/standardization') throw Error('Use mise run setup-runtime');
  const root = fileURLToPath(new URL('../', import.meta.url)).replace(/[\\/]$/, '');
  if (realpathSync(root) !== root) throw Error('Use a real skill directory');
  const artifacts = join(root, '.artifacts');
  if (!present(artifacts, 'directory')) mkdirSync(artifacts, { mode: 0o700 });
  const lockPath = join(artifacts, 'runtime-install.lock');
  const lock = openSync(lockPath, 'wx', 0o600);
  try {
    writeFileSync(lock, String(process.pid) + '\n');
    const results = [prepare(root, '--include=dev', artifacts),
      prepare(join(root, 'runtime', 'standardization'), '--omit=peer', artifacts)];
    process.stderr.write(JSON.stringify({ results, acceptance: 'pending',
      limit: 'Cooperating installer lock only. Stop active consumers before a rebuild; retained trees need separate cleanup review.' }) + '\n');
  } finally { closeSync(lock); unlinkSync(lockPath); }
}

try { main(); }
catch (error) { process.stderr.write(String(error.stack ?? error) + '\n'); process.exitCode = 1; }
