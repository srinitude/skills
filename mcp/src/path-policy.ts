import { readFile, realpath } from 'node:fs/promises';
import { isAbsolute, join, relative } from 'node:path';

export type PathPolicyCode =
  | 'ABSOLUTE_PATH'
  | 'HIDDEN_PATH'
  | 'INVALID_PATH'
  | 'INVALID_SKILL_NAME'
  | 'NOT_FOUND'
  | 'PATH_TRAVERSAL'
  | 'SYMLINK_ESCAPE';

export class PathPolicyError extends Error {
  constructor(
    readonly code: PathPolicyCode,
    message: string,
  ) {
    super(message);
    this.name = 'PathPolicyError';
  }
}

function inside(parent: string, child: string): boolean {
  const difference = relative(parent, child);
  return difference === '' || (!difference.startsWith('..') && !isAbsolute(difference));
}

function validateSkillName(name: string): void {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name) || name.length > 64) {
    throw new PathPolicyError('INVALID_SKILL_NAME', 'skill name is invalid');
  }
}

function validateRelativePath(path: string): string[] {
  if (isAbsolute(path))
    throw new PathPolicyError('ABSOLUTE_PATH', 'absolute paths are forbidden');
  if (path.includes('\\'))
    throw new PathPolicyError('INVALID_PATH', 'backslashes are forbidden');
  const segments = path.split('/');
  if (segments.some((segment) => segment === '' || segment === '.' || segment === '..')) {
    throw new PathPolicyError('PATH_TRAVERSAL', 'path traversal is forbidden');
  }
  if (segments.some((segment) => segment.startsWith('.'))) {
    throw new PathPolicyError('HIDDEN_PATH', 'hidden paths are forbidden');
  }
  return segments;
}

async function resolveExisting(path: string): Promise<string> {
  try {
    return await realpath(path);
  } catch {
    throw new PathPolicyError('NOT_FOUND', 'requested file was not found');
  }
}

export async function readSkillFile(
  root: string,
  skillName: string,
  requestedPath: string,
): Promise<string> {
  validateSkillName(skillName);
  const segments = validateRelativePath(requestedPath);
  const skillsRoot = await resolveExisting(join(root, 'skills'));
  const skillRoot = await resolveExisting(join(skillsRoot, skillName));
  if (!inside(skillsRoot, skillRoot)) {
    throw new PathPolicyError('SYMLINK_ESCAPE', 'skill root leaves the skills directory');
  }
  const target = await resolveExisting(join(skillRoot, ...segments));
  if (!inside(skillRoot, target)) {
    throw new PathPolicyError('SYMLINK_ESCAPE', 'file target leaves the skill directory');
  }
  return readFile(target, 'utf8');
}
