#!/bin/sh
# inject-skills.sh
#
# Copy a selected subset of Agent Skills from this toolkit into a target
# project, or remove exactly what was copied. The script is self contained,
# depends only on a POSIX shell, cp, rm, find, and sed, and writes a manifest
# so a later revert deletes only the files it added.
#
# Why this exists: the global install (npx skills add, plugin marketplaces)
# makes every skill discoverable to every project. Some teams want one or two
# skills in one repo only, with no global state and no extra context tokens
# spent on skills that repo does not use. This script does that copy in,
# records what it copied, and reverts it on request.
#
# Usage:
#   scripts/inject-skills.sh <target-project> [options]
#   scripts/inject-skills.sh --revert <target-project> [options]
#   scripts/inject-skills.sh --list
#   scripts/inject-skills.sh --help
#
# Options:
#   --skills a,b,c      Comma separated skill names to inject. Default: all.
#   --all               Inject all skills (same as omitting --skills).
#   --slim              Copy only runtime readable parts: SKILL.md, references,
#                       examples, and scripts (without tests). Drops evals,
#                       local CI, and image prompt fixtures. Smallest footprint.
#   --into <name>       Destination directory name inside the target project.
#                       Default: .agent-skills
#   --force             Overwrite an existing injection manifest in the target.
#   --revert            Remove a previous injection, using its manifest.
#   --list              Print available skill names, one per line.
#   --help              Print this help.
#
# Exit codes: 0 success, 1 usage error, 2 missing skill or target,
#             3 manifest conflict, 4 partial revert (stray files remain).

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SKILLS_DIR="$REPO_ROOT/skills"
MANIFEST_NAME=".inject-manifest.json"
DEFAULT_INTO=".agent-skills"

print_help() {
  sed -n '3,30p' "$0" | sed 's/^# \{0,1\}//'
}

list_skills() {
  [ -d "$SKILLS_DIR" ] || { echo "no skills directory at $SKILLS_DIR" >&2; exit 2; }
  find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d -printf '%f\n' 2>/dev/null \
    | sort || find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null \
    | while read -r d; do basename -- "$d"; done | sort
}

