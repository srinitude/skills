/** Physical source limits only. Runtime behavior and type checks are separate. */
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
    || ts.isClassExpression(node) || ts.isInterfaceDeclaration(node)
    || ts.isEnumDeclaration(node) || ts.isTypeAliasDeclaration(node);
}

function children(node: ts.Node) {
  const result: ts.Node[] = [];
  ts.forEachChild(node, child => { result.push(child); });
  return result;
}

function physicalLines(text: string) {
  if (!text.length) return 0;
  const normalized = text.replaceAll('\r\n', '\n');
  const separators = new Set('\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029');
  let count = 1;
  for (const character of normalized) count += Number(separators.has(character));
  return count - Number(separators.has(normalized.at(-1)!));
}

function wholeLines(node: ts.Node, source: ts.SourceFile) {
  return physicalLines(source.text.slice(node.getStart(source), node.getEnd()));
}

function blockDepth(root: ts.Node) {
  let deepest = 0;
  const pending: [ts.Node, number][] = [[root, 0]];
  while (pending.length) {
    const [node, depth] = pending.pop()!;
    const following = children(node).map(child => {
      const peer = ts.isIfStatement(node) && ts.isIfStatement(child) && node.elseStatement === child;
      const level = depth + Number(!peer && (isConstruct(child) || blocks.has(child.kind)));
      deepest = Math.max(deepest, level);
      return [child, level] as [ts.Node, number];
    });
    pending.push(...following);
  }
  return deepest;
}

function checkConstructs(source: ts.SourceFile, limits: Limits, problems: string[]) {
  const pending: ts.Node[] = [source];
  while (pending.length) {
    const node = pending.pop()!;
    const count = isConstruct(node) ? wholeLines(node, source) : 0;
    if (count > limits.construct) {
      const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
      problems.push(`${source.fileName}:${line}: ${ts.SyntaxKind[node.kind]} has ${count} physical lines; cap is ${limits.construct}`);
    }
    pending.push(...children(node));
  }
}

function checkSource(program: ts.Program, path: string, limits: Limits) {
  const source = program.getSourceFile(path);
  if (!source) throw new Error(`compiler did not load source: ${path}`);
  const errors = program.getSyntacticDiagnostics(source);
  const problems = errors.map(error => `${path}: does not parse: ${ts.flattenDiagnosticMessageText(error.messageText, '\n')}`);
  const count = physicalLines(source.text);
  if (count > limits.file) problems.push(`${path}: ${count} physical lines; cap is ${limits.file}`);
  if (errors.length) return problems;
  const depth = blockDepth(source);
  if (depth > limits.depth) problems.push(`${path}: file nesting is ${depth}; cap is ${limits.depth}`);
  checkConstructs(source, limits, problems);
  return problems;
}

function checkFiles(limits: Limits) {
  const program = ts.createProgram(limits.files, {
    allowJs: true, noEmit: true, noResolve: true, noLib: true, jsx: ts.JsxEmit.Preserve,
  });
  return limits.files.flatMap(path => checkSource(program, path, limits));
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
