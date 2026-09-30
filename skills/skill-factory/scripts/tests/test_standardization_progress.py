"""Public output rewriting must carry broad work, owned repair and final proof."""
import sys
import unittest
from cli import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from standardization_markdown import rewrite_markdown, contract_resources, RESOURCE_OWNERS

PROFILE = {'primary_term': 'clock anchor', 'main_task': 'anchor',
           'outcome': 'Return the observed local ISO timestamp and its UTC offset.'}
PREFIX = '# Clock anchor\n\nKeep the UTC offset in every result.\n'
SUFFIX = '\n## Domain limits\n\nNever guess the time.\n'
LEGACY = '''
## Factory execution contract

The accepted outcome is: Return the observed local ISO timestamp and its UTC offset. Preserve current clock anchor behavior while changing its smallest owner.

1. Freeze the current package with `mise run ci` and record its digest.
2. Run `mise run domain-research-policy`, then judge the current clock anchor sources and counterevidence.
3. Run `mise run anchor` for the named clock anchor operation. Keep semantic choices with the model.
4. Run `mise run decision-policy`, `mise run ci`, and the behavioral evals. Return to the lowest failed owner.
5. Run `mise run invocation-policy -- <receipt>` and account for every task or its domain-specific non-use.
6. Optionally run `mise run improvement-policy`. Keep one changed dimension only if no protected dimension regresses.

Mise owns repeatable mechanics, ordering, receipts, and checks. The model owns interpretation, causal judgment, creative work, and direct perception that code cannot supply. Stop on missing authority, stale evidence, or a failed gate.
'''


def rewrite(body):
    return rewrite_markdown(body, {}, PROFILE, True)


def check_progress(self, actual):
    self.assertIn(PROFILE['outcome'], actual)
    self.assertIn('mise run anchor', actual)
    broad = actual.index('Build broad working paths')
    repair = actual.index('Switch to precise repair')
    final = actual.index('Before acceptance')
    self.assertLess(broad, repair)
    self.assertLess(repair, final)
    self.assertIn('mise run ci', actual[final:])
    self.assertIn('behavioral evals', actual[final:])
    self.assertIn('safety, authority, data integrity', actual)
    self.assertNotIn('Freeze the current package with', actual)
    self.assertNotIn('changing its smallest owner', actual)


def test_legacy_migration(self):
    for resources in ['', contract_resources() + '\n' + RESOURCE_OWNERS + '\n']:
        original = LEGACY.replace('\nMise owns', '\n' + resources + 'Mise owns')
        result = rewrite(PREFIX + original + SUFFIX)
        check_progress(self, result)
        self.assertTrue(result.startswith(PREFIX))
        self.assertTrue(result.endswith(SUFFIX))
        self.assertEqual(rewrite(result), result)


def test_custom_contract_needs_review(self):
    for addition in ['Keep a custom rule.\n', '```text\nKeep a custom rule.\n```\n']:
        with self.assertRaisesRegex(ValueError, 'reviewed.*migration'):
            rewrite(PREFIX + LEGACY + addition + SUFFIX)


def test_quoted_heading_is_not_a_contract(self):
    for quoted in ['```text\n## Factory execution contract\n```\n',
                   '    ## Factory execution contract\n',
                   '> ## Factory execution contract\n']:
        result = rewrite(PREFIX + '\n' + quoted)
        self.assertIn(quoted, result)
        check_progress(self, result)
        self.assertEqual(rewrite(result), result)


def test_duplicate_contract_needs_review(self):
    with self.assertRaisesRegex(ValueError, 'reviewed.*migration'):
        rewrite(PREFIX + LEGACY + LEGACY)


def test_render_pipeline_keeps_domain_and_reference_owners(self):
    from standardization_fixtures import profile
    from test_standardization_rules import updated
    files = updated()
    body = files['SKILL.md'].decode()
    self.assertIn('Build broad working paths', body)
    self.assertIn('Never infer a missing UTC offset.', body)
    self.assertEqual(updated(files), files)
    start = body.index('## Factory execution contract')
    end = body.index('\n[', start)
    old = LEGACY.replace(PROFILE['outcome'], profile()['outcome']).lstrip('\n')
    files['SKILL.md'] = (body[:start] + old + '\n' + body[end:]).encode()
    before = dict(files)
    result = updated(files)
    self.assertEqual(files, before)
    self.assertIn('Switch to precise repair', result['SKILL.md'].decode())
    self.assertEqual(updated(result), result)


class TestOutputProgress(unittest.TestCase):
    test_render_pipeline_keeps_domain_and_reference_owners = test_render_pipeline_keeps_domain_and_reference_owners
    test_legacy_migration = test_legacy_migration
    test_custom_contract_needs_review = test_custom_contract_needs_review
    test_quoted_heading_is_not_a_contract = test_quoted_heading_is_not_a_contract
    test_duplicate_contract_needs_review = test_duplicate_contract_needs_review

    def test_new_output_has_a_repair_path_and_full_proof(self):
        result = rewrite(PREFIX)
        check_progress(self, result)
        self.assertEqual(rewrite(result), result)


if __name__ == '__main__':
    unittest.main()