# Decide whether a path (relative to a skill root, forward slashes) should be
# copied. The default copy keeps everything a skill needs to run, minus test
# fixtures and local CI that a consuming project does not execute.
keep_path_default() {
  case "$1" in
    evals/*) return 1 ;;
    scripts/tests/*) return 1 ;;
    .github/*) return 1 ;;
    assets/prompts/*) return 1 ;;   # image prompt shards, eval only
    */evals/*) return 1 ;;
    */scripts/tests/*) return 1 ;;
    */.github/*) return 1 ;;
    */assets/prompts/*) return 1 ;;
    *) return 0 ;;
  esac
}

# The slim copy keeps only the parts an agent reads at runtime.
keep_path_slim() {
  case "$1" in
    SKILL.md) return 0 ;;
    references/*) return 0 ;;
    examples/*) return 0 ;;
    scripts/tests/*) return 1 ;;
    scripts/*) return 0 ;;
    */SKILL.md) return 0 ;;
    */references/*) return 0 ;;
    */examples/*) return 0 ;;
    */scripts/tests/*) return 1 ;;
    */scripts/*) return 0 ;;
    *) return 1 ;;
  esac
}

json_escape() {
  # Minimal JSON string escape for file paths. Paths here are repo relative,
  # forward slash, no control chars, so this is enough.
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

relpath() {
  # path relative to SKILLS_DIR, using POSIX forward slashes
  _full=$1
  _pref=$SKILLS_DIR/
  case "$_full" in
    "$_pref"*) printf '%s' "${_full#$_pref}" ;;
    *) printf '%s' "$_full" ;;
  esac
}

prune_empty_dirs() {
  # Walk from a leaf directory up to a stop directory, removing empty dirs.
  _leaf=$1
  _stop=$2
  while [ "$_leaf" != "$_stop" ] && [ -d "$_leaf" ]; do
    if [ -z "$(find "$_leaf" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
      rmdir "$_leaf" 2>/dev/null || true
      _leaf=$(dirname -- "$_leaf")
    else
      break
    fi
  done
}

run_inject() {
  _target=$1; shift
  _skills_arg=""
  _mode="default"
  _into="$DEFAULT_INTO"
  _force=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --skills) _skills_arg=$2; shift 2 ;;
      --all) _skills_arg=""; shift ;;
      --slim) _mode="slim"; shift ;;
      --into) _into=$2; shift 2 ;;
      --force) _force=1; shift ;;
      *) echo "unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [ -n "$_target" ] || { echo "target project path required" >&2; exit 1; }
  [ -d "$_target" ] || { echo "target project not found: $_target" >&2; exit 2; }
  _target=$(CDPATH= cd -- "$_target" && pwd)
  _dest=$_target/$_into
  _manifest=$_dest/$MANIFEST_NAME

  if [ -f "$_manifest" ] && [ "$_force" -ne 1 ]; then
    echo "an injection already exists at $_manifest" >&2
    echo "run with --revert to remove it, or --force to overwrite" >&2
    exit 3
  fi

  # Resolve the skill list.
  if [ -n "$_skills_arg" ]; then
    _selected=$(printf '%s' "$_skills_arg" | tr ',' '\n' | sed '/^$/d')
  else
    _selected=$(list_skills)
  fi

  # Validate every requested skill exists.
  _missing=""
  for s in $_selected; do
    [ -d "$SKILLS_DIR/$s" ] || _missing="$_missing $s"
  done
  if [ -n "$_missing" ]; then
    echo "unknown skill(s):$_missing" >&2
    echo "available:" >&2
    list_skills >&2
    exit 2
  fi

  mkdir -p "$_dest"
  : > "$_dest/.inject-files.tmp"

  _count=0
  for s in $_selected; do
    _src=$SKILLS_DIR/$s
    find "$_src" -type f 2>/dev/null | while read -r f; do
      _rel=$(relpath "$f")
      case "$_mode" in
        slim) keep_path_slim "$_rel" || continue ;;
        default) keep_path_default "$_rel" || continue ;;
      esac
      _dst=$_dest/$_rel
      mkdir -p "$(dirname -- "$_dst")"
      cp -p -- "$f" "$_dst"
      printf '%s\n' "$_rel" >> "$_dest/.inject-files.tmp"
    done
    _count=$((_count + 1))
  done

  # Build the manifest JSON.
  {
    printf '{\n'
    printf '  "version": 1,\n'
    printf '  "toolkit": "srinitude/skills",\n'
    printf '  "mode": "%s",\n' "$_mode"
    printf '  "into": "%s",\n' "$(json_escape "$_into")"
    printf '  "skills": ['
    _first=1
    for s in $_selected; do
      [ "$_first" = 1 ] || printf ', '
      printf '"%s"' "$(json_escape "$s")"
      _first=0
    done
    printf '],\n'
    printf '  "files": [\n'
    _first=1
    while read -r rel; do
      [ -n "$rel" ] || continue
      [ "$_first" = 1 ] || printf ',\n'
      printf '    "%s"' "$(json_escape "$rel")"
      _first=0
    done < "$_dest/.inject-files.tmp"
    printf '\n  ]\n'
    printf '}\n'
  } > "$_manifest"
  rm -f "$_dest/.inject-files.tmp"

  _files=$(grep -c '"' "$_manifest" 2>/dev/null || true)
  echo "injected $_count skill(s) into $_dest"
  echo "manifest: $_manifest"
  echo "revert with: $0 --revert <target-project> --into $_into"
}

run_revert() {
  _target=$1; shift
  _into="$DEFAULT_INTO"
  while [ $# -gt 0 ]; do
    case "$1" in
      --into) _into=$2; shift 2 ;;
      *) echo "unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [ -n "$_target" ] || { echo "target project path required" >&2; exit 1; }
  [ -d "$_target" ] || { echo "target project not found: $_target" >&2; exit 2; }
  _target=$(CDPATH= cd -- "$_target" && pwd)
  _dest=$_target/$_into
  _manifest=$_dest/$MANIFEST_NAME

  [ -f "$_manifest" ] || { echo "no injection manifest at $_manifest" >&2; exit 2; }

  # Extract file paths from the manifest with sed. Each files entry is a line
  # like:     "path/to/file"
  _remaining=0
  _deleted=0
  sed -n 's/^[[:space:]]*"[^"]*"[[:space:]]*:.*//; s/^[[:space:]]*"\([^"]*\)"[,[:space:]]*$/\1/p' "$_manifest" \
    | while read -r rel; do
      [ -n "$rel" ] || continue
      # Only delete files that live inside the destination, to avoid path escape.
      case "$rel" in
        ../*|/*) continue ;;
      esac
      f=$_dest/$rel
      if [ -f "$f" ]; then
        rm -f -- "$f"
        _deleted=$((_deleted + 1))
      fi
      prune_empty_dirs "$(dirname -- "$f")" "$_dest"
    done

  rm -f "$_manifest"
  prune_empty_dirs "$_dest" "$_target"
  if [ -d "$_dest" ] && [ -n "$(find "$_dest" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
    echo "reverted injection; destination still has stray files: $_dest" >&2
    exit 4
  fi
  echo "reverted injection at $_dest"
}

main() {
  if [ $# -eq 0 ]; then print_help; exit 1; fi
  case "$1" in
    --help|-h) print_help; exit 0 ;;
    --list) list_skills; exit 0 ;;
    --revert) shift; run_revert "$@"; exit 0 ;;
    --skills|--all|--slim|--into|--force) run_inject "." "$@"; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 1 ;;
    *) run_inject "$@"; exit 0 ;;
  esac
}

main "$@"
