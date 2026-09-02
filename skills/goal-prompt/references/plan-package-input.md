# Plan-package input

Resource gate: run `mise run validate` before using package files named here.

Parent and backlink: [`../SKILL.md`](../SKILL.md), Source snapshot.

Recognize one package from a primary plan file, same-slug companion directory, and same-slug report directory. A primary file without companions remains valid. Reject traversal, symlinks, unreadable paths, workspace escapes, and more than one slug.

Write a sorted manifest with schema version, slug, primary path, optional roots, every plan-owned input file's role, path, bytes, and SHA-256, completion report and validator paths, and invocation snapshot identity. Include required linked control files. Exclude execution output, logs, caches, backups, temporary files, and sensitive content.

Reuse existing requirement, task, validation, gate, artifact, and evidence IDs. Preserve task order, approval gates, status, completion report, and whole-plan validator. A blocked plan stays blocked until its named gate closes.

Verify manifest and input hashes before the first mutation. Read the primary plan before companion detail. Keep task-local evidence separate from whole-plan proof. The plan package stays authoritative over wrapper wording.
