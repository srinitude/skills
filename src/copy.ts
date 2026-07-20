import { createHash } from 'node:crypto';
import { readdir, readFile } from 'node:fs/promises';
import { extname, join, relative } from 'node:path';

export interface CopyFinding {
  code: string;
  message: string;
  path: string;
}

export interface CopyReport {
  findings: CopyFinding[];
  inspected_files: number;
  skill_files: string[];
  status: 'FAIL' | 'PASS';
}

const ignoredDirectories = new Set([
  '.artifacts',
  '.git',
  'mcp',
  'node_modules',
  'scripts',
  'src',
]);
const publicExtensions = new Set(['.json', '.md', '.py', '.toml', '.yaml', '.yml']);
const bannedTerms = /\b(herdr|humanize-writing|leverage)\b/i;
const audienceLabels =
  /\b(beginner|beginners|expert|experts|non-technical|novice|novices)\b/i;
const modelNames = /\b(Claude|DeepSeek|Gemini|GPT|Grok|Llama|Mistral|Qwen)\b/;

function portable(root: string, path: string): string {
  return relative(root, path).split('\\').join('/');
}

async function files(root: string, directory = root): Promise<string[]> {
  const found: string[] = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isDirectory() && ignoredDirectories.has(entry.name)) continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) found.push(...(await files(root, path)));
    else if (entry.isFile()) found.push(path);
  }
  return found.sort();
}

function finding(code: string, message: string, path: string): CopyFinding {
  return { code, message, path };
}

function scanText(path: string, source: string): CopyFinding[] {
  const found: CopyFinding[] = [];
  if (bannedTerms.test(source)) {
    found.push(finding('BANNED_TERM', 'public copy contains a banned source term', path));
  }
  if (audienceLabels.test(source)) {
    found.push(finding('AUDIENCE_LABEL', 'public copy labels its reader', path));
  }
  if (/[–—]/u.test(source)) {
    found.push(
      finding('FORBIDDEN_DASH', 'public copy contains an en dash or em dash', path),
    );
  }
  if ((path === 'AGENTS.md' || path === 'CLAUDE.md') && modelNames.test(source)) {
    found.push(finding('MODEL_NAME', 'context policy names a model', path));
  }
  if (
    (path.startsWith('skills/') || path === 'AGENTS.md' || path === 'CLAUDE.md') &&
    /hermes/i.test(source)
  ) {
    found.push(
      finding('CLIENT_NAME_SCOPE', 'core skill copy names an integration client', path),
    );
  }
  if (extname(path) === '.md') {
    const lines = source.trimEnd().split('\n').length;
    if (lines >= 200)
      found.push(finding('MARKDOWN_LINES', 'Markdown must stay below 200 lines', path));
    if (source.length >= 20_000) {
      found.push(
        finding('MARKDOWN_SIZE', 'Markdown must stay below 20,000 characters', path),
      );
    }
  }
  return found;
}

function duplicateBodies(entries: Array<{ hash: string; path: string }>): CopyFinding[] {
  const findings: CopyFinding[] = [];
  const owners = new Map<string, string>();
  for (const entry of entries) {
    const owner = owners.get(entry.hash);
    if (owner) {
      findings.push(
        finding('DUPLICATE_SKILL_BODY', `skill body duplicates ${owner}`, entry.path),
      );
    } else {
      owners.set(entry.hash, entry.path);
    }
  }
  return findings;
}

export async function validateCopy(root: string): Promise<CopyReport> {
  const paths = await files(root);
  const findings: CopyFinding[] = [];
  const skillFiles: string[] = [];
  const bodies: Array<{ hash: string; path: string }> = [];
  let inspected = 0;
  for (const absolute of paths) {
    const path = portable(root, absolute);
    if (absolute.endsWith('/SKILL.md') || path === 'SKILL.md') {
      skillFiles.push(path);
      if (!path.startsWith('skills/')) {
        findings.push(
          finding('DUPLICATE_SKILL_LOCATION', 'SKILL.md must live below skills/', path),
        );
      }
      const source = await readFile(absolute, 'utf8');
      bodies.push({ hash: createHash('sha256').update(source).digest('hex'), path });
    }
    if (!publicExtensions.has(extname(path))) continue;
    inspected += 1;
    findings.push(...scanText(path, await readFile(absolute, 'utf8')));
  }
  findings.push(...duplicateBodies(bodies));
  return {
    findings,
    inspected_files: inspected,
    skill_files: skillFiles.sort(),
    status: findings.length === 0 ? 'PASS' : 'FAIL',
  };
}
