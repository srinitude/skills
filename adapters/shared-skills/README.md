# Shared skill-directory placement

This integration verifies the `.agents/skills` discovery convention described in
[the current Agent Skills client guide](https://agentskills.io/client-implementation/adding-skills-support).
It performs a read-only preflight. It does not install or change permissions.

The supported paths are `~/.agents/skills/<name>` for user availability and
`<project>/.agents/skills/<name>` for project availability. These are host discovery
conventions, not Agent Skills frontmatter fields. Use this adapter only when the
current host supports those roots. Native client roots, custom search paths, and
plugin scope controls require that client's integration and current documentation.

Run `mise run check-skill-destination -- --scope project --project <project>
--name <name> --dest <project>/.agents/skills/<name>`. User scope uses `--scope user`
and the user destination. `--home` provides the host's user root for controlled
fixtures or configured hosts. Include `--project` when checking user installation
alongside an active project's skills so duplicate names can be detected.

The JSON receipt identifies scope, exact destination, verified discovery roots,
and the owning reference. Pass it as `--placement-receipt` to the factory operation
that performs placement. A mismatch or an existing same-name skill in another
checked root blocks placement. The factory repeats that collision check immediately
before accepting a variant. This adapter makes no claim about other roots or
unverified precedence rules.
