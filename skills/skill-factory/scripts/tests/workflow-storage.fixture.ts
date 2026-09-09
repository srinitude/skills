import { appendFile } from 'node:fs/promises';
import { z } from 'zod';

// Synthetic engine input probes. These values are not human decisions or authority.
process.env.MASTRA_TELEMETRY_DISABLED = '1';
const { createStep, createWorkflow } = await import('@mastra/core/workflows');
const { Mastra } = await import('@mastra/core/mastra');
const { LibSQLStore } = await import('@mastra/libsql');
const [, , mode, directory, runId, choice] = process.argv;
if (!directory || !runId) throw new Error('Expected mode, private test directory and run ID');
const shape = z.object({ count: z.number() });
const response = z.object({ proceed: z.boolean() }).strict();
const workflow = createWorkflow({
  id: 'persisted-engine-probe', inputSchema: shape, outputSchema: shape,
}).then(createStep({
  id: 'synthetic-gate', inputSchema: shape, outputSchema: shape,
  suspendSchema: z.object({ question: z.string() }), resumeSchema: response,
  execute: async ({ inputData, resumeData, suspend }) => {
    if (!resumeData) return suspend({ question: 'Synthetic resume probe' });
    if (!response.parse(resumeData).proceed) throw new Error('Synthetic rejection');
    return inputData;
  },
})).then(createStep({
  id: 'effect', inputSchema: shape, outputSchema: shape,
  execute: async ({ inputData }) => {
    await appendFile(directory + '/effects.txt', runId + '\n');
    return shape.parse({ count: inputData.count + 1 });
  },
})).commit();
const storage = new LibSQLStore({ id: 'test-storage', url: 'file:' + directory + '/runs.db' });
await storage.init();
new Mastra({ logger: false, storage, workflows: { 'persisted-engine-probe': workflow } });
try {
  const run = await workflow.createRun({ runId });
  const result = mode === 'start'
    ? await run.start({ inputData: { count: 0 } })
    : await run.resume({ step: 'synthetic-gate', resumeData: JSON.parse(choice || '{}') });
  const report = { status: result.status, result: result.status === 'success' ? result.result : null };
  if (mode === 'start' && process.send) {
    process.send(report);
    await new Promise(() => {});
  }
  console.log(JSON.stringify(report));
  process.exitCode = result.status === 'success' || result.status === 'suspended' ? 0 : 1;
} catch (error) {
  console.error(error instanceof Error ? error.message : 'Engine error');
  process.exitCode = 1;
} finally {
  await storage.close();
}
