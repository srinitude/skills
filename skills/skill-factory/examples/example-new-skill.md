# Example: choose scope before a new scaffold

This example covers the scope boundary before implementing a line-budget capability.

## User says

```text
Create a user-level skill scaffold for checking Markdown line budgets. I want it available across my projects. Call it line-budget and keep the package in my authoring directory.
```

## Executor replies

```text
The scaffold records user scope. Its own validator can read that designation. The domain implementation and seeded evals still need work before this is an accepted skill.
```

## Commands run

The authoring directory below is a portable label for the local fixture directory. Readiness output and the absolute created path are omitted from the report excerpt.

```text
$ mise run new -- --name line-budget --description "Use when Markdown line budgets or largest sections must be measured." --scope user --dest <authoring-parent>
files: 42
scope: user
scope_label: user-level
placement: authoring
blocked_until: every SCAFFOLD placeholder is replaced; check_placeholders.py exits 1 until then
exit 0
```

## Resulting metadata

```yaml
metadata:
  author: skill-factory
  version: "0.1.0"
  scope: "user"
```

Use `--scope project` for intended availability in one project. The designation describes availability; the authoring directory does not determine it. When an installation is requested, the integration verifies the destination separately. When scope is unresolved, `mise run resolve-scope` returns the one availability question before creating files. Omitting the scaffold's scope flag exits with a usage error.

## What the run proves

The scaffold has one explicit designation, preserves the standard metadata, and ships its own checker with strict scope acceptance. `mise run test -- -k Scope` verifies creation in both scopes, update preservation, explicit choice, legacy inspection, invalid metadata, and no-write failures. These scope checks do not prove the line-budget behavior or remove the scaffold's unfinished-content gate.
