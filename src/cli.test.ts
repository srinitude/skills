import { mkdtemp, readFile, readdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

import { runCli } from './cli.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { recursive: true, force: true })),
  );
});

test('writes a repository validation report and returns PASS', async () => {
  const output = await mkdtemp(join(tmpdir(), 'skills-cli-'));
  temporary.push(output);
  const report = join(output, 'validation.json');
  let diagnostics = '';

  const code = await runCli(['validate', '--all', '--report', report], {
    root,
    stderr: { write: (text) => (diagnostics += text) },
  });

  expect(code).toBe(0);
  expect(JSON.parse(await readFile(report, 'utf8'))).toMatchObject({
    skillCount: 3,
    sourcePageCount: 13,
    status: 'PASS',
  });
  expect(diagnostics).toContain('validation: PASS');
});

test('returns BLOCKED for an unknown command without writing a report', async () => {
  let diagnostics = '';
  const code = await runCli(['unknown'], {
    root,
    stderr: { write: (text) => (diagnostics += text) },
  });

  expect(code).toBe(2);
  expect(diagnostics).toContain('unknown command');
});

test('runs a fixture eval and writes its report directory', async () => {
  const output = await mkdtemp(join(tmpdir(), 'skills-cli-'));
  temporary.push(output);
  const reportDirectory = join(output, 'eval-report');
  let diagnostics = '';
  const code = await runCli(
    [
      'eval',
      '--skill',
      'starting-point',
      '--transport',
      'fixture',
      '--report',
      reportDirectory,
    ],
    { root, stderr: { write: (text) => (diagnostics += text) } },
  );
  const report = JSON.parse(
    await readFile(join(reportDirectory, 'report.json'), 'utf8'),
  ) as {
    records: unknown[];
    status: string;
  };

  expect(code).toBe(0);
  expect(report.status).toBe('PASS');
  expect(report.records).toHaveLength(72);
});

test('runs a per-skill fixture benchmark', async () => {
  const output = await mkdtemp(join(tmpdir(), 'skills-cli-'));
  temporary.push(output);
  const reportPath = join(output, 'speed.json');
  let diagnostics = '';
  const code = await runCli(
    [
      'benchmark',
      '--skill',
      'starting-point',
      '--transport',
      'fixture',
      '--report',
      reportPath,
    ],
    { root, stderr: { write: (text) => (diagnostics += text) } },
  );
  const report = JSON.parse(await readFile(reportPath, 'utf8')) as {
    samples: number;
    status: string;
  };

  expect(code).toBe(0);
  expect(report).toMatchObject({ samples: 1000, status: 'PASS' });
});

test('checks all integration manifests and writes a report', async () => {
  const output = await mkdtemp(join(tmpdir(), 'skills-cli-'));
  temporary.push(output);
  const reportDirectory = join(output, 'integrations');
  let diagnostics = '';
  const code = await runCli(
    ['check-integrations', '--source', root, '--out', reportDirectory],
    { root, stderr: { write: (text) => (diagnostics += text) } },
  );
  const report = JSON.parse(
    await readFile(join(reportDirectory, 'report.json'), 'utf8'),
  ) as {
    clients: string[];
    status: string;
  };

  expect(code).toBe(0);
  expect(report).toMatchObject({ status: 'PASS' });
  expect(report.clients).toHaveLength(10);
  expect(diagnostics).toContain('integrations: PASS');
});

test('packages the repository and writes a package report', async () => {
  const output = await mkdtemp(join(tmpdir(), 'skills-cli-'));
  temporary.push(output);
  let diagnostics = '';
  const code = await runCli(['package', '--out', output], {
    root,
    stderr: { write: (text) => (diagnostics += text) },
  });
  const report = JSON.parse(
    await readFile(join(output, 'package-report.json'), 'utf8'),
  ) as {
    sha256: string;
  };

  expect(code).toBe(0);
  expect(report.sha256).toMatch(/^[a-f0-9]{64}$/);
  expect((await readdir(output)).some((name) => name.endsWith('.tgz'))).toBe(true);
  expect(diagnostics).toContain('package: PASS');
});
