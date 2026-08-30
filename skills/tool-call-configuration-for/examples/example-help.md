# Example: help

Guess this example removes: which public commands the executable accepts and whether help mutates files.

## User says

```
help
```

## Executor replies

```
The skill accepts help, generate, and apply. Generate needs one exact tool reference plus behavior. Apply also needs one exact existing-skill target and a checked integration plan.
```

## Commands run

```text
$ python3 scripts/tool_call_config.py help
usage: tool_call_config.py [-h] {generate,apply} ...

Generate or apply one exact tool behavior configuration.

Exit codes:
  0  generated, applied, or already satisfied
  1  checked conflict, stale plan, or failed validation
  2  usage, identity, path, or input error

Examples:
  python3 scripts/tool_call_config.py generate @tool.json --behavior @rules.json --output ./out
  python3 scripts/tool_call_config.py apply @tool.json --target my-skill --skills-root ../ --behavior @rules.json --integration @plan.json

positional arguments:
  {generate,apply}

options:
  -h, --help        show this help message and exit
exit 0
```

## Files created

None.

## What the run proves

Help names the grammar and exit contract without reading a tool or writing a file.
