# A method constraint that may be fixed, and contradicts itself

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this before deciding that a stated method is optional, before silently resolving a constraint that cannot hold, and before deciding whether a preview default is scope expansion.

Guess it removes: whether "use regex only, no libraries" is a fixed constraint or a candidate path, which clause to honor when both cannot hold, and whether shipping a dry run by default overrides what the user asked for.

## What the user said

> Write a python script that renames all the files in a folder to snake case. Use regex only, no libraries.

## Classification

Resource gate: run `mise run validate` before using package files named here.

Fixed. It is explicit, emphatic, and stated twice. Row one of the table in [`../references/constraint-classes.md`](../references/constraint-classes.md). Treating it as a candidate path and shipping a helper library would ignore the clearest instruction in the request.

It is also impossible as written: the regular expression engine is a library, and listing a directory needs another one. Evident intent is no third-party or convenience helpers. Honor that, do every name transformation with the regular expression engine, and say which clause was relaxed in one sentence.

## The reply the skill should produce

> `snake_rename.py` is in your working directory. It previews by default and renames only with `--apply`, because renaming is not undoable.
>
> On "no libraries": it imports `os`, `re`, and `sys`. Nothing third-party. There is no way to list a directory or rename a file without `os`, and `re` is the regular expression engine you asked for, so I read the constraint as no helper libraries and did every transformation with `re.sub`. Tell me if you meant something stricter.
>
> I ran it against a fixture folder I created. Two behaviors worth checking against what you wanted: `.tar.gz` keeps only the last extension and becomes `spaced_out_name_tar.gz`, and a name that is all punctuation becomes `file.txt`. Collisions get a numeric suffix instead of overwriting, subdirectories are skipped, and `already_snake.py` and `.env` are left alone.

## The script that run created

```python
#!/usr/bin/env python3
"""Rename files in a folder to snake case using regular expressions only.

Preview is the default. Nothing is renamed until you pass --apply.

Usage:
    python3 snake_rename.py <folder>
    python3 snake_rename.py <folder> --apply
"""
import os
import re
import sys

SPLIT = re.compile(r"^(.*?)(\.[^.]+)?$")


def to_snake(name):
    parts = SPLIT.match(name)
    stem, ext = parts.group(1) or "", (parts.group(2) or "").lower()
    if not stem:
        return name
    stem = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", stem)
    stem = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", stem)
    stem = re.sub(r"[^A-Za-z0-9]+", "_", stem)
    stem = re.sub(r"^_+|_+$", "", stem).lower()
    return (stem or "file") + ext


def free_name(folder, target, taken):
    parts = SPLIT.match(target)
    stem, ext = parts.group(1) or "", parts.group(2) or ""
    candidate, index = target, 1
    while candidate in taken or os.path.exists(os.path.join(folder, candidate)):
        candidate = "%s_%d%s" % (stem, index, ext)
        index += 1
    return candidate


def main(argv):
    apply_changes = "--apply" in argv[1:]
    args = [item for item in argv[1:] if not item.startswith("-")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: python3 snake_rename.py <folder> [--apply]")
        return 2
    folder, taken, planned = args[0], set(), []
    for name in sorted(os.listdir(folder)):
        if not os.path.isfile(os.path.join(folder, name)):
            continue
        new = to_snake(name)
        if new == name:
            continue
        new = free_name(folder, new, taken)
        taken.add(new)
        planned.append((name, new))
    for old, new in planned:
        print("%s -> %s" % (old, new))
        if apply_changes:
            os.rename(os.path.join(folder, old), os.path.join(folder, new))
    print("%d file(s) %s" % (len(planned), "renamed" if apply_changes else "would be renamed; pass --apply"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

## The run

The fixture folder `sample/` was created for this run and holds no user data. It contains `My File.TXT`, `camelCaseName.md`, `HTTPServerLog.txt`, `  spaced--out__name!!.tar.gz`, `already_snake.py`, `.env`, `report v2.PDF`, `PascalCase`, `###.txt`, a colliding `dup Name.txt` and `dup_name.txt` pair, and a `nested/` subdirectory.

```
$ python3 snake_rename.py sample
  spaced--out__name!!.tar.gz -> spaced_out_name_tar.gz
###.txt -> file.txt
HTTPServerLog.txt -> http_server_log.txt
My File.TXT -> my_file.txt
PascalCase -> pascal_case
camelCaseName.md -> camel_case_name.md
dup Name.txt -> dup_name_1.txt
report v2.PDF -> report_v2.pdf
8 file(s) would be renamed; pass --apply
exit=0

$ python3 snake_rename.py sample --apply
  spaced--out__name!!.tar.gz -> spaced_out_name_tar.gz
###.txt -> file.txt
HTTPServerLog.txt -> http_server_log.txt
My File.TXT -> my_file.txt
PascalCase -> pascal_case
camelCaseName.md -> camel_case_name.md
dup Name.txt -> dup_name_1.txt
report v2.PDF -> report_v2.pdf
8 file(s) renamed
exit=0

$ ls -A sample
.env
already_snake.py
camel_case_name.md
dup_name.txt
dup_name_1.txt
file.txt
http_server_log.txt
my_file.txt
nested
pascal_case
report_v2.pdf
spaced_out_name_tar.gz

$ python3 snake_rename.py sample
0 file(s) would be renamed; pass --apply
exit=0

$ python3 snake_rename.py
usage: python3 snake_rename.py <folder> [--apply]
exit=2
```

## Replies that fail

Resource gate: run `mise run validate` before using package files named here.

> Here is a script that renames all your files to snake_case.

No run, no output, no exit code. The script row of the proof threshold table in [`../references/proof-checklist.md`](../references/proof-checklist.md) wants execution against representative inputs, not code that reads correctly.

> Here is the script. Note it uses `pathlib` and `slugify`, which are cleaner than raw regex.

The constraint was fixed and was dropped without asking.

> Here is the script. It previews changes.

Preview is mentioned, the flag is not. The user runs it, sees nothing change, and reports it as broken.

## Why the good reply is the right one

Preview by default is the reversible form of the requested outcome, not a widened scope, and the flag is named in one sentence so the safe first run cannot be mistaken for a failure. The destructive path was demonstrated on a fixture, never on the user's folder.

The contradiction was named once and resolved in the open. The reply is short because the analysis behind it stays private: the user gets the file, the one clause that was relaxed, and the two behaviors most likely to surprise them.

The double extension result is disclosed rather than fixed. Extending the script to treat `.tar.gz` as one extension is a scope decision that belongs to the user, and the disclosure is one clause long.
