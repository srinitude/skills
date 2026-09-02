import type { SmokeContext } from './client-smoke-types.js';
import { command, isolatedHome, requireText } from './client-smoke-utils.js';

async function claude(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-claude');
  await command(
    'claude',
    ['plugin', 'validate', '--strict', context.archiveRoot],
    context.archiveRoot,
    home,
  );
  await command(
    'claude',
    ['plugin', 'marketplace', 'add', context.archiveRoot],
    context.archiveRoot,
    home,
  );
  await command(
    'claude',
    ['plugin', 'install', 'srinitude-skills@srinitude-skills'],
    context.archiveRoot,
    home,
  );
  const output = await command(
    'claude',
    ['plugin', 'list', '--json'],
    context.archiveRoot,
    home,
  );
  requireText(output, 'srinitude-skills', 'Claude Code');
  return 'Claude Code validated and cold-installed the archive plugin';
}

async function codex(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-codex');
  const base = ['-y', '@openai/codex@latest', 'plugin'];
  await command(
    'npx',
    [...base, 'marketplace', 'add', context.archiveRoot],
    context.archiveRoot,
    home,
  );
  await command(
    'npx',
    [...base, 'add', 'srinitude-skills@srinitude-skills'],
    context.archiveRoot,
    home,
  );
  const output = await command('npx', [...base, 'list'], context.archiveRoot, home);
  requireText(output, 'srinitude-skills', 'Codex');
  return 'Current Codex cold-installed the archive marketplace plugin';
}

async function gemini(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-gemini');
  await command(
    'gemini',
    ['extensions', 'validate', context.archiveRoot],
    context.archiveRoot,
    home,
  );
  await command(
    'gemini',
    ['extensions', 'install', context.archiveRoot, '--consent'],
    context.archiveRoot,
    home,
  );
  const output = await command('gemini', ['extensions', 'list'], context.archiveRoot, home);
  requireText(output, 'srinitude-skills', 'Gemini CLI');
  return 'Gemini CLI validated and cold-installed the archive extension';
}

async function hermes(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-hermes');
  const output = await command(
    'hermes',
    ['plugins', 'doctor', '--ci', context.archiveRoot],
    context.archiveRoot,
    home,
  );
  requireText(output, 'srinitude-skills', 'Hermes Agent');
  return 'Hermes Agent loaded and validated the archive plugin with its real runtime';
}

async function openclaw(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-openclaw');
  const base = ['-y', 'openclaw@latest', 'plugins'];
  await command(
    'npx',
    [...base, 'install', context.tarball, '--force', '--accept-capabilities'],
    context.archiveRoot,
    home,
  );
  const output = await command(
    'npx',
    [...base, 'inspect', 'srinitude-skills'],
    context.archiveRoot,
    home,
  );
  requireText(output, 'srinitude-skills', 'OpenClaw');
  requireText(output, 'mcp', 'OpenClaw');
  return 'Current OpenClaw cold-installed and inspected the Codex-compatible bundle';
}

async function opencode(context: SmokeContext): Promise<string> {
  const home = await isolatedHome('skills-opencode');
  const output = await command(
    'npx',
    ['-y', 'opencode-ai@latest', 'mcp', 'list'],
    context.archiveRoot,
    home,
  );
  requireText(output, 'srinitude-skills', 'opencode');
  requireText(output, 'connected', 'opencode');
  return 'Current opencode started the archive MCP route and reported connected';
}

export const agentRouteProofs = {
  'claude-code': claude,
  codex,
  'gemini-cli': gemini,
  'hermes-agent': hermes,
  openclaw,
  opencode,
};
