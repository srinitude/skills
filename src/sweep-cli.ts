import { readFile } from 'node:fs/promises';

import { parseSweepApproval } from './eval/sweep-approval.js';
import { parseSweepManifest } from './eval/sweep-manifest.js';
import { runSweep } from './eval/sweep-runner.js';

interface DiagnosticSink {
  write(text: string): unknown;
}

function optionValue(args: string[], option: string): string | undefined {
  const index = args.indexOf(option);
  return index >= 0 ? args[index + 1] : undefined;
}

function required(args: string[], option: string): string {
  const value = optionValue(args, option);
  if (!value) throw new Error(`${option} is required`);
  return value;
}

function phase(args: string[]): 'dry-run' | 'full' | 'pilot' {
  const value = required(args, '--phase');
  if (value !== 'dry-run' && value !== 'pilot' && value !== 'full') {
    throw new Error('--phase must be dry-run, pilot, or full');
  }
  return value;
}

async function json(path: string): Promise<unknown> {
  return JSON.parse(await readFile(path, 'utf8'));
}

export async function runSweepCli(args: string[], stderr: DiagnosticSink): Promise<number> {
  const manifest = parseSweepManifest(await json(required(args, '--manifest')));
  const approvalPath = optionValue(args, '--approval');
  const report = await runSweep({
    apiKey: process.env.OPENROUTER_API_KEY,
    approval: approvalPath ? parseSweepApproval(await json(approvalPath)) : undefined,
    capUsd: Number(required(args, '--cap')),
    manifest,
    out: required(args, '--out'),
    phase: phase(args),
    unknownPriceCapUsd: Number(optionValue(args, '--unknown-price-cap') ?? '0'),
  });
  stderr.write(`sweep: ${report.status}\n`);
  return report.status === 'PASS' ? 0 : 2;
}
