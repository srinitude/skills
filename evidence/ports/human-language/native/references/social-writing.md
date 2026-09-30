# Social writing and corpus limits

Use with [writing rules and output checks](writing-rules.md) for posts, captions, replies, or learning from a collection of writing. Read [writing before 2015](pre-2015-writing.md) for fixed historical examples and their preservation limits.

## Write for the exchange

- Know the post's job: report, explain, invite, reply, joke, reflect, or promote. Keep its real point. Do not give every post a hook, a lesson, and a call to reply.
- Use the parent post, thread, link, image, or video when the text depends on it and you can inspect it. If needed context is missing, ask for it or keep the claim narrow. Do not invent what an image shows.
- Keep supplied voice, dialect, line breaks, and fragments when they help. Do not add slang, errors, lowercase text, profanity, or emoji to imitate a person.
- Preserve useful specifics and the author's stance. Numbers and confident language do not prove a claim. Keep predictions, opinions, quoted claims, and observed facts distinct.
- Use a list when the items need scanning. Keep repeated terms for the same thing. Vary pace for meaning; do not use a sentence-length quota.
- Fit the chosen platform and reader. Verify live length or format limits when the task needs them. A captured post may be shortened by a collector rather than by its author.
- Keep a reply or caption clear in its actual setting. If it will stand alone elsewhere, supply the context the new reader needs. Avoid copying unrelated private context into it.

## Learn from data with care

A supplied 2026 collection contains 13,426 records from 5,388 case-sensitive account handles, or 5,387 groups when case is ignored. Its 8,967 `human` and 4,459 `ai` labels have no verified source or accuracy. The collection is evidence about these captured texts, not verified authorship, writing quality, reach, or what readers understood. It is separate from the pre-2015 sample.

Source: `2026-07-03:00:26:05-tweets.jsonl`, SHA-256 `f2d7b1b2ad89fa82f3f40ed11c31cf325367597e8ae97e7854ed3628c7fc5fba`. Local analysis on September 15, 2026 used 30 stated features, duplicate checks, 1,000 author-bootstrap draws, matched groups, an exploratory topic model, and direct reading. No detector or human-reader study was run.

| Finding in this collection | What changes in writing review |
| --- | --- |
| 7,709 captures, 57.4%, have 270–290 characters. Many inspected endings are cut off. | Do not learn an ideal length, abrupt ending, or punctuation habit from the capture boundary. |
| The overall top 100 authors supply 23.7% of all rows. A separate top 100 ranked within the `ai`-labeled group supply 40.8% of that group's rows. | Check author concentration before treating a frequent trait as a general style rule. |
| The raw blank-line gap is about 9.3 percentage points. It is about -0.4 points in 5,202 rows matched by length band, day, and route. | Blank lines do not deserve a blanket ban. The comparison changes which texts are included and does not prove a cause. |
| The raw first-person-term gap is about -32.3 points, but about -5.6 points within the 532 authors present in both groups. | Do not invent “I” stories to match a label. Author mix explains part of the observed difference; the remaining gap is still not proof of authorship. |
| Direct reading found promotional hooks in `human`-labeled texts and useful technical lists in `ai`-labeled texts. Some near-identical captures have opposite labels. | Judge the passage's actual use and evidence. Keep a useful list; check a claim even when its label says human. |

Gaps above are `ai` minus `human`. These are descriptive comparisons with uncertain labels. Matching and author checks reduce some differences but do not remove all topic, language, genre, or collection bias. The topic model suggests a strong AI/tools focus; it is not a validated map of every topic. No engagement data supports claims about reach or persuasion.

When drawing a writing rule from any corpus:

1. Check parsing, missing text, duplicate posts, dates, and the method used to collect it. A collection date is not a publication date.
2. Compare like with like. Length, language, topic, author, genre, and collection route may explain a pattern. Check whether a few accounts dominate it.
3. Read examples and exceptions after measuring them. A count cannot tell whether a repeated phrase was useful, a joke landed, or a reply answered its question.
4. Keep capture artifacts out of style rules. Abrupt endings, wrapped links, and missing punctuation may come from clipping. Whitespace word counts do not measure languages such as Japanese well.
5. Separate a pattern from its cause. Label differences do not prove which traits make writing human, good, or effective. Do not turn these findings into an authorship claim or a detector-evasion recipe.
6. Keep source text and personal data local unless sharing is authorized. Use aggregate results in a reusable skill; do not bundle a private corpus or author profiles.

Qualitative review found useful lists, concrete explanations, firm views, personal stories, marketing hype, clipped text, and multilingual posts across this collection. These observations support choices based on purpose and context. They do not justify copying all traits from a `human` label or rejecting all traits from an `ai` label.

## Check the transfer

Review a clipped post without inventing its ending. Keep a useful list despite its label. Preserve a prediction as a prediction. Explain an image-dependent caption only when its image context is supplied. Keep a requested personal voice without adding life events. Judge the result by meaning, clarity, tone, and task fit; use the cases in [validation](validation.md).
