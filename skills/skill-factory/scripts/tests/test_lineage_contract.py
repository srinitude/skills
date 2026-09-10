"""Current lineage, version and owned-file boundaries under a complete review."""
import json
import unittest

from cli import SKILL_DIR, run
import test_lineage_review as reviewed


class TestLineageContract(unittest.TestCase):
    setUp = reviewed.TestLineageReview.setUp
    prepare = reviewed.TestLineageReview.prepare
    invoke = reviewed.TestLineageReview.invoke
    package = reviewed.TestLineageReview.package

    def test_help_documents_usage_and_exit_codes(self):
        result = run('check_lineage.py', '--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage', result.stdout.lower())
        self.assertIn('exit code', result.stdout.lower())
        self.assertIn('--review', result.stdout)

    def test_refreshed_lineage_passes(self):
        refreshed = self.invoke()
        self.assertEqual(refreshed.returncode, 0, refreshed.stdout + refreshed.stderr)
        result = run('check_lineage.py', self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stale_public_version_fails(self):
        lineage = json.loads(self.prepared.read_bytes())
        lineage['public_version'] = '0.9.0'
        self.target.write_text(json.dumps(lineage))
        result = run('check_lineage.py', self.root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('public_version', result.stdout)

    def test_generation_contract_uses_portable_name_grammar(self):
        text = (SKILL_DIR / 'references/generation-contract.md').read_text()
        self.assertIn('^[a-z0-9]+(?:-[a-z0-9]+)*$', text)
        self.assertNotIn('[a-z0-9._-]*', text)

    def test_runtime_trees_are_excluded_from_lineage(self):
        for relative in ['.mise/state.json', 'node_modules/pkg/index.js']:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('runtime')
        self.prepare(); result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        paths = [item['path'] for item in json.loads(self.target.read_bytes())['source_files']]
        self.assertFalse(any(path.startswith(('.mise/', 'node_modules/')) for path in paths))

    def test_runtime_symlinks_are_excluded_but_owned_links_cannot_change_lineage(self):
        bins = self.root / 'node_modules/.bin'; bins.mkdir(parents=True)
        (bins / 'compiler').symlink_to(self.root / 'SKILL.md')
        self.prepare(); result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (self.root / 'note.bin').write_bytes(b'new owned data'); self.prepare()
        (self.root / 'owned-link').symlink_to(self.root / 'SKILL.md')
        before = self.package(); result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('owned-link', result.stdout)
        self.assertEqual(self.package(), before)

    def test_lineage_rejects_external_file_symlinks(self):
        external = self.folder / 'private.txt'; external.write_text('private')
        (self.root / 'linked.txt').symlink_to(external)
        before = self.package(); result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('linked.txt', result.stdout)
        self.assertEqual(self.package(), before)

    def test_lineage_rejects_a_symlinked_skill_root(self):
        linked = self.folder / 'linked-sample'; linked.symlink_to(self.root, target_is_directory=True)
        before = self.package()
        result = run('check_lineage.py', linked, '--write', '--review', self.request_path)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('symlink', result.stdout.lower())
        self.assertEqual(self.package(), before)


if __name__ == '__main__':
    unittest.main()
