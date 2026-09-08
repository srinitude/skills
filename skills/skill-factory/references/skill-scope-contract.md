# Skill scope contract

Load this file through `mise run validate` before creating or changing a skill. It extends the [generation contract](generation-contract.md), which owns the package structure and all other frontmatter rules. Copy both files into every generated package so these requirements do not depend on the source installation.

## Designation

Metadata retains author and a quoted version string. Every newly created or updated output stores the string `user` or `project` once as `metadata.scope`. User-level means intended availability across the user's projects; project-level means intended for a specific project or repository. Derive human-readable labels from that field and preserve other metadata. This uses the existing metadata extension point; it adds no top-level Agent Skills field.

## Resolve before writing

Resolve scope before writing. Honor explicit choice and otherwise preserve valid scope on updates. Infer missing scope only from unambiguous intended use and authoritative context; location, current directory, and generic content alone cannot decide it. Ask one concise question before an affected write when evidence is insufficient or conflicting. Legacy inspection may accept an absent designation without assigning one. Acceptance of new or updated output and generated self-validation require valid scope. Invalid values, types, and duplicate keys fail in both modes.

## Operations, variants, and placement

Apply scope to every operation that creates or changes a skill, including standardization and import. A variant is a separate derived skill unless the user explicitly requests in-place adaptation. Resolve source, target scope, unique identity, destination, and target project first. Read the complete relevant source and project context, preserve applicable behavior and attribution, remove private data and hidden installation dependencies when generalizing, and prove both package and adapted behavior. Record actual source identity and immutable digest, both scopes, and adaptations in lineage. Maintain variants independently; an explicit refresh compares baselines and resolves customization conflicts before writing. Classification alone never installs, moves, duplicates, or changes runtime permissions. An existing placement operation verifies scope through its host integration, which owns client paths and resolution rules. The factory's references/scope-variants.md, loaded through `mise run variant`, owns the detailed workflow; generated skills retain this contract without depending on a factory installation.
