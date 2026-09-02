# Help example

Guess removed: Help starts no run and writes no file.

## Request

> Show me the skill commands.

## Command

```sh
mise run run-help
```

## Real output

```text
usage: run_pipeline.py [-h] {start,packet,record,check} ...

Build and check one design run. The tool writes stable run files. It does not
judge design work. Exit codes: 0 the command passed 1 the run is blocked 2 the
command input is bad

positional arguments:
  {start,packet,record,check}
    start               make a stable run folder
    packet              make one model work packet
    record              check and save one model result
    check               check all model records

options:
  -h, --help            show this help message and exit
```

The command exits with code `0`. It creates no files.
