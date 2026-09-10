"""Real body revision and post-effect source drift through the registry consumer."""
import json
import sys
import unittest
from pathlib import Path

import test_registry_review as cases
import refresh_registry_lineage as registry
import review_ledger_write as writer
from skill_package import sha
from standardization_test_support import native_formatter


class TestRegistryRecovery(unittest.TestCase):
    def setUp(self):
        cases.TestReviewedRegistry.setUp(self)

    def prepare_next(self):
        plan = cases.TestReviewedRegistry.plan(self)
        return cases.TestReviewedRegistry.prepare(self, plan['changes'][0])

    def test_formatter_body_change_requires_its_separate_current_revision(self):
        native_formatter(self.repo)
        body = self.root / 'SKILL.md'; body.write_text('# Clock anchor')
        old = body.read_bytes(); request = self.prepare_next()
        previous = self.folder / 'previous-body.md'; previous.write_bytes(old)
        binding = request.pop('initial_body_review')
        review = json.loads(Path(binding['path']).read_bytes())
        review.update(candidate_sha256=sha(self.prepared.read_bytes()), previous_sha256=sha(old))
        review_path = self.folder / 'candidate-body-review.json'; review_path.write_text(json.dumps(review))
        request['change']['body_sha256'] = sha(old)
        request['body_revision'] = {'previous':{'path':str(previous), 'sha256':sha(old)},
            'review':{'path':str(review_path), 'sha256':sha(review_path.read_bytes())}}
        self.review_path.write_text(json.dumps(request))
        result = registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
        self.assertEqual(result['change']['path'], 'SKILL.md')
        self.assertEqual(body.read_bytes(), b'# Clock anchor\n')
        self.assertEqual(result['change']['after']['body']['sha256'], sha(body.read_bytes()))

    def test_post_effect_source_drift_restores_manifest_and_preserves_prior_write(self):
        self.prepare_next(); registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
        lineage = self.root / 'evals/source-lineage.json'; accepted = lineage.read_bytes()
        request = self.prepare_next(); self.assertEqual(request['change']['path'], 'evidence/ports/clock-anchor/source-manifest.json')
        before = self.manifest.read_bytes()
        source = Path(self.request['original_source']['path']); original = source.read_bytes(); changed = []
        def trace(frame, event, value):
            if event == 'return' and frame.f_code is writer.install.__code__ and not changed:
                source.write_bytes(original + b'actual post-effect drift'); changed.append(True)
            return trace
        sys.settrace(trace)
        try:
            with self.assertRaises(ValueError):
                registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
        finally:
            sys.settrace(None)
        self.assertEqual(changed, [True])
        self.assertEqual((self.manifest.read_bytes(), lineage.read_bytes()), (before, accepted))
        source.write_bytes(original)
        result = registry.refresh_skill(self.repo, 'clock-anchor', self.review_path)
        self.assertEqual(result['change']['new_sha256'], sha(self.manifest.read_bytes()))


if __name__ == '__main__':
    unittest.main()
