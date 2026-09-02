# Complete documentation inventory

Resource gate: run `mise run validate` before using package files named here.

Parent and backlink: [`../SKILL.md`](../SKILL.md), Procedure step 3.

Use this branch only when the rewrite claims complete coverage of official documentation or documented primitives.

1. Fetch the current official documentation root, navigation index, and full-text corpus when those surfaces exist.
2. Record URL, fetch time, SHA-256, bytes, and lines for each source.
3. Parse real page markers or destinations. Require unique paths and nonempty bodies.
4. Inventory the root plus every live page. Do not use a public sitemap as the only page list when the canonical corpus exposes more pages.
5. Record canonical URL, title, digest rule, size, headings, relevant rule IDs, disposition, reason, and reviewed state.
6. Parse Markdown link destinations from navigation data and reconcile every destination to a page or proved alias.
7. Merge duplicate rules into stable IDs and keep reverse coverage from pages to rules.
8. Fail on unread pages, unreviewed rows, empty bodies, unmatched navigation, or relevant rules without an owner.

Installation guides and catalogs still need inventory rows even when they add no runtime rule. Execution must refetch current sources when the planning snapshot is stale.
