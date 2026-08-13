import { cp, mkdir, mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

async function copyEvidence(root: string, fixture: string): Promise<void> {
  await mkdir(join(fixture, 'evidence', 'ports'), { recursive: true });
  await mkdir(join(fixture, 'skills'), { recursive: true });
  for (const file of ['agentskills-pages.json', 'skills-sh-pages.json']) {
    await cp(join(root, 'evidence', file), join(fixture, 'evidence', file));
  }
  await cp(
    join(root, 'skills', 'starting-point'),
    join(fixture, 'skills', 'starting-point'),
    {
      recursive: true,
    },
  );
  await cp(
    join(root, 'evidence', 'ports', 'starting-point'),
    join(fixture, 'evidence', 'ports', 'starting-point'),
    { recursive: true },
  );
}

async function createIndependentSkill(root: string, fixture: string): Promise<void> {
  const independent = join(fixture, 'skills', 'independent-skill');
  await cp(join(root, 'skills', 'starting-point'), independent, { recursive: true });
  const skill = await readFile(join(independent, 'SKILL.md'), 'utf8');
  await writeFile(
    join(independent, 'SKILL.md'),
    skill
      .replace('name: starting-point', 'name: independent-skill')
      .replace("version: '0.1.0'", "version: '7.4.2'"),
  );
  const cases = JSON.parse(
    await readFile(join(independent, 'evals', 'cases.json'), 'utf8'),
  );
  cases.skill = 'independent-skill';
  await writeFile(join(independent, 'evals', 'cases.json'), JSON.stringify(cases));
  const lineage = JSON.parse(
    await readFile(join(independent, 'evals', 'source-lineage.json'), 'utf8'),
  );
  lineage.public_version = '7.4.2';
  await writeFile(
    join(independent, 'evals', 'source-lineage.json'),
    JSON.stringify(lineage),
  );
}

async function createIndependentEvidence(root: string, fixture: string): Promise<void> {
  const source = join(root, 'evidence', 'ports', 'starting-point');
  const target = join(fixture, 'evidence', 'ports', 'independent-skill');
  await cp(source, target, { recursive: true });
  for (const file of ['source-manifest.json', 'source-archive.json']) {
    const path = join(target, file);
    const document = JSON.parse(await readFile(path, 'utf8'));
    document.skill = 'independent-skill';
    await writeFile(path, JSON.stringify(document));
  }
}

export async function createVersionFixture(root: string): Promise<string> {
  const fixture = await mkdtemp(join(tmpdir(), 'skills-version-independence-'));
  await copyEvidence(root, fixture);
  await createIndependentSkill(root, fixture);
  await createIndependentEvidence(root, fixture);
  await writeFile(
    join(fixture, 'package.json'),
    JSON.stringify({ name: 'version-fixture', version: '9.9.9' }),
  );
  return fixture;
}
