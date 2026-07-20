import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

import { validateRepository } from './repository-validation.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

test('validates every skill and all frozen specification pages', async () => {
  const report = await validateRepository(root);

  expect(report).toMatchObject({
    errors: [],
    skillCount: 1,
    sourcePageCount: 9,
    status: 'PASS',
    version: '0.1.0',
  });
  expect(report.skills).toEqual([
    expect.objectContaining({ name: 'starting-point', status: 'PASS', version: '0.1.0' }),
  ]);
});
