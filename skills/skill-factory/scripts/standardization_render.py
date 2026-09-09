"""Calculate standardization bytes using the existing domain transformation owners."""
import tomllib
from pathlib import Path

from standardization_assets import asset_files
from standardization_contracts import contract_files
from standardization_discovery import enrich_content
from standardization_markdown import rewrite_markdown, script_task_map
from standardization_mise import normalize_mise
from standardization_rewrites import rewritten_section, rewritten_text
from standardization_runtime import check_runtime, LEDGER_EXAMPLES, ROOT_FILES
from standardization_seed import seeds
from skill_scope import scoped_text


def checked_name(files, name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != name or name not in files:
        raise ValueError('missing or unsafe planned rewrite path: ' + name)
    return name


def text_rewrites(files, profile, strict):
    for name, rules in profile.get('text_rewrites', {}).items():
        checked_name(files, name)
        files[name] = rewritten_text(files[name].decode('utf-8'), rules, name, strict).encode('utf-8')


def support_files(files, factory, copies, scripts, canonical):
    check_runtime(files, factory)
    for name in ROOT_FILES + LEDGER_EXAMPLES:
        files.setdefault(name, (factory / name).read_bytes())
    for source, target in copies:
        files[target] = (factory / source).read_bytes()
    for name in scripts:
        target = 'scripts/' + name
        if target not in files or name in canonical:
            files[target] = (factory / target).read_bytes()


def body_policy(text, template, prefix, label):
    policies = [line.strip() for line in template.splitlines() if line.strip().startswith(prefix)]
    if len(policies) != 1:
        raise ValueError('factory must have exactly one canonical ' + label + ' paragraph')
    existing = [line.strip() for line in text.splitlines() if prefix in line]
    if existing:
        if existing != policies:
            raise ValueError('existing ' + label + ' policy needs an explicit reviewed profile migration')
        return text
    marker = '\nMise owns repeatable mechanics'
    if text.count(marker) != 1:
        raise ValueError(label + ' policy insertion needs a reviewed body owner')
    return text.replace(marker, '\n' + policies[0] + '\n' + marker, 1)


def body_policies(text, factory):
    template = (factory / 'assets/skill-template.md').read_text(encoding='utf-8')
    for prefix, label in [('For every individual added, changed or removed file', 'file-review'),
                          ('**Efficiency and optional improvement.**', 'efficiency')]:
        text = body_policy(text, template, prefix, label)
    return text


def render(root, original, profile, scope, factory, sources, stamp):
    files = dict(original)
    seeds(root, files, profile, factory)
    profile = enrich_content(files, profile)
    text_rewrites(files, profile, False)
    for rule in profile.get('section_rewrites', []):
        name = checked_name(files, rule['path'])
        files[name] = rewritten_section(files[name].decode('utf-8'), rule).encode('utf-8')
    files['mise.toml'] = normalize_mise(files['mise.toml'].decode('utf-8'), profile).encode('utf-8')
    support_files(files, factory, *sources)
    tasks = tomllib.loads(files['mise.toml'].decode('utf-8'))['tasks']
    owners = script_task_map(tasks)
    for name in files:
        if name.endswith('.md'):
            files[name] = rewrite_markdown(files[name].decode('utf-8'), owners, profile,
                                           add_contract=name == 'SKILL.md').encode('utf-8')
    text_rewrites(files, profile, True)
    files['SKILL.md'] = body_policies(files['SKILL.md'].decode('utf-8'), factory).encode('utf-8')
    contract_files(files, tasks, profile)
    asset_files(files, profile, tasks, stamp)
    if scope is not None:
        files['SKILL.md'] = scoped_text(files['SKILL.md'].decode('utf-8'), scope).encode('utf-8')
    return files
