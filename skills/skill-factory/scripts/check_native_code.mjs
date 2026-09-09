/** Parse JavaScript and TypeScript with the pinned compiler and measure syntax. */
/* global console, process */
import { readFileSync } from 'node:fs';
import ts from 'typescript';

const MAX_FILE = 200;
const MAX_CONSTRUCT = 30;
const MAX_DEPTH = 3;
const BLOCKS = new Set([
  ts.SyntaxKind.IfStatement, ts.SyntaxKind.ForStatement,
  ts.SyntaxKind.ForInStatement, ts.SyntaxKind.ForOfStatement,
  ts.SyntaxKind.WhileStatement, ts.SyntaxKind.DoStatement,
  ts.SyntaxKind.SwitchStatement, ts.SyntaxKind.TryStatement,
]);

function construct(node) {
  return ts.isFunctionLike(node) || ts.isClassDeclaration(node) || ts.isClassExpression(node);
}

function children(node) {
  const result = [];
  ts.forEachChild(node, child => { result.push(child); });
  return result;
}

function tokens(node, source, result = []) {
  const inner = node.getChildren(source);
  if (inner.length) inner.forEach(child => tokens(child, source, result));
  else if (![ts.SyntaxKind.EndOfFileToken, ts.SyntaxKind.SyntaxList].includes(node.kind)) {
    result.push([node.getStart(source), node.end]);
  }
  return result;
}

function nested(node) {
  return children(node).flatMap(child => construct(child) ? [child] : nested(child));
}

function lines(source, spans, start = 0, end = source.end, excluded = []) {
  const found = new Set();
  for (const [a, b] of spans) {
    if (a < start || b > end || excluded.some(node => a >= node.pos && b <= node.end)) continue;
    const first = source.getLineAndCharacterOfPosition(a).line;
    const last = source.getLineAndCharacterOfPosition(Math.max(a, b - 1)).line;
    for (let line = first; line <= last; line += 1) found.add(line);
  }
  return found.size;
}

function depth(node) {
  return Math.max(0, ...children(node).map(child =>
    depth(child) + (BLOCKS.has(child.kind) || construct(child) ? 1 : 0)));
}

function checkConstructs(node, source, spans, problems) {
  if (construct(node)) {
    const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
    const name = node.name?.getText(source) || ts.SyntaxKind[node.kind];
    const count = lines(source, spans, node.getStart(source), node.end, nested(node));
    if (count > MAX_CONSTRUCT) problems.push(`${source.fileName}:${line}: ${name} has ${count} lines; cap is ${MAX_CONSTRUCT}`);
    if (ts.isFunctionLike(node) && depth(node) > MAX_DEPTH) {
      problems.push(`${source.fileName}:${line}: ${name} nesting is ${depth(node)}; cap is ${MAX_DEPTH}`);
    }
  }
  children(node).forEach(child => checkConstructs(child, source, spans, problems));
}

function inspect(files) {
  const program = ts.createProgram(files, {
    allowJs: true, noResolve: true, noLib: true, noEmit: true, types: [],
    target: ts.ScriptTarget.ESNext, jsx: ts.JsxEmit.Preserve,
  });
  const problems = program.getSyntacticDiagnostics().map(diagnostic => {
    const line = diagnostic.file?.getLineAndCharacterOfPosition(diagnostic.start || 0).line;
    return `${diagnostic.file?.fileName || 'compiler'}:${(line ?? 0) + 1}: ${ts.flattenDiagnosticMessageText(diagnostic.messageText, ' ')}`;
  });
  for (const path of files) {
    const source = program.getSourceFile(path);
    if (!source) throw new Error(`compiler did not read ${path}`);
    const spans = tokens(source, source);
    const count = lines(source, spans);
    if (count > MAX_FILE) problems.push(`${path}: ${count} lines of code; cap is ${MAX_FILE}`);
    checkConstructs(source, source, spans, problems);
  }
  return { files, compiler: ts.version, problems };
}

function main() {
  if (process.argv.slice(2).join(' ') === '--help') {
    console.log('Usage: check_native_code.mjs --files-from-stdin\nRead a JSON array of owned file paths.\nExit codes: 0 pass, 1 rejected, 2 usage.\nExample: feed ["scripts/workflow.ts"] on stdin.');
    return;
  }
  if (process.argv.slice(2).join(' ') !== '--files-from-stdin') {
    process.exitCode = 2;
    console.error('Expected --files-from-stdin; use --help.');
    return;
  }
  const files = JSON.parse(readFileSync(0, 'utf8'));
  if (!Array.isArray(files) || !files.every(path => typeof path === 'string' && path)) {
    throw new Error('file paths must be a JSON array of nonempty strings');
  }
  const report = inspect(files);
  console.log(JSON.stringify(report));
  process.exitCode = report.problems.length ? 1 : 0;
}

try { main(); }
catch (error) {
  console.error(String(error));
  process.exitCode = 1;
}
