"""Apply only the next exact registry effect under the skill's current file review."""
import base64
from pathlib import Path

from agentic_request_contract import read_json
from review_ledger_context import require
from review_ledger_source import read_file
from review_ledger_write import write_file
from registry_lineage_plan import build_plan, current_inputs


def refresh(root, names, review_path):
    require(review_path is not None, 'registry refresh requires --review before formatter execution')
    binding = {'path': str(Path(review_path).absolute())}
    raw = read_file(binding); request = read_json(raw.decode('utf-8'))
    require(isinstance(request, dict) and request.get('action') == 'write-file'
            and isinstance(request.get('change'), dict), 'registry review requires a write-file request')
    plan = build_plan(root, names)
    require(plan['changes'], 'registry has no changed file; run complete validation instead')
    selected = plan['changes'][0]
    require(request['change'].get('path') == selected['path'], 'registry review must target the next planned file')
    prepared = read_file(request['change']['new_file'])
    require(prepared == base64.b64decode(selected['content_base64']), 'registry prepared data differs from current derived bytes')
    require(request['change'].get('expected_sha256') == selected['expected_sha256'], 'stale registry file identity')
    require(0 <= selected['mode'] <= 0o777 and request['change'].get('mode',
            {'expected': selected['mode'], 'new': selected['mode']}) ==
            {'expected': selected['mode'], 'new': selected['mode']}, 'registry request must preserve the planned mode')
    owner = Path(root) / 'skills' / selected['skill']
    calls = 0
    def check():
        nonlocal calls
        require(read_file(binding) == raw and read_file(request['change']['new_file']) == prepared, 'registry request changed')
        current_inputs(plan, selected, calls != 0)
        calls += 1
        return True
    related = {'target_root': Path(root)} if selected['owner'] == 'repository' else {}
    result = write_file(request, owner, effect_check=check, **related)
    return {'status': 'PASS', 'mode': 'one-file-write', 'change': result, 'execution_acceptance': 'pending',
            'remaining_from_plan': len(plan['changes']) - 1,
            'next': 'Replan and review the next file; a final empty plan still requires complete source and domain validation.'}
