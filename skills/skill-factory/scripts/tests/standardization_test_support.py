"""Explicit fixture reviews for actual standardization calls; acceptance stays pending."""
import json
import unittest

from cli import run, SKILL_DIR
from scaffold_test_support import review_fixture


def reviewed_standardize(*args):
    if '--apply' not in args:
        return run('standardize_registry_skill.py', *args)
    result = run('standardize_registry_skill.py', *(arg for arg in args if arg != '--apply'))
    if result.returncode:
        return result
    owner = unittest.TestCase()
    try:
        path, _, case = review_fixture(owner, json.loads(result.stdout)['plan'])
        plan_path = case.folder / 'standardization-plan.json'
        plan_path.write_text(result.stdout)
        return run('standardize_registry_skill.py', *args, '--plan-file', plan_path, '--review', path)
    finally:
        owner.doCleanups()


def native_formatter(base):
    """Use the declared real formatter in a disposable repository fixture."""
    (base / '.git').mkdir(exist_ok=True)
    (base / '.prettierrc.json').write_text('{}')
    modules = base / 'node_modules'; modules.mkdir(exist_ok=True)
    source = SKILL_DIR / 'node_modules/prettier'
    if not (source / 'bin/prettier.cjs').is_file():
        raise ValueError('declared Prettier dependency is missing; install the locked runtime')
    (modules / 'prettier').symlink_to(source, target_is_directory=True)
    return (modules / 'prettier/bin/prettier.cjs').absolute()
