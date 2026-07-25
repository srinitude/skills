# Example: the help command

Guess this example removes: what the reply to "what can this skill do" contains, and how much of it comes from running something rather than from memory.

## User says

```
what can the skill factory do?
```

## Executor replies

```
Five commands, one line each:

help            this table
new <prompt>    build a skill that fulfills the prompt, test first, and prove it with fresh check output
validate <path> run the structure, writing, code, and placeholder checks on a skill and report every FAIL line
eval <path>     check the eval files, then run the cases and grade each assertion against quoted evidence
doctor          report environment readiness and, when the task runner is missing, the six commands that replace it

Every bundled script prints its own flags and exit codes with --help. Here is one, run just now:

$ python3 scripts/scaffold_skill.py --help
usage: scaffold_skill.py [-h] --name NAME --description DESCRIPTION
                         --dest DEST [--force]
...
Exit codes:
  0  skill created
  1  target already exists (rerun with --force to replace it)
  2  usage or input error
exit 0

Say the word and I will start a build. I need one line on the outcome you want and where the skill should land.
```

## Commands run

```
$ python3 scripts/scaffold_skill.py --help
usage: scaffold_skill.py [-h] --name NAME --description DESCRIPTION
                         --dest DEST [--force]

Scaffold a new skill directory that passes every factory check.

Creates SKILL.md, mise.toml, a CI workflow, support directories,
starter script and tests, seed evals, and copies of the checker
scripts so the new skill verifies itself. Prints a JSON summary.

Exit codes:
  0  skill created
  1  target already exists (rerun with --force to replace it)
  2  usage or input error

Example:
  python3 scripts/scaffold_skill.py --name release-notes \
    --description "Use when release notes are needed from a git log." \
    --dest /path/to/skills

options:
  -h, --help            show this help message and exit
  --name NAME
  --description DESCRIPTION
  --dest DEST           parent directory for the new skill
  --force               replace an existing target directory
exit 0
```

## Files created

None. The help command reads and reports.

## What the run proves

The command table in SKILL.md matches the scripts on disk, and the exit codes quoted in the reply come from a real --help run rather than from memory.
