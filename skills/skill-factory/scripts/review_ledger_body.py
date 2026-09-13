"""Bound initial-body reviews for ordinary writes, bootstrap and body revisions."""
import json
from skill_package import sha
from agentic_request_contract import read_json
from review_ledger_context import require


def file_binding(value):
    require(isinstance(value, dict) and set(value) == {'path', 'sha256'},
            'invalid body file binding')
    return value


def revision(request):
    value = request.get('body_revision')
    modes = [key for key in ['initial_body_review', 'bootstrap_body', 'body_revision'] if key in request]
    require(len(modes) == 1, 'file writes require exactly one initial body review mode')
    if value is None:
        return None
    require(isinstance(value, dict) and set(value) == {'previous', 'review'}
            and request['change']['path'] == 'SKILL.md',
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
        return [{'path': str(root / 'SKILL.md'), 'sha256': request['change']['body_sha256']},
                file_binding(request.get('initial_body_review'))]
    require(isinstance(bootstrap, dict) and set(bootstrap) == {'body', 'review'},
            'bootstrap requires exact body and review bindings')
    for binding in bootstrap.values():
        file_binding(binding)
    require(bootstrap['body']['sha256'] == request['change']['body_sha256'],
            'bootstrap body differs from the reviewed change')
    return [bootstrap['body'], bootstrap['review']]


def pending_prerequisite(review, request, binding, selected):
    require(selected == binding['sha256'] and isinstance(selected, str),
            'pending body review requires its caller-selected exact digest')
    value = review.get('prerequisite')
    require(isinstance(value, dict) and set(value) ==
            {'change_sha256', 'reason', 'pending_validation'},
            'pending body review requires one exact prerequisite and remaining validation')
    change = json.dumps(request['change'], sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    require(value['change_sha256'] == sha(change),
            'pending body review is bound to another file change')
    require(isinstance(value['reason'], str) and value['reason'].strip()
            and isinstance(value['pending_validation'], list) and value['pending_validation']
            and all(isinstance(item, str) and item.strip() for item in value['pending_validation']),
            'prerequisite reason and pending validation must remain explicit')


def read_review(captured, request, binding, candidate, source_sha256, pending_body_review=None):
    review = read_json(captured[binding['path']].decode('utf-8'))
    require(isinstance(review, dict) and review.get('candidate_sha256') == candidate
            and review.get('ledger_sha256') == request['ledger_sha256']
            and review.get('source_sha256') == source_sha256
            and review.get('execution_acceptance') == 'pending', 'stale or invalid initial body review')
    initial = review.get('initial_contract_validation')
    require(isinstance(initial, dict)
            and all(isinstance(initial.get(key), str) and initial[key].strip()
                    for key in ['reviewer', 'method', 'limit']), 'initial body review is unfinished')
    if pending_body_review is not None:
        require(initial.get('state') == 'pending', 'prerequisite exception requires pending validation')
        pending_prerequisite(review, request, binding, pending_body_review)
    else:
        require(initial.get('state') == 'PASS', 'initial body review is unfinished')
    return review


def body_review(captured, request, root, source_sha256, phase='before', pending_body_review=None):
    value = revision(request)
    aliases = [path for path in root.iterdir() if path.name.casefold() == 'skill.md']
    if value is not None:
        previous = value['previous']
        absent = phase == 'before' and previous is None
        require(not aliases if absent else len(aliases) == 1 and aliases[0].name == 'SKILL.md',
                'body revision has a creation collision, missing body or body alias')
        candidate = request['change']['new_file']
        require(captured[candidate['path']].decode('utf-8').strip(), 'candidate body must be nonempty UTF-8')
        review = read_review(captured, request, value['review'], candidate['sha256'], source_sha256, pending_body_review)
        require('previous_sha256' in review and review['previous_sha256'] ==
                (previous['sha256'] if previous is not None else None), 'stale previous body review')
        return {'body_revision_review': review}
    bootstrap = request.get('bootstrap_body')
    if bootstrap is None:
        require(len(aliases) == 1 and aliases[0].name == 'SKILL.md',
                'ordinary writes require the canonical body without aliases')
        return {'initial_body_review': read_review(captured, request, request['initial_body_review'],
                                                  request['change']['body_sha256'], source_sha256, pending_body_review)}
    require(pending_body_review is None, 'bootstrap rejects a pending body exception')
    require(not aliases, 'bootstrap cannot hide an installed body or body alias')
    return {'bootstrap_review': read_review(captured, request, bootstrap['review'],
                                           bootstrap['body']['sha256'], source_sha256)}
