import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

import { loadCatalog, type CatalogEntry } from '../../src/catalog.js';
import { readSkillFile } from './path-policy.js';
import { registerTools } from './tools.js';

function registerResources(server: McpServer, root: string, catalog: CatalogEntry[]): void {
  for (const entry of catalog) {
    const uri = `skill://${entry.name}/SKILL.md`;
    server.registerResource(
      `skill-${entry.name}`,
      uri,
      {
        description: entry.description,
        mimeType: 'text/markdown',
        title: entry.name,
      },
      async () => ({
        contents: [
          {
            mimeType: 'text/markdown',
            text: await readSkillFile(root, entry.name, 'SKILL.md'),
            uri,
          },
        ],
      }),
    );
  }
}

export async function createSkillServer(root: string): Promise<McpServer> {
  const catalog = await loadCatalog(root);
  const server = new McpServer({ name: 'srinitude-skills', version: '0.1.0' });
  registerResources(server, root, catalog);
  registerTools(server, root, catalog);
  return server;
}
