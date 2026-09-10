"""Keep native literal dependency arguments intact in policy and standardization."""
import json
import sys
import tomllib
import unittest
from pathlib import Path

import test_task_graph_policy as policy
from cli import SCRIPTS
sys.path.insert(0,str(SCRIPTS))
from standardization_mise import normalize_mise, runtime_dependencies
from standardization_seed import base_mise


class TestTaskArgumentDependencies(unittest.TestCase):
    check = policy.TestTaskGraphPolicy.check

    def test_literal_argument_references_pass_in_both_dependency_phases(self):
        for declaration in [
            'depends = [{ task = "test", args = ["--flag", "a b", "λ", "a b"] }, "decision-policy"]',
            'depends = ["decision-policy"]\ndepends_post = [{ task = "test", args = ["--review", "{{usage.review}}"] }]']:
            graph = policy.task_text().replace('depends = ["test", "decision-policy"]',declaration)
            result = self.check(graph)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_argument_references_keep_unknown_cycle_and_shape_rejection(self):
        for declaration,diagnostic in [
            ('depends = [{ task = "absent", args = ["x"] }]','unknown dependencies'),
            ('depends = [{ task = "ci", args = ["x"] }]','cycle'),
            ('depends = [{ task = "test", args = "x" }]','dependencies'),
            ('depends = [{ task = "test", args = [1] }]','dependencies'),
            ('depends = [{ task = "test", env = {X="y"} }]','dependencies')]:
            graph=policy.task_text().replace('depends = ["test", "decision-policy"]',declaration)
            result=self.check(graph)
            self.assertEqual(result.returncode,1,result.stdout+result.stderr)
            self.assertIn(diagnostic,result.stdout);self.assertNotIn('Traceback',result.stderr)

    def test_argument_instances_survive_runtime_edge_reduction(self):
        names = {'test', 'lint-code', 'check-runtime', 'setup-runtime'}
        for provider, removed in [('test', 'lint-code'), ('lint-code', 'check-runtime'),
                                  ('check-runtime', 'setup-runtime')]:
            instance = {'task': removed, 'args': ['a b', 'a b']}
            with self.subTest(provider=provider):
                self.assertEqual(runtime_dependencies('ci', [provider, removed, instance], names),
                                 [provider, instance])

    def test_standardization_preserves_argument_bytes_and_reading_order(self):
        source=base_mise({'primary_term':'source-ledger'})
        source+='\n[tasks.first]\ndescription = "Source ledger prepare"\ndepends = []\nrun = "true"\n'
        source+='\n[tasks.second]\ndescription = "Source ledger effect"\ndepends = [{task="first",args=["a b","λ","a b"]}]\nrun = "true"\n'
        source+='\n[tasks.third]\ndescription = "Source ledger followup"\ndepends = []\ndepends_post = [{task="second",args=["--review","{{usage.review}}"]}]\nrun = "true"\n'
        before=tomllib.loads(source)['tasks'];output=normalize_mise(source);after=tomllib.loads(output)['tasks']
        for name in ['first','second','third']:
            self.assertEqual(before[name],after[name])
        self.assertLess(list(after).index('first'),list(after).index('second'))
        self.assertLess(list(after).index('second'),list(after).index('third'))
        self.assertEqual(normalize_mise(output),output)


if __name__=='__main__':
    unittest.main()
