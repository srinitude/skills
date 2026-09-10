"""Actual minimal ledger fixtures for scaffold boundary tests; no accepted meaning claim."""
import json
import unittest
from pathlib import Path

from cli import run
from test_review_ledger_write import TestLedgerWrite, sha


def review_fixture(owner, plan):
    case = TestLedgerWrite()
    case.setUp()
    owner.addCleanup(case.doCleanups)
    context = {key: case.request[key] for key in
               ('ledger', 'ledger_sha256', 'expected_documents', 'original_source', 'inventory_document')}
    body = next(item for item in plan['files'] if item['path'] == 'SKILL.md')
    initial = {'candidate_sha256': body['sha256'], 'previous_sha256': None,
               'ledger_sha256': context['ledger_sha256'], 'source_sha256': case.data['source']['sha256'],
               'execution_acceptance': 'pending', 'initial_contract_validation': {
                   'state': 'PASS', 'reviewer': 'Test author; non-independent fixture declaration',
                   'method': 'The fixture requires full source reads and per-file body/contribution declarations.',
                   'limit': 'The seeded body is not a domain-accepted skill or human-reviewed artifact.'}}
    body_review = case.folder / 'initial-body-review.json'
    body_review.write_text(json.dumps(initial))
    record = {'plan_sha256': sha(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode()),
              'context': context, 'body_review': {'path': str(body_review), 'sha256': sha(body_review.read_bytes())},
              'files': {item['path']: {'reviewer': 'Test author; fixture only', 'review': {
                  'Contribution': 'Create the exact planned test fixture file ' + item['path'],
                  'Body decision': 'The planned body declares full ledger reads; seeded domain acceptance stays pending.'}}
                        for item in plan['files']}}
    path = case.folder / 'scaffold-review.json'
    path.write_text(json.dumps(record))
    return path, record, case


def reviewed_scaffold(dest, name, description, extra):
    args = ('--name', name, '--description', description, '--dest', dest, *extra)
    result = run('scaffold_skill.py', *args, '--plan')
    if result.returncode:
        return result
    owner = unittest.TestCase()
    try:
        path, _, _ = review_fixture(owner, json.loads(result.stdout))
        return run('scaffold_skill.py', *args, '--review', path)
    finally:
        owner.doCleanups()
