# Place progressive disclosure within the heading tree

- Keep disclosure routes under the right topic and load their detail at the point of need.

## Reading route

- Use this guide when selecting a disclosure location, splitting a branch, or reviewing a reading path.

### Prerequisites and scope

- Prerequisites: the source text, intended reader, source topic map, target format, and applicable live language and meaning rules. No other guide must be read first to understand these placement rules.
- Read before choosing a disclosure location, moving detail, or checking a split. These rules govern the skill package and every future Markdown output and linked child.
- The [skill entry](../SKILL.md) is a navigation-only return route. It supplies no required context to this file.

- Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.

## Choose the place by meaning

- Decide both where a route belongs and when its detail becomes necessary.

### Find the owning heading

- A disclosure is a link to further detail or a supported control that reveals it. Its owner is the most specific active heading whose topic includes that detail. Use the source topic map, not visual closeness, file length, or folder depth, to find that owner.
- Place the link or control inside that owner's section at the point of need, after enough context to explain its purpose and immediately before the first action or explanation that depends on it. Keep it before the next sibling or shallower heading closes that section. Optional detail belongs beside the claim or topic it expands.
- For detail about one H4 subsection, place the disclosure within that H4 section. Do not attach it to a neighboring H4, an unrelated H3, or a generic links section merely because the destination resolves.
- If the detail forms a real child subsection, keep the needed child heading and place the disclosure there with a short statement of its purpose. Do not leave an empty heading or disguise a required subsection as a link label. At H6, use an in-section link and a child file; never invent H7.
- Keep the parent's core meaning, essential conditions, warnings, and next action visible. Move non-core detail only. A title and an unexplained link cannot replace required context.

### Place shared and required context

- If several sibling sections need the same prerequisite, introduce its route under their nearest shared ancestor immediately before the first dependent branch. If the whole file needs it, introduce its route under the H1 before the first dependent section. Load only the shared context needed by the active branch; this placement does not trigger every sibling branch.
- Give each disclosure a clear destination label, scope, and reading trigger. State whether it is required before an action, required only when a condition holds, or optional supporting detail. Do not make a required read look optional.
- A local reminder may point to the same shared source where needed. Keep one content owner, reuse current context, and avoid duplicate rule blocks or automatic rereads. A global index may help navigation but cannot replace the local route at the point of need.
- Keep section ownership and prerequisite order distinct. If a needed source belongs to a later branch, introduce a clear earlier prerequisite route without moving the source under a false parent. Resolve a real dependency cycle before acceptance.

### Load detail just in time

- Treat disclosure placement and context loading as separate checks. The route must be easy to find at the point of need; its linked detail must be loaded when its stated condition becomes true, before the dependent work starts.
- Keep always-needed rules and context in the entry path. Keep branch detail behind its own trigger. Do not load every child at startup, hide a needed prerequisite until after its use, or move a route to the file's end simply to collect links.
- When a branch becomes active, read its missing prerequisites first, then the needed detail, then do the dependent work. Follow the same rule at each depth. Reuse complete, current text already in context under the existing reread rules.
- For a required step, place the route before that step. For a conditional exception, place it with the rule and condition it changes. For optional explanation, place it beside the relevant point without making it a prerequisite. Keep essential warnings visible before the action they govern.
- Record the need that triggers each disclosure, the earliest point where the reader has enough context, and the first dependent passage. Judge timing within that window; file length, heading depth, and link position alone cannot prove it is just in time.

## Preserve structure when splitting

- Move a coherent non-core branch while keeping its parent relationship and essential context visible.

### Move a coherent branch

1. Record the source heading path, moved content, retained core, intended destination, and reason for the split.
2. Move the selected non-core branch without changing its parent-child meaning, conditions, exceptions, or required order.
3. Keep a useful summary and disclosure route at the owning source section. Preserve any real subsection heading and make the continuation's scope clear.
4. Give the child file its own title, H2 and H3 minimum, and any needed deeper headings. Its local heading levels may restart; record how its topic still belongs to the original branch. Do not copy the parent's heading depth blindly or detach the meaning from its parent.
5. State the child's own prerequisites. Keep a return link navigation-only. If parent and child would require each other, retain necessary core in the parent or place shared context in a source both can read first, then recheck the full dependency path.
6. Repeat the placement and size review for each child. Update source links, heading fragments, relative paths, and reading triggers after every move.

### Keep visible and loaded context honest

- A collapsible block remains part of its source file and loaded context. It does not meet the file-splitting rule or reduce physical lines.
- When a supported disclosure control is useful, keep it within its owning section and apply the [keyboard, label, state, export, and visibility checks](readability.md). Essential prerequisites and warnings stay visible before the action they govern.
- If the target strips or cannot use the control, use a supported in-place link or visible form that keeps the same meaning and reading route. Report any unresolved target limit.

## Check placement before acceptance

- Validate the active heading owner, the reading trigger, and the destination together.

### Check the file and joined reading path

- Record the source heading path, actual disclosure location, destination heading, reading trigger, and first dependent passage. Confirm that the intended owner is still active at the disclosure location.
- Compare the topic map with the source and parsed outline. Check rendered placement when a target is available, including generated headings, includes, nested lists, and quotes that can change the visible structure.
- Review semantic ownership by reading the linked content in context. A valid path, valid anchor, or correct heading count does not prove that the link belongs there.
- Test premature loading of inactive branches, detail loaded after dependent work, correctly timed reuse of current context, and disclosures under the correct H2-H6 owner, a shared prerequisite at the common ancestor, a link moved past a closing sibling heading, a link under the wrong sibling, a prerequisite introduced too late, a detached generic links section, a recursive child split, and an H6 continuation. Reject the misplaced cases even when all links resolve.
- Recheck after repairs. Keep unresolved ownership or prerequisite conflicts visible and withhold acceptance of the affected path. When maintaining this skill, update its instructions and behavior checks; distinguish actual test runs from planned tests.
