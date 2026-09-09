# Example: the help command

This example explains the public commands and the scope needed before writing.

## User says

```text
What can the skill factory do?
```

## Executor replies

```text
help: show the supported operations.
new <prompt>: create a skill for a stated outcome and scope.
update <path> <prompt>: preserve the skill's purpose, accepted behavior, and valid scope unless a change is requested.
standardize <path>: apply the factory format without replacing the capability.
standardize-target <path> <profile>: plan or apply a profile-bound registry standardization.
refresh-registry-lineage <skill...>: refresh lineage for accepted registry changes.
import <source> <destination>: convert a source into a separate portable package.
variant <source> <user-or-project>: create an independent user-level or project-level variant, or explicitly refresh it from its source.
validate <path>: check changed output; untouched legacy inspection permits missing scope.
eval <path>: check eval contracts and run the applicable behavioral cases.
doctor: report environment readiness.

Choose user for availability across your projects or project for a specific project. The choice is stored once in metadata.scope. A scope label does not install the skill.
```

## Fresh help readback

Load [the full help record](help-run.json) through `mise run new`, `mise run standardize-target` or `mise run variant` before using their flags. It contains actual complete stdout, stderr and exit codes for creation help, standardization help and variant-plan help, with the observed runtime identity. These commands create no target files. Creation exposes `--plan` and `--review`; standardization exposes `--apply`, `--plan-file` and `--review`; variant planning retains its independent scope, project, placement, refresh and in-place branches.

The plan operation resolves the source, target scope, identity, destination and project context. The review operation prepares a digest-bound draft. Accept validates the completed review, adapted behavior and package before promotion. Load references/scope-variants.md through `mise run variant` for the full workflow and failure branches.

## What the run proves

The run record stores complete stdout and stderr in `stdout_base64` and `stderr_base64`. Decode base64 as UTF-8 to read the exact observed streams, including discovery diagnostics. Commands, exit codes, inputs and historical runtime identities are unchanged.

Help output proves interface availability. Source/ledger review, behavioral checks, failure and recovery observations, and current delivery evidence remain separate requirements.
