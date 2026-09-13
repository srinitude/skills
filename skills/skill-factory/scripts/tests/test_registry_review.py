"""Real registry planning, review rejection, attribution and individual effects."""
import ast
import base64
from graphlib import TopologicalSorter
import copy
import json
import shutil
import unittest
from pathlib import Path

import refresh_registry_lineage as registry
import test_refresh_registry_lineage as fixtures
import test_review_ledger_write as ledger_cases
from standardization_test_support import native_formatter
from skill_package import inventory, sha


def _TestReviewedRegistry_setUp(self):
    ledger_cases.TestLedgerWrite.setUp(self)
    self.repo = self.folder / 'repository'; self.repo.mkdir()
    fixtures.TestRegistryLineageRefresh().fixture(self.repo, 'repository_baseline')
    self.root = self.repo / 'skills/clock-anchor'
    self.request['change']['body_sha256'] = sha((self.root / 'SKILL.md').read_bytes())
    self.request['initial_body_review'] = ledger_cases.initial_body_review(self)
    self.manifest = self.repo / 'evidence/ports/clock-anchor/source-manifest.json'
    self.review_path = self.folder / 'registry-request.json'

def _TestReviewedRegistry_prepare(self, item):
    request = copy.deepcopy(self.request)
    self.prepared.write_bytes(base64.b64decode(item['content_base64']))
    request['change'].update(path=item['path'], expected_sha256=item['expected_sha256'],
        new_file={'path':str(self.prepared), 'sha256':item['sha256']},
        mode={'expected':item['mode'], 'new':item['mode']})
    self.review_path.write_text(json.dumps(request))
    return request

def _TestReviewedRegistry_plan(self):
    from registry_lineage_plan import build_plan
    return build_plan(self.repo, ['clock-anchor'])

def _TestReviewedRegistry_test_missing_review_rejects_before_native_formatter_and_any_file_effect(self):
    native_formatter(self.repo)
    target = self.root / 'unformatted.json'; target.write_bytes(b'{"width":1}')
    before = inventory(self.repo)
    with self.assertRaisesRegex(ValueError, 'requires --review'):
        registry.refresh_skill(self.repo, 'clock-anchor')
    self.assertEqual(inventory(self.repo), before)

def _TestReviewedRegistry_test_all_named_bodies_precede_source_and_metadata_effects(self):
    native_formatter(self.repo)
    other = self.repo / 'skills/second'; shutil.copytree(self.root, other)
    evidence = self.repo / 'evidence/ports/second'; shutil.copytree(self.manifest.parent, evidence)
    manifest = json.loads((evidence / 'source-manifest.json').read_bytes())
    manifest['skill'] = 'second'; (evidence / 'source-manifest.json').write_text(json.dumps(manifest))
    (other / 'SKILL.md').write_text('# Second')
    from registry_lineage_plan import build_plan
    plan = build_plan(self.repo, ['clock-anchor', 'second'])
    self.assertEqual((plan['changes'][0]['skill'], plan['changes'][0]['path']), ('second', 'SKILL.md'))

def _TestReviewedRegistry_test_registry_module_dependencies_have_no_import_cycle(self):
    scripts = Path(registry.__file__).parent
    paths = [scripts / 'refresh_registry_lineage.py', *scripts.glob('registry_lineage_*.py')]
    modules = {path.stem for path in paths}
    graph = {path.stem: {node.module for node in ast.walk(ast.parse(path.read_text()))
                        if isinstance(node, ast.ImportFrom) and node.module in modules} for path in paths}
    order = list(TopologicalSorter(graph).static_order())
    self.assertEqual(set(order), modules)

def _TestReviewedRegistry_finish(self):
    results = []
    for _ in range(8):
        plan = self.plan()
        if not plan['changes']:
            return results
        self.prepare(plan['changes'][0])
        results.append(registry.refresh_skill(self.repo, 'clock-anchor', self.review_path))
    self.fail('fixture registry refresh did not reach a current plan')

