"""Keep update policies in checked native tasks, preserving custom rules."""
import json
import re
import tomllib
from validate_skill import split_frontmatter
from standardization_mise import normalize_mise
from scaffold_rules import START_RULES, LEGACY_START_RULES, route_cue, template_inputs, rule_spec, task_toml
from standardization_seed import task_records, operations, json_bytes


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


def policy_specs(factory, skill, tasks):
    blocks, owners = template_inputs(factory)
    template = (factory / 'assets/skill-template.md').read_text()
    selected = []
    for prefix in BODY_POLICIES:
        _, policy = body_policy('', template, prefix)
        matches = [owner for index, owner in owners.items() if policy in blocks[index]]
        if len(matches) != 1:
            raise ValueError('Body policy needs one reviewed template route: ' + prefix)
        if matches[0] not in selected:
            selected.append(matches[0])
    result = {}
    for owner in selected:
        name = 'rule:body-' + owner.removeprefix('rule:')
        parts = [blocks[index].replace('{{NAME}}', skill)
                 for index, parent in owners.items() if parent == owner]
        others = {key: value for key, value in tasks.items() if key != name}
        expected = rule_spec(name, owner, parts, blocks[-1], others)
        if name in tasks and tasks[name] != expected:
            raise ValueError('Body task needs an explicit reviewed profile migration: ' + name)
        result[name] = expected
    return result


def remove_exact_blocks(text, values):
    matches = [(start, end, block) for start, end, block in policy_blocks(text) if block in values]
    if len(matches) != len({block for _, _, block in matches}):
        raise ValueError('Duplicate body routes need an explicit reviewed profile migration')
    for start, end, _ in reversed(matches):
        text = text[:start] + text[end:]
    return text


def routed_body(text, factory, cues):
    _, body, error = split_frontmatter(text)
    if error:
        raise ValueError(error)
    header = text[:len(text) - len(body)]
    starts = {START_RULES, LEGACY_START_RULES}
    if sum(block in starts for _, _, block in policy_blocks(body)) > 1:
        raise ValueError('Duplicate startup rules need an explicit reviewed profile migration')
    body = remove_exact_blocks(body, {*starts, *cues})
    template = (factory / 'assets/skill-template.md').read_text()
    policies = []
    for prefix in BODY_POLICIES:
        body, policy = body_policy(body, template, prefix)
        policies.append(policy)
    body = body_references(body, template, policies)
    return header + '\n\n'.join([START_RULES, *cues]) + '\n\n' + body.lstrip()


def route_policies(files, factory, skill):
    mise = files['mise.toml'].decode('utf-8')
    tasks = tomllib.loads(mise)['tasks']
    specs = policy_specs(factory, skill, tasks)
    cues = [route_cue(name) for name in specs]
    files['SKILL.md'] = routed_body(files['SKILL.md'].decode('utf-8'), factory, cues).encode()
    added = [task_toml(name, spec) for name, spec in specs.items() if name not in tasks]
    if added:
        files['mise.toml'] = normalize_mise(mise.rstrip() + '\n\n' + '\n\n'.join(added) + '\n').encode()
    return specs


def route_operations(files, specs, profile):
    name = 'assets/use-case-contract.json'
    contract = json.loads(files[name])
    graph = contract['task_graph']
    for task, record in task_records(profile, specs).items():
        graph['tasks'].setdefault(task, record)
    present = {item['task'] for item in graph['public_operations']}
    graph['public_operations'].extend(row for row in operations(profile, specs) if row['task'] not in present)
    if contract != json.loads(files[name]):
        files[name] = json_bytes(contract)
