"""One native public definition and its checked Usage projection."""
import argparse
import contextlib
import io
import json
import re
import subprocess
from pathlib import Path

from standardize_registry_skill import FACTORY, build_parser, parse_args as parse_native
from skill_scope import read_fields


WORKFLOW_NOTES = ('Use --flag VALUE or --flag=VALUE. Repeating a workflow option is an error.\n'
    'Without --workflow-state, private temporary state is removed after this command.\n'
    'Save stdout from planning, then pass that file with --plan-file when applying.\n'
    'Persistence is opt-in. A review record is not authenticated human permission.\n'
    'Success reports execution_acceptance: pending; validate the actual output separately.')


class UniqueValue(argparse._StoreAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is not None or not values or values.startswith('--'):
            raise ValueError('Each workflow option requires one explicit value')
        super().__call__(parser, namespace, values, option_string)


class UniqueFlag(argparse._StoreTrueAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest):
            raise ValueError('Each workflow option may appear only once')
        super().__call__(parser, namespace, values, option_string)


def workflow_options(parser):
    group = parser.add_argument_group('Workflow options')
    group.add_argument('--workflow-state', metavar='DIRECTORY', action=UniqueValue,
        help='Existing absolute directory owned by this caller, private (0700) on a supported POSIX filesystem. Retains plans, native results and a local SQLite store.')
    group.add_argument('--workflow-run', metavar='UUID', action=UniqueValue,
        help='Select a suspended run in --workflow-state. Resume with --apply, --plan-file and --review.')
    group.add_argument('--workflow-reject', action=UniqueFlag,
        help='Reject that suspended run without applying files. Requires --workflow-state and --workflow-run.')


def build_public_parser():
    parser = build_parser()
    parser.prog = 'standardize-target'
    workflow_options(parser)
    parser.epilog = WORKFLOW_NOTES
    return parser


def usage_spec():
    from argparse_usage import generate
    from argparse_usage.kdl_utils import format_flag
    parser = build_public_parser()
    # The published exporter omits help and argparse's implicit long aliases.
    # Reject unreviewed action shapes instead of silently exporting a weaker grammar.
    for action in parser._actions:
        if type(action) not in (argparse._HelpAction, argparse._StoreAction, argparse._StoreTrueAction, UniqueValue, UniqueFlag) or action.nargs not in (None, 0):
            raise ValueError('Review Usage exporter support for the changed argument action')
    spec = generate(parser, version=read_fields(FACTORY)['metadata']['version'])
    # The exporter omits epilog; Markdown ignores after_help and after_long_help.
    spec += '\nlong_about ' + json.dumps(parser.description + '\n\n' + parser.epilog)
    help_action = next(action for action in parser._actions if isinstance(action, argparse._HelpAction))
    short, long = help_action.option_strings
    spec += '\n' + format_flag(short=short, long=long, help_text=help_action.help, takes_arg=False)
    native = build_parser()._option_string_actions
    aliases = {name: [name[:n] for n in range(3, len(name))
                     if sum(other.startswith(name[:n]) for other in native) == 1]
               for name in native if name.startswith('--')}
    lines = []
    for line in spec.splitlines():
        match = re.match(r'flag "([^" ]+)(?: [^" ]+)?"', line)
        name = long if line.startswith('flag "' + short + ' ') else match.group(1) if match else None
        values = aliases.get(name, [])
        if values:
            nodes = ' '.join('alias ' + json.dumps(value) + ' hide=#true;' for value in values)
            line += ' ' + nodes if line.endswith('{') else ' { ' + nodes + ' }'
        lines.append(line)
    return '\n'.join(lines) + '\n'


def workflow_args(argv):
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    workflow_options(parser)
    parsed, native = parser.parse_known_args(argv)
    selected = {key.removeprefix('workflow_'): value for key, value in vars(parsed).items()
                if value is not None and value is not False}
    if selected.get('state') and not Path(selected['state']).is_absolute():
        raise ValueError('Workflow state requires an absolute directory')
    if selected.get('run') and (not selected.get('state') or not re.fullmatch(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', selected['run'])):
        raise ValueError('A resumed run requires an explicit state directory and UUID')
    if selected.get('reject') and not selected.get('run'):
        raise ValueError('Rejection requires a suspended run in an explicit state directory')
    return selected, native


def parse_args(argv):
    selected, native = workflow_args(argv)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            parsed = parse_native(native)
    except SystemExit as error:
        if error.code == 0:
            print(build_public_parser().format_help(), end='')
        raise
    if selected.get('reject') and parsed.apply:
        raise ValueError('Rejection and --apply are mutually exclusive')
    check_usage(parsed, selected, argv)
    return parsed, selected


def checked_usage_spec():
    spec = usage_spec()
    try:
        recorded = (FACTORY / 'assets/standardization.usage.kdl').read_bytes()
    except OSError as error:
        raise ValueError('Usage projection is missing or unreadable; regenerate and review it') from error
    if recorded != spec.encode('utf-8'):
        raise ValueError('Usage projection is stale; regenerate and review it')
    return spec


def boolean_binding(value):
    if value not in ('true', 'false'):
        raise ValueError('Usage returned an invalid boolean binding')
    return value == 'true'


def check_usage(parsed, selected, argv):
    # Native validation owns rejection semantics; Usage must agree before effects.
    result = subprocess.run(['usage', 'explain', '--format', 'json', '--spec', checked_usage_spec(),
        '--', 'standardize-target', *argv], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Usage contract check failed: ' + result.stderr.strip())
    report = json.loads(result.stdout)
    if report['errors'] or report['refused'] is not None:
        raise ValueError('Usage rejected arguments accepted by the native definition')
    expected = {**vars(parsed), 'workflow_state': selected.get('state'),
        'workflow_run': selected.get('run'), 'workflow_reject': selected.get('reject', False)}
    values = {item['name'].replace('-', '_'): item['value'] for item in report['values']}
    for name, value in expected.items():
        if isinstance(value, bool):
            values[name] = boolean_binding(values.get(name))
        elif value is None:
            values.setdefault(name, None)
    if values != expected:
        raise ValueError('Usage bindings differ from the native definition')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, epilog='Example: export this definition through the owning Mise task. Exit 0 succeeds; exit 2 rejects arguments.')
    parser.parse_args()
    print(usage_spec(), end='')
