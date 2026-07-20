import type { EvalCase } from './schema.js';

export interface CriterionVerdict {
  criterion: string;
  observation: string;
  status: 'FAIL' | 'PASS';
}

export interface ScoreResult {
  required: CriterionVerdict[];
  status: 'FAIL' | 'PASS';
  veto: CriterionVerdict[];
}

function requiredVerdict(criterion: string, response: string): CriterionVerdict {
  const present = response.includes(criterion);
  return {
    criterion,
    observation: present ? 'Exact fixture criterion found.' : 'Fixture criterion missing.',
    status: present ? 'PASS' : 'FAIL',
  };
}

function vetoVerdict(criterion: string, response: string): CriterionVerdict {
  const present = response.includes(criterion);
  return {
    criterion,
    observation: present
      ? 'Forbidden fixture criterion found.'
      : 'Forbidden criterion absent.',
    status: present ? 'FAIL' : 'PASS',
  };
}

export function scoreFixtureResponse(testCase: EvalCase, response: string): ScoreResult {
  const required = testCase.required.map((criterion) =>
    requiredVerdict(criterion, response),
  );
  const veto = testCase.veto.map((criterion) => vetoVerdict(criterion, response));
  const status = [...required, ...veto].every((verdict) => verdict.status === 'PASS')
    ? 'PASS'
    : 'FAIL';
  return { required, status, veto };
}
