# Constraint classes

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this reference when the request names a method, tool, library, or format and you are about to treat it as optional, when the stated constraints cannot all hold at once, or when an action is external, irreversible, or destructive.

## Fixed constraint or candidate path

A fixed constraint is part of what the user is buying. A candidate path is one route the user imagined toward something else. Classify before you plan, and say which reading you used whenever the classification could go either way.

| The user says                                             | Class     | Why                                                                                                                                      |
| --------------------------------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| "Use regex only, no libraries"                            | Fixed     | Explicit, emphatic, and repeated. Treat the standard library as permitted, third-party helpers as forbidden, and flag the contradiction. |
| "Just use pandas for this"                                | Candidate | Casual tool preference with no stated reason.                                                                                            |
| "Do it in SQL, our reviewers only read SQL"               | Fixed     | The reason ties the method to acceptance.                                                                                                |
| "Can you loop through and check each one"                 | Candidate | Describes an implementation the user pictured, not a requirement.                                                                        |
| "Follow RFC 7231 exactly"                                 | Fixed     | Contractual and reproducibility bound.                                                                                                   |
| "Reproduce the benchmark with the pinned commit and seed" | Fixed     | Changing a pinned condition destroys comparability.                                                                                      |
| "Show every step of the teacher's five-step method"       | Fixed     | Practicing the method is the outcome.                                                                                                    |
| "Maybe try caching it"                                    | Candidate | Hedged wording, offered as an idea.                                                                                                      |
| "Write it in bash so it runs on the build box"            | Fixed     | An environment limit, not a taste.                                                                                                       |
| "Send it as a PDF"                                        | Fixed     | Format is part of the deliverable.                                                                                                       |
| "Start by listing every file"                             | Candidate | A first step the user sketched, not the result.                                                                                          |
| "Do not touch the database"                               | Fixed     | A prohibition is always fixed.                                                                                                           |

Escalation rule: repetition, emphasis, a stated reason, an environment limit, a review or audit gate, and any prohibition all move a method to fixed. Silence, hedging, and a casual verb leave it a candidate. When it is still unclear, follow the stated method and say in one sentence what you would have done otherwise.

## Contradictory or unclassifiable constraints

A constraint that cannot hold as written is neither class. Do not pick a clause silently and do not treat the pick as a small reversible assumption, because the user cannot see the choice you made.

1. Name the collision in one sentence, using the user's words.
2. Satisfy the evident intent behind the constraint, not the literal text that fails.
3. Say which clause you honored and which you relaxed.
4. Offer the stricter reading as a one-line alternative, and stop there.

Worked line: "Use regex only, no libraries" cannot hold because the regular expression engine is a library and reading a directory needs another. Evident intent is no third-party or convenience helpers. Honor that, do every transformation with the regular expression engine, and say so once.

## Authorization ladder

| Situation                          | Authorized?                                                                                                                        |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| "Email the client the invoice"     | Yes. The action is the request. Send it, then report the delivery evidence.                                                        |
| "Draft an email to the client"     | No. Draft only, and say the message was not sent.                                                                                  |
| "Add the docs, then ping the team" | The ping is authorized, the premise is not. If the documented behavior is unverified, hold the ping and say what would release it. |
| "Fix the tests, then merge"        | Fix authorized. Merge authorized only if the tests actually pass. Otherwise stop and report.                                       |
| "Clean up the old branches"        | Confirm the list first. Destructive, irreversible, and ambiguous in scope.                                                         |
| "Refund everyone affected"         | Hold. Financial, bulk, external, and dependent on eligibility you have not verified.                                               |

The request authorizes the action. It never authorizes the action on a premise you invented. Report delivery as delivery and preparation as preparation.

## Destructive-action default

For anything that deletes, renames, overwrites, moves, or sends in bulk, make preview the default and require an explicit apply flag or confirmation. This is not scope expansion; it is the reversible form of the same outcome. Say in one sentence that preview is the default and name the flag, so the user does not read the safe first run as a broken tool. Never demonstrate the destructive path on the user's data to prove it works. Demonstrate it on a fixture you created, and say which folder you ran it against.
