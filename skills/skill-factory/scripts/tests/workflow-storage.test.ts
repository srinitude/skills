import assert from 'node:assert/strict';
import { fork, spawn } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const fixture = fileURLToPath(new URL('./workflow-storage.fixture.ts', import.meta.url));

async function interruptedSuspension(directory: string, id: string) {
  const child = fork(fixture, ['start', directory, id], { silent: true });
  await new Promise<void>((resolve, reject) => {
    child.once('error', reject);
    child.once('exit', code => reject(new Error('Child exited before suspension: ' + code)));
    child.once('message', message => {
      try {
        assert.equal((message as { status: string }).status, 'suspended');
        resolve();
      } catch (error) { reject(error); }
    });
  });
  const closed = new Promise(resolve => child.once('exit', resolve));
  child.kill('SIGKILL');
  await closed;
}

function resume(directory: string, id: string, response: unknown) {
  return new Promise<{ code: number | null; stdout: string; stderr: string }>((resolve, reject) => {
    const child = spawn(process.execPath, [fixture, 'resume', directory, id, JSON.stringify(response)]);
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', data => { stdout += data; });
    child.stderr.on('data', data => { stderr += data; });
    child.once('error', reject);
    child.once('close', code => resolve({ code, stdout, stderr }));
  });
}

test('committed suspension survives killed process; only one concurrent resume causes the effect',
  { timeout: 30000 }, async () => {
    const directory = await mkdtemp(join(tmpdir(), 'workflow-storage-'));
    try {
      await interruptedSuspension(directory, 'one');
      await assert.rejects(() => readFile(join(directory, 'effects.txt')));
      const results = await Promise.all([resume(directory, 'one', { proceed: true }),
        resume(directory, 'one', { proceed: true })]);
      assert.equal(results.filter(result => result.code === 0).length, 1, JSON.stringify(results));
      assert.equal(await readFile(join(directory, 'effects.txt'), 'utf8'), 'one\n');
      const replay = await resume(directory, 'one', { proceed: true });
      assert.notEqual(replay.code, 0);
      assert.equal(await readFile(join(directory, 'effects.txt'), 'utf8'), 'one\n');
    } finally { await rm(directory, { recursive: true, force: true }); }
  });

test('invalid resume input and explicit rejection produce no protected effect',
  { timeout: 30000 }, async () => {
    const directory = await mkdtemp(join(tmpdir(), 'workflow-rejection-'));
    try {
      await interruptedSuspension(directory, 'invalid');
      assert.notEqual((await resume(directory, 'invalid', { proceed: 'yes' })).code, 0);
      await assert.rejects(() => readFile(join(directory, 'effects.txt')));
      await interruptedSuspension(directory, 'rejected');
      assert.notEqual((await resume(directory, 'rejected', { proceed: false })).code, 0);
      await assert.rejects(() => readFile(join(directory, 'effects.txt')));
    } finally { await rm(directory, { recursive: true, force: true }); }
  });
