"""Document guards for inherited ordering and relation vocabulary, not execution proof."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / 'assets/skill-template.md'
PHASES = ['Frame and resolve', 'Inspect and prepare',
          'Reconcile the governing ledger', 'Freeze the executable change plan',
          'Implement the selected operation', 'Prove the integrated result',
          'Account for the invocation', 'Maintain and deliver']
RELATIONS = '''part-of contextualizes defines references equivalent-under distinct-from
refines example-of qualifies excepts contradicts supersedes preserves requires-all
requires-alternative requires-exclusive-choice conditional-on forbids permits
must-be-absent motivates advances prevents protects tradeoff-with reinforces
interacts-with read-before executes-before gates-effect gates-acceptance
remains-available exclusive-access feedback-to parallel-with definition-owned-by
execution-owned-by authorized-by state-owned-by accepted-by maintained-by reads
writes consumes produces hands-off-to bound-to proves falsifies calibrates
invalidates recovers restores tests compares-with generates copies-from adapts
independent-variant-of refreshes body-represents change-reviews-body initially-loads
conditionally-loads delivers alias-of broader-than narrower-than related-concept
identical-to approximately-corresponds causally-influences higher-order-interaction
selected-from'''.split()


class TestTemplateDependencyOrder(unittest.TestCase):
    def test_foundation_and_plan_precede_development_and_acceptance(self):
        text = TEMPLATE.read_text(encoding='utf-8')
        steps = text.split('## Steps\n', 1)[1].split('## Assets\n', 1)[0]
        labels = re.findall(r'^\d+\. \*\*(.+?)\.\*\*', steps, re.M)
        self.assertEqual(labels, PHASES)
        foundation = steps.split('3. **', 1)[1].split('4. **', 1)[0]
        for phrase in ['source-to-ledger', 'ledger-to-source', 'initial contract',
                       'before final acceptance', 'frozen acceptance']:
            self.assertIn(phrase, foundation)
        implementation = steps.split('5. **', 1)[1].split('6. **', 1)[0]
        for phrase in ['before and after', 'every individual', 'repeat writes',
                       'current body', 'BOOTSTRAP, RED, GREEN, REFACTOR']:
            self.assertIn(phrase, implementation)

    def test_preconditions_are_owned_before_the_numbered_consumers(self):
        text = TEMPLATE.read_text(encoding='utf-8')
        boundary = text.index('## Steps\n')
        for label in ['Implement software for this outcome.',
                      'Verify every consumed language/interface.',
                      'Preserve change and variant boundaries.',
                      'Human input and recovery.', 'Reject purpose-defeating defaults.']:
            self.assertEqual(text.count(f'**{label}**'), 1)
            self.assertLess(text.index(f'**{label}**'), boundary)
        self.assertIn('Silence, notification, timeout and defaults are not input.', text)
        self.assertIn('Use realistic participant tasks', text)

    def test_complete_relationship_vocabulary_is_in_both_initial_bodies(self):
        self.assertEqual(len(RELATIONS), 74)
        for path in [ROOT / 'SKILL.md', TEMPLATE]:
            text = path.read_text(encoding='utf-8')
            initial = text.split('## Mise task graph\n', 1)[0]
            for relation in RELATIONS:
                with self.subTest(path=path.name, relation=relation):
                    self.assertIn(f'`{relation}`', initial)


if __name__ == '__main__':
    unittest.main()
