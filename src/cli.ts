import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { FixtureTransport } from './eval/fixture-transport.js';
import { runEvaluation } from './eval/runner.js';
import { loadEvalDefinition } from './eval/schema.js';
import { runSkillBenchmark } from './eval/speed.js';
import type { EvalReport, TerminalStatus } from './eval/types.js';
import { checkIntegrations } from './integrations.js';
import { buildPackage } from './package.js';
import { validateRepository } from './repository-validation.js';
import { validateSkill } from './skill-validation.js';

interface DiagnosticSink {
  write(text: string): unknown;
}

export interface CliOptions {
  root?: string;
  stderr?: DiagnosticSink;
}

const defaultRoot = dirname(dirname(fileURLToPath(import.meta.url)));

function statusCode(status: TerminalStatus): number {
  if (status === 'PASS') return 0;
  if (status === 'FAIL') return 1;
  return 2;
}

function optionValue(args: string[], option: string): string | undefined {
  const index = args.indexOf(option);
  return index >= 0 ? args[index + 1] : undefined;
}

async function saveReport(path: string, report: unknown): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(report, null, 2)}\n`);
}

function requireFixture(args: string[]): FixtureTransport {
  const transport = optionValue(args, '--transport');
  if (transport !== 'fixture')
    throw new Error(`unsupported transport: ${transport ?? '(missing)'}`);
  return new FixtureTransport();
}

function requireSkill(args: string[]): string {
  const skill = optionValue(args, '--skill') ?? args[0];
  if (!skill || skill.startsWith('-')) throw new Error('skill name is required');
  return skill;
}

async function saveEvalReport(directory: string, report: EvalReport): Promise<void> {
  await mkdir(directory, { recursive: true });
  await saveReport(resolve(directory, 'report.json'), report);
  await saveReport(resolve(directory, 'judge-packets.json'), report.judge_packets);
  const lines = report.records.map((record) => JSON.stringify(record)).join('\n');
  await writeFile(resolve(directory, 'records.ndjson'), `${lines}\n`);
}

async function validateCommand(
  args: string[],
  root: string,
  stderr: DiagnosticSink,
): Promise<number> {
  const reportPath = optionValue(args, '--report');
  if (!reportPath) {
    stderr.write('validation: BLOCKED: --report is required\n');
    return 2;
  }
  const all = args.includes('--all');
  const name = args.find((arg) => !arg.startsWith('-') && arg !== reportPath);
  if (!all && !name) {
    stderr.write('validation: BLOCKED: pass --all or a skill name\n');
    return 2;
  }
  const report = all ? await validateRepository(root) : await validateSkill(root, name!);
  await saveReport(reportPath, report);
  stderr.write(`validation: ${report.status}\n`);
  return statusCode(report.status);
}

async function evalCommand(
  args: string[],
  root: string,
  stderr: DiagnosticSink,
): Promise<number> {
  const skill = requireSkill(args);
  const transport = requireFixture(args);
  const directory = optionValue(args, '--report');
  if (!directory) throw new Error('--report is required');
  const definition = await loadEvalDefinition(root, skill);
  const report = await runEvaluation(definition, transport);
  await saveEvalReport(directory, report);
  stderr.write(`eval: ${report.status}\n`);
  return statusCode(report.status);
}

async function benchmarkCommand(
  args: string[],
  root: string,
  stderr: DiagnosticSink,
): Promise<number> {
  const skill = requireSkill(args);
  const transport = requireFixture(args);
  const reportPath = optionValue(args, '--report');
  const samples = Number(optionValue(args, '--samples') ?? '1000');
  if (!reportPath) throw new Error('--report is required');
  if (!Number.isInteger(samples) || samples < 1)
    throw new Error('--samples must be a positive integer');
  const report = await runSkillBenchmark(root, skill, transport, samples);
  await saveReport(reportPath, report);
  stderr.write(`benchmark: ${report.status}\n`);
  return statusCode(report.status);
}

async function integrationsCommand(
  args: string[],
  root: string,
  stderr: DiagnosticSink,
): Promise<number> {
  const source = resolve(optionValue(args, '--source') ?? root);
  const directory = optionValue(args, '--out');
  if (!directory) throw new Error('--out is required');
  const report = await checkIntegrations(source);
  await saveReport(resolve(directory, 'report.json'), report);
  stderr.write(`integrations: ${report.status}\n`);
  return statusCode(report.status);
}

async function packageCommand(
  args: string[],
  root: string,
  stderr: DiagnosticSink,
): Promise<number> {
  const directory = optionValue(args, '--out');
  if (!directory) throw new Error('--out is required');
  const report = await buildPackage(root, resolve(directory));
  await saveReport(resolve(directory, 'package-report.json'), report);
  stderr.write('package: PASS\n');
  return 0;
}

async function dispatch(
  command: string | undefined,
  args: string[],
  root: string,
  stderr: DiagnosticSink,
): Promise<number> {
  if (command === 'validate') return validateCommand(args, root, stderr);
  if (command === 'eval') return evalCommand(args, root, stderr);
  if (command === 'benchmark') return benchmarkCommand(args, root, stderr);
  if (command === 'check-integrations') return integrationsCommand(args, root, stderr);
  if (command === 'package') return packageCommand(args, root, stderr);
  throw new Error(`unknown command: ${command ?? '(missing)'}`);
}

export async function runCli(args: string[], options: CliOptions = {}): Promise<number> {
  const stderr = options.stderr ?? process.stderr;
  const root = options.root ?? defaultRoot;
  const [command, ...commandArgs] = args;
  try {
    return await dispatch(command, commandArgs, root, stderr);
  } catch (error) {
    stderr.write(`BLOCKED: ${error instanceof Error ? error.message : String(error)}\n`);
    return 2;
  }
}

const invoked = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : '';
if (import.meta.url === invoked) {
  process.exitCode = await runCli(process.argv.slice(2));
}
