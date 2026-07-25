# Example: the doctor command and the degraded path

Guess this example removes: whether a missing task runner stops a build, what the readiness report prints, and the exact wording for a completion claim when `mise run ci` never ran.

## User says

```
before I ask for anything big: is this environment ready for building skills?
```

## Executor replies

```
Ready, in degraded mode. Python 3.14.3 passes, git is present, every bundled script and template is present. The task runner is absent, which no longer blocks a build: it is a wrapper over six commands that I run directly.

$ python3 scripts/doctor.py
{
  "ready": true,
  "mode": "degraded",
  "fallback": [
    "python3 -m unittest discover -s scripts/tests -p 'test_*.py'",
    "python3 scripts/validate_skill.py .",
    "python3 scripts/lint_writing.py .",
    "python3 scripts/check_code_rules.py .",
    "python3 scripts/check_placeholders.py .",
    "python3 scripts/check_evals.py ."
  ],
  ...
}
exit 0

What that costs you: I can prove every job passes, and I cannot prove the aggregate wrapper command passes. My completion claim will read "every job in mise.toml passed as a direct command; mise run ci itself did not run here".
```

## Commands run

```
$ python3 scripts/doctor.py
{
  "ready": true,
  "mode": "degraded",
  "fallback": [
    "python3 -m unittest discover -s scripts/tests -p 'test_*.py'",
    "python3 scripts/validate_skill.py .",
    "python3 scripts/lint_writing.py .",
    "python3 scripts/check_code_rules.py .",
    "python3 scripts/check_placeholders.py .",
    "python3 scripts/check_evals.py ."
  ],
  "checks": [
    {
      "name": "python",
      "required": true,
      "ok": true,
      "detail": "found 3.14.3, need 3.11 or newer"
    },
    {
      "name": "mise",
      "required": false,
      "ok": false,
      "detail": "mise not on PATH"
    },
    {
      "name": "git",
      "required": false,
      "ok": true,
      "detail": "/usr/bin/git"
    },
    {
      "name": "scripts",
      "required": true,
      "ok": true,
      "detail": "all present"
    },
    {
      "name": "templates",
      "required": true,
      "ok": true,
      "detail": "all present"
    }
  ]
}
exit 0

$ mise run ci
/bin/bash: line 12: mise: command not found
exit 127
```

## Files created

None.

## What the run proves

A missing task runner leaves "ready" true, flips "mode" to degraded, and fills "fallback" with the six commands to run instead. Only a required check that fails, meaning the interpreter version or a missing bundled script or template, exits 1 and stops the build. The run also shows what the wrapper command does when it is absent: exit 127, quoted rather than hidden.

## When does the doctor stop a build?

The stop condition is exit 1, printed with "ready": false and the failing required check named in its detail field. Report that check, say what is missing, and wait. Exit 0 with mode degraded is not a stop: continue, run the six fallback commands, and phrase the completion claim as shown above.
