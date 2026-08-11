# Hermes official docs inventory (complete-coverage plans)

Use when a plan or rewrite claims rules for **every official Hermes docs page** or **every documented Hermes primitive**.

Typical artifacts (profile/workspace report dir):

| Artifact | Role |
|---|---|
| `docs-inventory.json` | Root page + every `llms-full` source marker |
| `primitive-catalog.json` | Stable `PRIM-###` merge of normative rules |
| `baseline.json` | Task 1 hashes only; leave untouched in Task 2 |

Example report dir used on this workflow: `.hermes/reports/hermes-primitives-policy/`.

## Live endpoints

Fetch all three from the official site (planning snapshot is evidence only; execution re-fetches):

| Endpoint | Role |
|---|---|
| `https://hermes-agent.nousresearch.com/docs` | Root docs page (separate inventory row) |
| `https://hermes-agent.nousresearch.com/docs/llms.txt` | Navigation / index entries for cross-check |
| `https://hermes-agent.nousresearch.com/docs/llms-full.txt` | Full page bodies with source markers |

Do **not** treat the public sitemap as the page list. It may only expose the `/docs` root while the real corpus lives in `llms-full.txt`.

HTTP: use a normal client with a descriptive User-Agent (e.g. `Hermes-Agent/policy-execution`). Record `url`, fetch time, `sha256`, byte length, and line count for each endpoint.

## Split the full corpus

1. Download `llms-full.txt`.
2. Split on markers of the form `<!-- source: <path> -->`.
3. Require unique source paths and non-empty bodies.
4. Inventory rows = **1 root** + **every live source marker**. The live marker count wins over any earlier planning count.

Regex shape used successfully for body split:

```python
pattern = re.compile(
    r'^<!-- source: (.+?) -->\n(.*?)(?=\n---\n\n<!-- source: |\Z)',
    re.M | re.S,
)
```

Marker-only scan (counts / path lists):

```python
markers = re.findall(r'^<!-- source: (.+?) -->', full_text, re.M)
```

## source_path → canonical_url

Source markers look like `website/docs/.../*.md`. Public docs URLs drop the `website` prefix, drop `.md`, and drop a trailing `/index` segment for directory indexes:

```python
def public_path(source_path: str) -> str:
    x = source_path
    if x.startswith('website'):
        x = x[len('website'):]
    if x.endswith('.md'):
        x = x[:-3]
    if x.endswith('/index'):
        x = x[:-6]
    if not x.startswith('/'):
        x = '/' + x
    return x.rstrip('/') or '/docs'

canonical_url = 'https://hermes-agent.nousresearch.com' + public_path(source_path)
# root row: source_path == 'root' → https://hermes-agent.nousresearch.com/docs
```

## Inventory row fields

For each page (root + every source marker):

- `source_path` (or `root` for `/docs`)
- `canonical_url`
- `title` (first **semantic** H1 when present; exclude synthetic path-slug H1s)
- `page_digest` (sha256 of delimiter-trimmed body normalized to no leading blank line and exactly one trailing LF; full recipe in `hermes-primitives-policy-evidence`)
- `byte_count` / `char_count` (delimiter-trimmed body sizes; may differ from the digest canon when a leading blank was stripped only for hashing)
- optional `heading_policy` / `page_digest_policy` strings so later gates recompute the same way
- `relevant_primitive_ids`
- `normative_rules` (short list of must/must-not/may statements found)
- `source_anchors` (complete H1–H3 display text; protect inline code before stripping markdown delimiters; do not erase `*`, `<>`, or spaces that belong in the heading)
- `disposition`: one of `SOUL`, `AGENTS`, `covered_existing`, `procedure_only`, `not_runtime_policy`
- `disposition_reason` (required for `procedure_only` and `not_runtime_policy`)
- `reviewed` (bool; must be true before PASS)

Installation guides, platform walkthroughs, catalogs, and developer internals still get rows even when they add no universal runtime rule.

