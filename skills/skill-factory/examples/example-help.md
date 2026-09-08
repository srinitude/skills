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

The following excerpts were observed from public tasks. Readiness details and unrelated help paragraphs are omitted; no files were created.

```text
$ mise run new -- --help
usage: scaffold_skill.py [-h] --name NAME --description DESCRIPTION
                         --scope {user,project}
                         [--placement-receipt PLACEMENT_RECEIPT] --dest DEST
exit 0

$ mise run variant -- plan --help
--source SOURCE
--source-id SOURCE_ID
--scope {user,project}
--name NAME
--dest DEST
--project PROJECT
--project-id PROJECT_ID
--refresh
--in-place
exit 0
```

The plan operation resolves the source, target scope, identity, destination, and project context. The review operation prepares a digest-bound draft. Accept validates the completed review, adapted behavior, and package before promotion. Load references/scope-variants.md through `mise run variant` for the full workflow and failure branches.

## What the run proves

The scaffold requires an explicit scope. Both variant directions use the same public operation. Help output proves interface availability; the behavioral tests establish adaptation and preservation for their exercised cases.
