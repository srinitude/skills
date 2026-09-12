"""The current ledger method must reach a standardized body before its consumers."""
import sys
import unittest
from cli import SCRIPTS

sys.path.insert(0, str(SCRIPTS))

from standardization_markdown import contract_section, rewrite_markdown, rewrite_script_text
from standardization_render import body_policies
from standardization_discovery import enrich_content

FACTORY = SCRIPTS.parent
PREFIXES = (
    '**Start here.**', '**Reusable ledger artifact, owned here.**',
    '**Relationship records.**', '| Relationship family |',
    '**Dependency contract.**', '**Order and invalidation.**',
    '**Required initial context.**', '**Traverse, work and check.**',
)
DOMAIN = 'Return the observed local ISO timestamp and its UTC offset.'
HEADER = '---\nname: clock-anchor\ndescription: "Use when a timestamp is needed."\n---\n'


def expected_blocks():
    blocks = (FACTORY / 'assets/skill-template.md').read_text().split('\n\n')
    return [next(block for block in blocks if block.startswith(prefix)) for prefix in PREFIXES]


def original_body():
    return HEADER + '# Clock anchor\n\n' + DOMAIN + '\n\n' + contract_section({
        'primary_term': 'clock anchor', 'main_task': 'anchor', 'outcome': DOMAIN})


def _TestStandardizationLedgerBody_test_complete_current_ledger_blocks_precede_domain_action(self):
    original = original_body()
    actual = body_policies(original, FACTORY)
    self.assertTrue(actual.startswith(HEADER))
    positions = []
    for block in expected_blocks():
        self.assertEqual(actual.count(block), 1, block.splitlines()[0])
        positions.append(actual.index(block))
    self.assertEqual(positions, sorted(positions))
    self.assertLess(positions[-1], actual.index(DOMAIN))
    self.assertIn(original.removeprefix(HEADER), actual)
    self.assertEqual(body_policies(actual, FACTORY), actual)

def _TestStandardizationLedgerBody_test_custom_ledger_policy_requires_explicit_migration(self):
    custom = '**Relationship records.** Keep a project-specific exception.'
    original = original_body() + '\n' + custom + '\n'
    with self.assertRaisesRegex(ValueError, 'reviewed.*migration'):
        body_policies(original, FACTORY)

def _TestStandardizationLedgerBody_test_stale_relation_table_cannot_hide_behind_its_current_heading(self):
    table = expected_blocks()[3]
    stale = table.replace('`excepts`, ', '')
    self.assertNotEqual(table, stale)
    with self.assertRaisesRegex(ValueError, 'reviewed.*migration'):
        body_policies(original_body() + '\n' + stale + '\n', FACTORY)

def _TestStandardizationLedgerBody_test_complete_rewrite_cycle_keeps_current_policies_and_owner_links(self):
    profile = {'primary_term': 'clock anchor', 'main_task': 'anchor', 'outcome': DOMAIN}
    initial = rewrite_markdown(original_body(), {}, profile, True)
    first = body_policies(initial, FACTORY)
    second = body_policies(rewrite_markdown(first, {}, profile, True), FACTORY)
    self.assertEqual(second, first)
    self.assertIn('[context reader](scripts/agentic_context.py)', second)

def _TestStandardizationLedgerBody_test_standardized_body_loads_its_shipped_reference_and_example_owners(self):
    profile = {'primary_term': 'clock anchor', 'main_task': 'anchor', 'outcome': DOMAIN}
    first = rewrite_markdown(original_body(), {}, profile, True)
    for owner in ['references/generation-contract.md', 'examples/example-ledger-write.md']:
        self.assertIn(owner, first)
        self.assertTrue((FACTORY / owner).is_file())
    self.assertIn('before accepting', first)
    self.assertIn('before a file change', first)
    self.assertEqual(rewrite_markdown(first, {}, profile, True), first)