## Nav cross-check (llms.txt)

1. Parse **markdown links**, not bare path fragments. Relative-only regexes miss absolute URLs and undercount entries.

```python
# Prefer this: every markdown destination
links = set(re.findall(r'\]\(([^)]+)\)', llms_txt))
nav = {
    u.split('#')[0].rstrip('/')
    for u in links
    if u.startswith('https://hermes-agent.nousresearch.com/docs')
}
```

2. Match each nav URL to a source row via `canonical_url` **or** a documented alias.
3. Fail the audit on unmatched nav entries, unread rows, unreviewed rows, empty bodies, or relevant-but-unmapped primitive IDs.

### Nav aliases (path transform alone is not enough)

Some live nav URLs do not equal `public_path(source)`. Record them under inventory `aliases` as `nav_url → source_path` and clear `unmatched_nav_*` only after every alias is proven against a real marker:

| Nav URL (examples) | Source marker |
|---|---|
| `.../docs/guides/build-a-hermes-plugin` | `website/docs/developer-guide/plugins/index.md` |
| `.../docs/integrations/index` | `website/docs/integrations/index.md` (nav keeps `/index`; transform drops it) |
| `.../docs/user-guide/messaging/index` | `website/docs/user-guide/messaging/index.md` (same `/index` mismatch) |

When `unmatched_nav_count > 0`: search markers for the last path segment / topic keywords; do not invent sources. Prefer aliases over changing `public_path` for one-off guide redirects.

## Primitive catalog

1. Merge duplicate rules across pages into stable `PRIM-###` entries.
2. Each entry names: scope, source pages, rule force, target owner (`SOUL` / `AGENTS` / skill / docs), and proposed live text when runtime policy must carry it.
3. Keep reverse coverage: every inventory row maps to zero or more catalog IDs, and every relevant catalog ID maps back to pages.
4. Runtime policy gets the smallest routing rule that makes the primitive discoverable. Long recipes stay in skills or live docs.

## Ownership defaults

- **SOUL:** identity, source precedence, task validation, universal safety, tool/state/primitive selection, durability boundary (session-local vs durable work), availability checks against the live surface.
- **AGENTS:** profile paths, workspace boundaries, artifact locations, work modes, source-study rules, Git controls, backend path ownership, profile isolation, surface-aware delivery (e.g. TUI cron without live delivery).
- **Skills / live docs:** setup recipes, platform walkthroughs, catalogs, developer internals, task-specific runbooks.

## JSON checks objects (recommended)

`docs-inventory.json` → `checks`:

- `inventory_rows`, `expected_rows` (markers + 1 root)
- `source_marker_count`, `unique_source_paths`, `duplicate_source_paths`
- `nav_entries`, `unmatched_nav_entries`, `unmatched_nav_count`
- `unread_rows`, `unreviewed_rows`, `relevant_unmapped_rows`
- `all_bodies_nonempty`

`primitive-catalog.json` → `checks`:

- `catalog_entries`, `inventory_rows`
- `reverse_coverage_complete`, `relevant_unmapped_count`
- `nav_entries`, `unmatched_nav_count`

## Temp scripts and residue

- Builders/verifiers: write under `/tmp` (or OS tempfile), run, delete in the same turn.
- Do **not** leave `fix_*.py` / `_build_*.py` under the report dir.
- After writes: `json.loads` both artifacts; list the report dir and confirm only intended JSON files remain (plus pre-existing `baseline.json` when present).

## Acceptance

- Inventory rows = root page + every live source marker.
- Unique `source_path`s; all bodies non-empty; all rows reviewed.
- Zero unread, unreviewed, unmatched nav (after documented aliases), or relevant-but-unmapped rows.
- Catalog reverse coverage complete; every `relevant_primitive_ids` set ⊆ catalog IDs.
- Planning digest recorded; execution re-fetch required; digest change expands the audit rather than justifying the old snapshot.
- Label verification **ad-hoc** unless a full suite exists.
