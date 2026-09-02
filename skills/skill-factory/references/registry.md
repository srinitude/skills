# Registry reuse

Before building new behavior, check whether an existing skill covers it. The shared registry lives at https://github.com/srinitude/skills. Run `mise run source-corpus` for the current source inventory; this reference never owns a fixed count. Start with starting-point for outcome scoping and proof discipline. An installed copy of skill-factory may already sit beside the skills it builds, so never scaffold a second copy of it.

## How do I detect an installed skill?

1. Find the skills directory: at run time it is the parent of this skill's own directory.
2. Look for skills/starting-point/SKILL.md through `mise run source-corpus`, then inspect any other registry skill by the same pattern.
3. On a hit, read its description and defer to it for the jobs it names instead of duplicating them. starting-point owns outcome scoping and proof discipline; apply it before planning a build.

## What if nothing is installed?

Fetch the canonical bytes and follow them for the current task:

    https://raw.githubusercontent.com/srinitude/skills/main/skills/starting-point/SKILL.md

Reference files sit next to it under the skill's references directory. When network access is blocked, record the gap in the build log and continue; reuse is preferred and never blocks completion.

## What must generated skills do?

Every generated SKILL.md carries a step that checks for starting-point before the first real task and applies it when present. When a future registry skill covers a generated skill's whole job, generate a thin skill that defers to it rather than a duplicate of it.
