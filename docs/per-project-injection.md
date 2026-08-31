# Per-project injection

The global install routes (skills.sh, plugin marketplaces) make every skill
discoverable to every project on a machine. That is the right default for a
developer who wants the whole toolkit everywhere. It is the wrong default for
a team that wants one or two skills in one repository only, with no global
state and no context tokens spent on skills that repository never loads.

Per-project injection is the opt-in alternative. It copies a selected subset
of skills into a target project, records exactly what it copied in a
manifest, and removes exactly that on revert. It is a plain shell script with
no runtime, no daemon, no network, and no dependency beyond a POSIX shell and
the standard file utilities.

## When to use it

- You want skills scoped to one repo, not installed for every project.
- You work in an air-gapped or offline environment where the global CLI and
  marketplaces cannot reach a registry.
- You want to pin a skill to a specific commit and not inherit later changes
  until you re-inject.
- You want to keep the context footprint small by carrying only the skills a
  project uses.

## How it works

The script `scripts/inject-skills.sh` reads the canonical skill tree in this
repository and writes a copy into `<target>/.agent-skills/` by default. It
writes a manifest at `<target>/.agent-skills/.inject-manifest.json` that lists
every file it copied. Revert reads that manifest and deletes only those files,
then prunes the empty directories it created.

Two copy modes control the footprint:

- `default` (omitted flag): copies everything a skill needs to run, excluding
  test fixtures in `evals/`, local CI in `.github/`, test code in
  `scripts/tests/`, and the image prompt shards in `assets/prompts/`. These
  never run inside a consuming project.
- `--slim`: copies only the parts an agent reads at runtime, namely
  `SKILL.md`, `references/`, `examples/`, and `scripts/`. This is the smallest
  footprint and the lowest token cost when an agent loads the whole skill body.

## Commands

List the skills available to inject:

```sh
scripts/inject-skills.sh --list
```

Inject two skills into a project, slim footprint:

```sh
scripts/inject-skills.sh ./my-app --skills timebox,goal-prompt --slim
```

Inject every skill into a project, default footprint, into a custom folder:

```sh
scripts/inject-skills.sh ./my-app --all --into .skills
```

Revert a previous injection:

```sh
scripts/inject-skills.sh --revert ./my-app --into .skills
```

If you omit `--into` on revert, it defaults to `.agent-skills`, the same
default used by inject.

## Safety

- The script refuses to overwrite an existing manifest unless you pass
  `--force`, so a second inject never silently changes what a revert will undo.
- Revert only deletes paths listed in the manifest, and only paths that resolve
  inside the destination directory. A path that starts with `/` or `..` is
  skipped, so a hand-edited manifest cannot reach outside the target.
- The script copies with `cp -p` so file timestamps are preserved, which keeps
  diff and cache behavior predictable.
- Injection adds nothing to your shell profile, your global config, or any
  registry. Removing the injected directory and its manifest is a complete
  uninstall.

## Pinning to a release

Injection copies from whatever checkout you run it in. To pin a release,
check out the tagged commit before injecting:

```sh
git clone https://github.com/srinitude/skills
cd skills
git checkout v0.1.0
scripts/inject-skills.sh ../my-app --skills timebox,goal-prompt --slim
```

The manifest records the `toolkit` field as `srinitude/skills` but does not
record a version. To track which release a project is pinned to, commit the
manifest and note the tag in your project changelog or a comment beside it.

## Reverting after manual edits

If a teammate edits an injected skill in place, revert still removes the
file because revert keys on the manifest path list, not on file content. If
you want to keep local edits, copy the skill out of the injected directory
before reverting, or do not revert and remove the manifest files manually.
