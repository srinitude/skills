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
const frozenEvidencePrefix = 'evidence/ports/';
const bannedTerms = /\b(herdr|humanize-writing|leverage)\b/i;
const audienceLabels =
  /\b(beginner|beginners|expert|experts|non-technical|novice|novices)\b/i;
const modelNames = /\b(Claude|DeepSeek|Gemini|GPT|Grok|Llama|Mistral|Qwen)\b/;

function isSourceProvenance(path: string): boolean {
  return /\/evals\/source-(lineage|mapping)\.json$/.test(path);
}

function portable(root: string, path: string): string {
  return relative(root, path).split('\\').join('/');
}

interface FileInventory {
  files: string[];
  special: string[];
}

async function files(root: string, directory = root): Promise<FileInventory> {
  const found: string[] = [];
  const special: string[] = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isDirectory() && ignoredDirectories.has(entry.name)) continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      const nested = await files(root, path);
      found.push(...nested.files);
      special.push(...nested.special);
    } else if (entry.isFile()) found.push(path);
    else special.push(path);
  }
  return { files: found.sort(), special: special.sort() };
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
    !isSourceProvenance(path) &&
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
  const inventory = await files(root);
  const paths = inventory.files;
  const findings: CopyFinding[] = [];
  const skillFiles: string[] = [];
  const bodies: Array<{ hash: string; path: string }> = [];
  let inspected = 0;
  for (const absolute of inventory.special) {
    findings.push(
      finding(
        'SPECIAL_ENTRY',
        'public copy contains a symlink or unsupported filesystem entry',
        portable(root, absolute),
      ),
    );
  }
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
    if (path.startsWith(frozenEvidencePrefix)) continue;
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
