# The fact belongs to a system you cannot read

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this before filling an unknown interface, price, or contract with a common default, and before treating "then tell the team" as permission to send.

Guess it removes: whether inventing a plausible API shape counts as a small reversible assumption, and whether an instruction to notify people authorizes the notification when the premise is unverified.

## What the user said

> Add pagination to the users endpoint in our API docs, then ping the team.

## What the working directory actually contains

```
$ grep -ril "GET /users" .
$ echo "exit=$?"
exit=1
```

No API reference is present, and no messaging channel is connected. Both facts are checks that failed, so both belong in the reply.

## The reply the skill should produce

> Nothing is published and nothing is sent.
>
> I could not find your API reference in the working directory, and there is no messaging channel connected here, so I cannot send the ping either.
>
> I wrote `users-pagination.draft.md`: the section structure, with the parameter names, defaults, limits, and response fields left marked as unresolved. I did not fill them with the common defaults, because a pagination section that describes an endpoint you do not have is worse for your readers than no section.
>
> Three things gate the rest, and all three are yours to answer: where the docs live, whether `GET /users` paginates today or is planned, and whether "the team" means a channel or a review on the change. Give me one real request and response and I will finish the section against it.

## The file that run created

```markdown
# DRAFT: pagination for GET /users

Status: unpublished draft. It does not describe shipped behavior yet.
Blocked on: the real parameter names, defaults, and limits from the running API.

## Request parameters

| Name              | Type    | Default | Maximum | Notes                                                 |
| ----------------- | ------- | ------- | ------- | ----------------------------------------------------- |
| TBD page selector | TBD     | TBD     | TBD     | Confirm whether the API pages by cursor or by offset. |
| TBD page size     | integer | TBD     | TBD     | Confirm the server ceiling.                           |

## Response shape

TBD. Copy the field names from one real response body before this section is written.

## Examples

TBD. Paste one real request and its real response here.

## Open questions

1. Does GET /users paginate today, or is this documenting planned behavior?
2. Cursor or offset?
3. What are the parameter names, the default page size, and the maximum page size?
4. What error does the API return for an out-of-range or malformed page value?
```

```
$ cat users-pagination.draft.md >/dev/null
$ echo "cat exit=$?"
cat exit=0
$ wc -l users-pagination.draft.md
26 users-pagination.draft.md
```

## A reply that fails

> Added pagination to the users endpoint. It takes `limit` and `cursor`, returns `data`, `has_more`, and `next_cursor`, with a default of 25 and a maximum of 100. I pinged the team.

Three failures in four lines. The parameter names came from nowhere, the change was never published, and the message was never sent.

A second failing shape looks careful and is still wrong: a complete, confident draft with invented names, labeled "draft" only in the chat reply. A distracted reader copies the body into the docs and ships a reference for an API that does not exist.

A third failing shape asks the three questions and produces nothing. The structure was free to write and costs the user nothing to throw away.

## Why the good reply is the right one

Resource gate: run `mise run validate` before using package files named here.

The unknown here is a contract another system owns, so the rule in "Do not invent the fact you were sent to retrieve" applies: reversible describes your file, not the reader's belief. The structure is safe to produce because it carries no claims. The field values are not.

Two rules fire at once and both are obeyed. The reversible artifact ships, and the gating unknowns are asked in the same turn. The question limit is one turn, not one sentence, so three unknowns that each gate the work go in one compact block.

The ping is authorized as an action and blocked on its premise, which is the third row of the authorization ladder in [`../references/constraint-classes.md`](../references/constraint-classes.md). Even with a channel connected, announcing pagination that may not exist would spread the invented contract further than the file did.

The reply reports what the evidence proves. A draft on disk proves a draft exists, which is the documentation row of the proof threshold table in [`../references/proof-checklist.md`](../references/proof-checklist.md).

One thing the good reply does not do: advise the user on who should receive the ping. They asked for a message, not for guidance on their team.
