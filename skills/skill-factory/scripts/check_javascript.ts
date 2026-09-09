/** Syntax-based size checks only. Runtime behavior and type checks are separate. */
import { readFileSync } from 'node:fs';
import ts from 'typescript';
import { z } from 'zod';

const request = z.object({
  files: z.array(z.string().min(1)).min(1),
  file: z.number().int().positive(),
  construct: z.number().int().positive(),
  depth: z.number().int().nonnegative(),
}).strict();
type Limits = z.infer<typeof request>;
const blocks = new Set([
  ts.SyntaxKind.IfStatement, ts.SyntaxKind.ForStatement,
  ts.SyntaxKind.ForInStatement, ts.SyntaxKind.ForOfStatement,
  ts.SyntaxKind.WhileStatement, ts.SyntaxKind.DoStatement,
  ts.SyntaxKind.TryStatement, ts.SyntaxKind.SwitchStatement,
  ts.SyntaxKind.WithStatement,
]);

function isConstruct(node: ts.Node) {
  return ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node)
    || ts.isArrowFunction(node) || ts.isMethodDeclaration(node)
    || ts.isConstructorDeclaration(node) || ts.isGetAccessorDeclaration(node)
    || ts.isSetAccessorDeclaration(node) || ts.isClassDeclaration(node)
    || ts.isClassExpression(node);
}

function codeLines(node: ts.Node, source: ts.SourceFile, own: boolean, root = true): Set<number> {
  const lines = new Set<number>();
  if (node.kind === ts.SyntaxKind.JSDocComment || node.kind === ts.SyntaxKind.EndOfFileToken
      || (own && !root && isConstruct(node))) return lines;
  const children = node.getChildren(source);
  if (children.length) {
    for (const child of children) {
      for (const line of codeLines(child, source, own, false)) lines.add(line);
    }
  } else if (node.getEnd() > node.getStart(source)) {
    const first = source.getLineAndCharacterOfPosition(node.getStart(source)).line;
    const last = source.getLineAndCharacterOfPosition(node.getEnd() - 1).line;
    for (let line = first; line <= last; line++) lines.add(line);
  }
  return lines;
}

function blockDepth(node: ts.Node): number {
  let deepest = 0;
  ts.forEachChild(node, child => {
    const extra = isConstruct(child) || blocks.has(child.kind) ? 1 : 0;
    deepest = Math.max(deepest, blockDepth(child) + extra);
  });
  return deepest;
}

function checkConstructs(node: ts.Node, source: ts.SourceFile, limits: Limits, problems: string[]) {
  if (isConstruct(node)) {
    const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
    const location = `${source.fileName}:${line}: ${ts.SyntaxKind[node.kind]}`;
    const count = codeLines(node, source, true).size;
    if (count > limits.construct) problems.push(`${location} has ${count} own code lines; cap is ${limits.construct}`);
    if (!ts.isClassDeclaration(node) && !ts.isClassExpression(node)) {
      const depth = blockDepth(node);
      if (depth > limits.depth) problems.push(`${location} nesting is ${depth}; cap is ${limits.depth}`);
    }
  }
  ts.forEachChild(node, child => { checkConstructs(child, source, limits, problems); });
}

function checkFiles(limits: Limits) {
  const problems: string[] = [];
  const program = ts.createProgram(limits.files, {
    allowJs: true, noEmit: true, noResolve: true, noLib: true, jsx: ts.JsxEmit.Preserve,
  });
  for (const path of limits.files) {
    const source = program.getSourceFile(path);
    if (!source) throw new Error(`compiler did not load source: ${path}`);
    const errors = program.getSyntacticDiagnostics(source);
    for (const error of errors) {
      problems.push(`${path}: does not parse: ${ts.flattenDiagnosticMessageText(error.messageText, '\n')}`);
    }
    const count = codeLines(source, source, false).size;
    if (count > limits.file) problems.push(`${path}: ${count} code lines; cap is ${limits.file}`);
    if (!errors.length) checkConstructs(source, source, limits, problems);
  }
  return problems;
}

try {
  const data: unknown = JSON.parse(readFileSync(0, 'utf8'));
  const problems = checkFiles(request.parse(data));
  process.stdout.write(JSON.stringify(problems) + '\n');
  process.exitCode = problems.length ? 1 : 0;
} catch (error) {
  process.stderr.write(`JavaScript/TypeScript checker error: ${String(error)}\n`);
  process.exitCode = 2;
}