def _TestStandardizationLedgerBody_test_descriptive_owner_link_keeps_its_existing_public_route(self):
    text = 'Use [the context reader](scripts/agentic_context.py) through `mise run agentic-request`.'
    self.assertEqual(rewrite_script_text(text, {}), text)

def _TestStandardizationLedgerBody_test_owner_links_do_not_invent_executable_tasks_on_the_next_update(self):
    profile = {'primary_term': 'clock anchor', 'main_task': 'anchor', 'outcome': DOMAIN}
    body = body_policies(original_body(), FACTORY)
    files = {'SKILL.md': body.encode(), 'scripts/agentic_context.py': b'"""Library owner."""',
             'mise.toml': b'[tasks.anchor]\nrun = "python3 scripts/anchor.py"\n'}
    actual = enrich_content(files, profile)
    self.assertNotIn('agentic-context', actual['script_tasks'])
    self.assertNotIn('agentic-context', actual['public_tasks'])

def _TestStandardizationLedgerBody_test_quoted_policy_examples_do_not_become_operative_rules(self):
    quoted = '```text\n**Relationship records.** A rejected example.\n```'
    actual = body_policies(original_body() + '\n' + quoted + '\n', FACTORY)
    self.assertIn(quoted, actual)
    self.assertIn(expected_blocks()[2], actual)


class TestStandardizationLedgerBody(unittest.TestCase):
    test_complete_current_ledger_blocks_precede_domain_action = _TestStandardizationLedgerBody_test_complete_current_ledger_blocks_precede_domain_action
    test_custom_ledger_policy_requires_explicit_migration = _TestStandardizationLedgerBody_test_custom_ledger_policy_requires_explicit_migration
    test_stale_relation_table_cannot_hide_behind_its_current_heading = _TestStandardizationLedgerBody_test_stale_relation_table_cannot_hide_behind_its_current_heading
    test_complete_rewrite_cycle_keeps_current_policies_and_owner_links = _TestStandardizationLedgerBody_test_complete_rewrite_cycle_keeps_current_policies_and_owner_links
    test_standardized_body_loads_its_shipped_reference_and_example_owners = _TestStandardizationLedgerBody_test_standardized_body_loads_its_shipped_reference_and_example_owners
    test_descriptive_owner_link_keeps_its_existing_public_route = _TestStandardizationLedgerBody_test_descriptive_owner_link_keeps_its_existing_public_route
    test_owner_links_do_not_invent_executable_tasks_on_the_next_update = _TestStandardizationLedgerBody_test_owner_links_do_not_invent_executable_tasks_on_the_next_update
    test_quoted_policy_examples_do_not_become_operative_rules = _TestStandardizationLedgerBody_test_quoted_policy_examples_do_not_become_operative_rules


class TestWholeDirectoryPolicy(unittest.TestCase):
    def test_policy_reaches_initial_body_and_scaffold_source(self):
        from scaffold_skill import FILLED
        self.assertIn(('SKILL.md', 'skill-template.md'), FILLED)
        actual = body_policies(original_body(), FACTORY)
        for phrase in ['**File graph.**', 'all authorized specifications for this skill',
                       'every existing file', 'baseline and added file',
                       'Unjustified changes remain unresolved',
                       'cosmetic churn do not prove implementation']:
            self.assertIn(phrase, actual)
            self.assertLess(actual.index(phrase), actual.index(DOMAIN))
        self.assertNotIn('goal documents', actual)
        self.assertEqual(body_policies(actual, FACTORY), actual)

    def test_weakened_graph_policy_requires_reviewed_migration(self):
        actual = body_policies(original_body(), FACTORY)
        weakened = actual.replace('every existing file', 'selected files')
        self.assertNotEqual(weakened, actual)
        with self.assertRaisesRegex(ValueError, 'reviewed.*migration'):
            body_policies(weakened, FACTORY)


if __name__ == '__main__':
    unittest.main()
