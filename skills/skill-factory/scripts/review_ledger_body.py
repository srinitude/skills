"""Bound body inputs and declared reviews for bootstrap and body revisions."""
from agentic_request_contract import read_json
from review_ledger_context import require


def file_binding(value):
    require(isinstance(value, dict) and set(value) == {'path', 'sha256'},
            'invalid body file binding')
    return value


def revision(request):
    value = request.get('body_revision')
    if value is None:
        return None
    require(isinstance(value, dict) and set(value) == {'previous', 'review'}
            and request.get('bootstrap_body') is None and request['change']['path'] == 'SKILL.md',
            'body_revision requires the canonical body and rejects bootstrap_body')
    file_binding(value['review'])
    previous = file_binding(value['previous']) if value['previous'] is not None else None
    expected = previous['sha256'] if previous is not None else None
    change = request['change']
    require(change['expected_sha256'] == expected and change['body_sha256'] ==
            (expected if expected is not None else change['new_file']['sha256']),
            'body revision previous identity differs from its change')
    return value


def body_inputs(request, root, phase='before'):
    value = revision(request)
    if value is not None:
        previous = value['previous']
        expected = request['change']['new_file']['sha256']
        if phase == 'before' and previous is None:
            current = request['change']['new_file']
        else:
            current = {'path': str(root / 'SKILL.md'), 'sha256':
                       previous['sha256'] if phase == 'before' else expected}
        return [current, *([previous] if previous is not None else []), value['review']]
    bootstrap = request.get('bootstrap_body')
    if bootstrap is None:
        return [{'path': str(root / 'SKILL.md'), 'sha256': request['change']['body_sha256']}]
    require(isinstance(bootstrap, dict) and set(bootstrap) == {'body', 'review'},
            'bootstrap requires exact body and review bindings')
    for binding in bootstrap.values():
        file_binding(binding)
    require(bootstrap['body']['sha256'] == request['change']['body_sha256'],
            'bootstrap body differs from the reviewed change')
    return [bootstrap['body'], bootstrap['review']]


def read_review(captured, request, binding, candidate, source_sha256):
    review = read_json(captured[binding['path']].decode('utf-8'))
    require(isinstance(review, dict) and review.get('candidate_sha256') == candidate
            and review.get('ledger_sha256') == request['ledger_sha256']
            and review.get('source_sha256') == source_sha256
            and review.get('execution_acceptance') == 'pending', 'stale or invalid initial body review')
    initial = review.get('initial_contract_validation')
    require(isinstance(initial, dict) and initial.get('state') == 'PASS'
            and all(isinstance(initial.get(key), str) and initial[key].strip()
                    for key in ['reviewer', 'method', 'limit']), 'initial body review is unfinished')
    return review


def body_review(captured, request, root, source_sha256, phase='before'):
    value = revision(request)
    aliases = [path for path in root.iterdir() if path.name.casefold() == 'skill.md']
    if value is not None:
        previous = value['previous']
        absent = phase == 'before' and previous is None
        require(not aliases if absent else len(aliases) == 1 and aliases[0].name == 'SKILL.md',
                'body revision has a creation collision, missing body or body alias')
        candidate = request['change']['new_file']
        require(captured[candidate['path']].decode('utf-8').strip(), 'candidate body must be nonempty UTF-8')
        review = read_review(captured, request, value['review'], candidate['sha256'], source_sha256)
        require('previous_sha256' in review and review['previous_sha256'] ==
                (previous['sha256'] if previous is not None else None), 'stale previous body review')
        return {'body_revision_review': review}
    bootstrap = request.get('bootstrap_body')
    if bootstrap is None:
        return {}
    require(not aliases, 'bootstrap cannot hide an installed body or body alias')
    return {'bootstrap_review': read_review(captured, request, bootstrap['review'],
                                           bootstrap['body']['sha256'], source_sha256)}
