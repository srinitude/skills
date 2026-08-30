# `exec_command` configuration

Read this file before every exact `exec_command` call made while following Skill Factory, and keep it active until the command, any returned session, evidence recovery, and cleanup are complete. It applies only to the native callable `exec_command`; similarly named, sibling, or non-shell tools keep their existing behavior.

## Verified callable contract

The current native registry resolves `tools.exec_command` to one callable with required string `cmd`; optional `workdir`, `yield_time_ms`, `max_output_tokens`, shell, login, terminal, justification, and approval fields; and returned output, wall time, optional exit code, token count, chunk handle, and session handle. The verified contract hash is `890eee7bc866789c1e70f071a9c0b342917f25cc2638f3b2b79780469f470f7c`. The callable can change state and is not generally idempotent.

## Required behavior

- `B-66624905d73b`: For text or file search, use `rg` or `rg --files` first. Use the next capable local method only when `rg` is unavailable.
- `B-c9cb3a4918f7`: Batch independent reads and checks. Run them concurrently only when results remain separately attributable; sequence dependencies and shared mutable state with one writer.
- `B-e4e528347ac4`: Set an explicit `workdir` whenever directory context matters. Never repurpose `HOME`, `home`, or `CODEX_HOME` as task variables.
- `B-c46083cf74ac`: Do not add cosmetic `echo` or `printf` separator commands to a chained invocation. Split work or label evidence outside the shell output.
- `B-c500fb1baa36`: Treat backticks and `$()` inside `cmd` as executable shell syntax. Remove unintended interpolation and choose quoting that cannot expose sensitive data in output; stop when no safe representation exists.
- `B-84fcb4b4eb05`: Keep `yield_time_ms` at or below 30000. Do not use a blocking sleep or wait longer than 60 seconds. Preserve a returned `session_id` and continue or interrupt that owned session through the session-control callable.
- `B-1c388240357e`: Set a bounded `max_output_tokens`. Treat truncation or an ongoing session as incomplete evidence; retrieve the missing bounded segment or narrow the command before relying on it.
- `B-97c2d87f44b7`: Before a destructive command, resolve and validate exact narrow targets and authority. Never use a home directory, filesystem root, unresolved variable, glob, or command substitution as a destructive target. Prefer recoverable operations and verify the final state.

## Result and retry rules

Classify a returned result from `exit_code`, `output`, `original_token_count`, `chunk_id`, `session_id`, and elapsed time. A missing exit code with a session handle means ongoing work, not success. Truncated output cannot prove an omitted fact. A nonzero exit is a command failure even when some output is useful.

Retry only when the command is proved idempotent, non-execution is proved, or an authoritative readback proves the intended effect absent. When execution is unknown, inspect state first. Preserve command, workdir, relevant options, exit state, and the evidence used for the conclusion without logging secrets.

## Enforcement limit

These rules are instruction-only. This reference does not prove that the host intercepts direct calls, enforces shell policy, or supplies atomic rollback. Stronger prevention needs a verified host policy layer, proxy, or restricted command implementation.
