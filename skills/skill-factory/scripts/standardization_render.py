"""Calculate standardization bytes using the existing domain transformation owners."""
import tomllib
import re
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
from validate_skill import split_frontmatter


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


BODY_POLICIES = (
    '**Start here.**', '| Key | Action and evidence meaning |', '**Reusable ledger artifact, owned here.**',
    '**Relationship records.**', '| Relationship family |',
    '**Dependency contract.**', '**File graph.**', '**Order and invalidation.**',
    '**Required initial context.**', '**Traverse, work and check.**',
    'For every individual added, changed or removed file',
    '**Efficiency and optional improvement.**',
    '**Implement software for this outcome.**',
)


def policy_blocks(text):
    """Locate prose/table blocks without treating fenced or indented code as rules."""
    found, start, offset, fence = [], None, 0, None
    for line in text.splitlines(keepends=True) + ['\n']:
        marker = re.match(r' {0,3}(`{3,}|~{3,})(.*)$', line)
        blocked = fence is not None or marker or line.startswith(('    ', '\t'))
        if marker and fence is None:
            fence = marker[1]
        elif marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
            fence = None
        if (blocked or not line.strip()) and start is not None:
            found.append((start, offset, text[start:offset].strip()))
            start = None
        elif not blocked and line.strip() and start is None:
            start = offset
        offset += len(line)
    return found


def body_policy(text, template, prefix):
    policies = [block for _, _, block in policy_blocks(template) if block.startswith(prefix)]
    if len(policies) != 1:
        raise ValueError('factory needs one canonical body policy: ' + prefix)
    existing = [(start, end, block) for start, end, block in policy_blocks(text) if block.startswith(prefix)]
    if existing and (len(existing) != 1 or existing[0][2] != policies[0]):
        raise ValueError('body policy needs an explicit reviewed profile migration: ' + prefix.lower())
    if existing:
        start, end, _ = existing[0]
        text = text[:start] + text[end:]
    return text, policies[0]


def body_references(text, template, policies):
    needed = set(re.findall(r'\[[^\]\n]+\]\[([^\]\n]+)\]', '\n'.join(policies)))
    current = [line for _, _, block in policy_blocks(text) for line in block.splitlines()]
    definitions = []
    for name in sorted(needed):
        prefix = '[' + name + ']:'
        source = [line for line in template.splitlines() if line.startswith(prefix)]
        if len(source) != 1:
            raise ValueError('factory needs one canonical body reference: ' + name)
        existing = [line for line in current if line.startswith(prefix)]
        if existing and existing != source:
            raise ValueError('body reference needs an explicit reviewed profile migration: ' + name)
        if not existing:
            definitions.extend(source)
    return text.rstrip() + ('\n\n' + '\n'.join(definitions) if definitions else '') + '\n'


def body_policies(text, factory):
    template = (factory / 'assets/skill-template.md').read_text(encoding='utf-8')
    _, body, error = split_frontmatter(text)
    if error:
        raise ValueError(error)
    header = text[:len(text) - len(body)]
    policies = []
    for prefix in BODY_POLICIES:
        body, policy = body_policy(body, template, prefix)
        policies.append(policy)
    body = body_references(body, template, policies)
    return header + '\n\n'.join(policies) + '\n\n' + body.lstrip()


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
