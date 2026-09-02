# Example: the help command

Guess this example removes: what the reply to "what can this skill do" contains, and how much of it comes from running something rather than from memory.

## User says

```
what can the skill factory do?
```

## Executor replies

```
Eight commands, one line each:

help            this table
new <prompt>    build a skill that fulfills the prompt, test first, and prove it with fresh check output
update <path> <prompt> change an existing skill while preserving its purpose and accepted behavior
standardize <path> transform an existing skill into the factory format without replacing its purpose
import <source> <destination> convert a host-specific source into a separate portable skill and repository-guidance package
validate <path> run the structure, writing, code, and placeholder checks on a skill and report every FAIL line
eval <path>     check the eval files, then run the cases and grade each assertion against quoted evidence
doctor          report environment readiness and stop when the required task runner is missing

Every bundled script prints its own flags and exit codes with --help. Here is one, run just now:

$ mise run new -- --help
usage: scaffold_skill.py [-h] --name NAME --description DESCRIPTION
                         --dest DEST
...
Exit codes:
  0  skill created
  1  target already exists
  2  usage or input error
exit 0

Say the word and I will start a build. I need one line on the outcome you want and where the skill should land.
```

## Commands run

```
$ mise run new -- --help
usage: scaffold_skill.py [-h] --name NAME --description DESCRIPTION
                         --dest DEST

Scaffold a new skill directory with every factory check owner.

Creates SKILL.md, mise.toml, a CI workflow, support directories,
starter script and tests, seed evals, and copies of the checker
scripts so the new skill verifies itself. Prints a JSON summary.

Exit codes:
  0  skill created
  1  target already exists
  2  usage or input error

Example:
  mise run new -- --name release-notes \
    --description "Use when release notes are needed from a git log." \
    --dest /path/to/skills

options:
  -h, --help            show this help message and exit
  --name NAME
  --description DESCRIPTION
  --dest DEST           parent directory for the new skill
exit 0
```

## Files created

None. The help command reads and reports.

## What the run proves

The command table in SKILL.md matches the scripts on disk, and the exit codes quoted in the reply come from a real --help run rather than from memory.