def _TestReviewedRegistry_test_native_plan_is_read_only_and_reviewed_sequence_preserves_modes(self):
    native_formatter(self.repo)
    target = self.root / 'unformatted.json'; target.write_bytes(b'{"width":1}'); target.chmod(0o640)
    self.manifest.chmod(0o600)
    before = inventory(self.repo); plan = self.plan()
    self.assertEqual(inventory(self.repo), before)
    self.assertEqual(plan['changes'][0]['path'], 'unformatted.json')
    results = self.finish()
    self.assertEqual(len(results), 3)
    self.assertEqual(target.read_bytes(), b'{ "width": 1 }\n')
    self.assertEqual((target.stat().st_mode & 0o777, self.manifest.stat().st_mode & 0o777), (0o640, 0o600))
    lineage = json.loads((self.root / 'evals/source-lineage.json').read_bytes())
    manifest = json.loads(self.manifest.read_bytes())
    self.assertEqual(manifest['native_manifest_sha256'], registry.canonical_digest(lineage['source_files']))
    self.assertEqual(manifest['native_manifest_sha256'], lineage['native_manifest_sha256'])
    self.assertTrue(all(result['execution_acceptance'] == 'pending' for result in results))

def _TestReviewedRegistry_test_skipping_next_file_and_stale_source_reject_without_effect_then_recover(self):
    plan = self.plan(); self.prepare(plan['changes'][-1]); before = inventory(self.repo)
    with self.assertRaisesRegex(ValueError, 'next planned file'):
        registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
    self.assertEqual(inventory(self.repo), before)
    self.prepare(plan['changes'][0])
    (self.root / 'new.txt').write_text('new source')
    before = inventory(self.repo)
    with self.assertRaisesRegex(ValueError, 'derived bytes'):
        registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
    self.assertEqual(inventory(self.repo), before)
    self.finish()
    self.assertEqual(self.plan()['changes'], [])

def _TestReviewedRegistry_test_archived_identity_is_retained_and_corrupt_evidence_rejects(self):
    manifest = json.loads(self.manifest.read_bytes()); manifest['source_kind'] = 'archived_source'
    self.manifest.write_text(json.dumps(manifest)); identity = manifest['native_manifest_sha256']
    self.finish()
    lineage = json.loads((self.root / 'evals/source-lineage.json').read_bytes())
    self.assertEqual(lineage['native_manifest_sha256'], identity)
    self.assertEqual(lineage['public_files'][0]['source_paths'], ['native.txt', 'target-scaffolding'])
    source = self.manifest.parent / 'native.txt'; source.write_text('corrupt')
    before = inventory(self.repo)
    with self.assertRaisesRegex(ValueError, 'source evidence bytes'):
        self.plan()
    self.assertEqual(inventory(self.repo), before)

def _TestReviewedRegistry_test_unplanned_mode_rejects_before_effect_and_valid_review_recovers(self):
    item = self.plan()['changes'][0]; request = self.prepare(item)
    request['change']['mode']['new'] = 0o600
    self.review_path.write_text(json.dumps(request)); before = inventory(self.repo)
    with self.assertRaisesRegex(ValueError, 'planned mode'):
        registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
    self.assertEqual(inventory(self.repo), before)
    self.finish()


class TestReviewedRegistry(unittest.TestCase):
    setUp = _TestReviewedRegistry_setUp
    prepare = _TestReviewedRegistry_prepare
    plan = _TestReviewedRegistry_plan
    finish = _TestReviewedRegistry_finish
    test_missing_review_rejects_before_native_formatter_and_any_file_effect = _TestReviewedRegistry_test_missing_review_rejects_before_native_formatter_and_any_file_effect
    test_native_plan_is_read_only_and_reviewed_sequence_preserves_modes = _TestReviewedRegistry_test_native_plan_is_read_only_and_reviewed_sequence_preserves_modes
    test_skipping_next_file_and_stale_source_reject_without_effect_then_recover = _TestReviewedRegistry_test_skipping_next_file_and_stale_source_reject_without_effect_then_recover
    test_archived_identity_is_retained_and_corrupt_evidence_rejects = _TestReviewedRegistry_test_archived_identity_is_retained_and_corrupt_evidence_rejects
    test_unplanned_mode_rejects_before_effect_and_valid_review_recovers = _TestReviewedRegistry_test_unplanned_mode_rejects_before_effect_and_valid_review_recovers
    test_all_named_bodies_precede_source_and_metadata_effects = _TestReviewedRegistry_test_all_named_bodies_precede_source_and_metadata_effects
    test_registry_module_dependencies_have_no_import_cycle = _TestReviewedRegistry_test_registry_module_dependencies_have_no_import_cycle


if __name__ == '__main__':
    unittest.main()
