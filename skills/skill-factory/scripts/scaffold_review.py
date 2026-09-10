"""Apply a complete declared scaffold review through the existing file guard."""
import base64
import json
import tempfile
from pathlib import Path

from agentic_request_contract import read_json
from review_ledger_body import read_review
from review_ledger_context import recorded_work_contract, require
from review_ledger_source import check_source_capture, read_file
from review_ledger_write import write_file
from scaffold_plan import plan_digest
from skill_package import inventory, sha

CONTEXT_FIELDS = {'ledger', 'ledger_sha256', 'expected_documents', 'original_source', 'inventory_document'}


def read_context(context):
    require(isinstance(context, dict) and set(context) == CONTEXT_FIELDS, 'invalid scaffold ledger context')
    bindings = [{'path': context['ledger'], 'sha256': context['ledger_sha256']},
                *context['expected_documents'], context['original_source']]
    captured = {item['path']: read_file(item) for item in bindings}
    require(sha(captured[context['ledger']]) == context['ledger_sha256'], 'stale scaffold ledger')
    data = read_json(captured[context['ledger']].decode('utf-8'))
    check_source_capture(data, context, captured)
    return data, captured


def load_review(path, plan):
    raw = read_file({'path': str(Path(path).absolute())})
    review = read_json(raw.decode('utf-8'))
    require(isinstance(review, dict) and set(review) ==
            {'plan_sha256', 'context', 'body_review', 'files'}, 'invalid scaffold review fields')
    require(review['plan_sha256'] == plan_digest(plan), 'stale scaffold plan review')
    data, captured = read_context(review['context'])
    definitions = recorded_work_contract(data)['review_fields']
    fields = {item['field'] for item in definitions}
    require(len(fields) == len(definitions), 'duplicate ledger review fields')
    require(isinstance(review['files'], dict) and set(review['files']) ==
            {item['path'] for item in plan['files']}, 'review must cover every planned file exactly')
    for item in review['files'].values():
        require(isinstance(item, dict) and set(item) == {'reviewer', 'review'}
                and isinstance(item['reviewer'], str) and item['reviewer'].strip()
                and isinstance(item['review'], dict) and set(item['review']) == fields
                and all(isinstance(v, str) and v.strip() for v in item['review'].values()),
                'unfinished scaffold file review')
    body = next(item for item in plan['files'] if item['path'] == 'SKILL.md')
    binding = review['body_review']
    require(isinstance(binding, dict) and set(binding) == {'path', 'sha256'}, 'invalid body review binding')
    captured[binding['path']] = read_file(binding)
    require(sha(captured[binding['path']]) == binding['sha256'], 'stale initial body review')
    initial = read_review(captured, review['context'], binding, body['sha256'], data['source']['sha256'])
    require('previous_sha256' in initial and initial['previous_sha256'] is None, 'creation body review requires absence')
    return review, raw


def current_inputs(factory, plan, review_path, review_raw):
    body_review = read_json(review_raw.decode('utf-8'))['body_review']
    require(sha(read_file(body_review)) == body_review['sha256'], 'initial body review changed since planning')
    require(read_file({'path': str(Path(review_path).absolute())}) == review_raw, 'scaffold review changed')
    require(inventory(factory) == plan['factory_files'], 'factory changed since scaffold planning')
    require((factory / 'SKILL.md').read_bytes() == plan['factory_body']['text'].encode('utf-8'),
            'factory body changed since scaffold planning')


def file_request(item, review, prepared, body, installed):
    request = {**review['context'], 'action': 'write-file', 'change': {
        'path': item['path'], 'expected_sha256': None, 'new_file': prepared,
        'body_sha256': body['sha256'], **review['files'][item['path']]}}
    if 'mode' in item:
        request['change']['mode'] = {'expected': None, 'new': item['mode']}
    if item['path'] == 'SKILL.md':
        request['body_revision'] = {'previous': None, 'review': review['body_review']}
    elif not installed:
        request['bootstrap_body'] = {'body': body, 'review': review['body_review']}
    else:
        request['initial_body_review'] = review['body_review']
    return request


def build_reviewed(factory, target, plan, review_path, review, review_raw, check=None):
    current_inputs(factory, plan, review_path, review_raw)
    if check:
        check()
    expected = {item['path']: item['sha256'] for item in plan['files']}
    target.mkdir()
    writes = []
    with tempfile.TemporaryDirectory(prefix='scaffold-inputs-', dir=target.parent) as temporary:
        folder = Path(temporary)
        body_item = next(item for item in plan['files'] if item['path'] == 'SKILL.md')
        body_path = folder / 'body.md'; body_path.write_bytes(base64.b64decode(body_item['content_base64']))
        body = {'path': str(body_path), 'sha256': body_item['sha256']}
        for item in plan['files']:
            current_inputs(factory, plan, review_path, review_raw)
            if check:
                check()
            prepared = folder / 'prepared.bin'; prepared.write_bytes(base64.b64decode(item['content_base64']))
            (target / item['path']).parent.mkdir(parents=True, exist_ok=True)
            request = file_request(item, review, {'path': str(prepared), 'sha256': item['sha256']},
                                   body, (target / 'SKILL.md').exists())
            result = write_file(request, target)
            current_inputs(factory, plan, review_path, review_raw)
            if check:
                check()
            writes.append({key: result[key] for key in ['path', 'new_sha256', 'reviewer', 'review', 'execution_acceptance']})
    require(inventory(target) == expected, 'scaffold differs from reviewed file bytes')
    return writes
