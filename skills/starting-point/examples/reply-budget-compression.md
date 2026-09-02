# The analysis was right and the reply was too long

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this before sending a reply that contains your own reasoning, tables, or step numbers. Verbosity is the failure this skill causes most often, because it runs a five-point map, a route comparison, and a proof checklist before answering.

Guess it removes: how much of the private analysis the user should see, and whether a correct argument justifies its own length.

## The same request, two replies

> Our onboarding conversion is bad. Can you A/B test the signup button color this week?

## Before, 368 words, every claim defensible

> I want to put two numbers in front of you first, because I think this test spends your week and returns nothing.
>
> **Step 1, the outcome.** You want more users completing onboarding. The requested work is a color experiment on the signup button.
>
> **Step 2, the proof.** A color test proves something only if it can reach significance. At 95% confidence and 80% power, the users per arm you would need are:
>
> | Baseline conversion | 10% relative lift | 5% relative | 2% relative |
> | ------------------- | ----------------- | ----------- | ----------- |
> | 5%                  | 31,234            | 122,124     | 752,703     |
> | 10%                 | 14,751            | 57,763      | 356,334     |
> | 20%                 | 6,510             | 25,583      | 158,150     |
> | 40%                 | 2,389             | 9,493       | 59,058      |
>
> Published button color effects cluster in the zero to two percent relative range, and the famous exceptions were contrast changes on pages where the call to action was hard to find. So the realistic ask is the right-hand column, six figures per arm, in seven days. If you do not have that traffic, the test ends at "no significant difference", which is not the same as "color does not matter", and you will have learned nothing either way.
>
> **Step 3, the route comparison.** I considered the requested path, an upstream path, and reuse of existing analytics. The requested path is aimed at the wrong step: the signup button is upstream of onboarding, so it governs who enters the funnel rather than who finishes it. If people drop at email verification, at a permissions screen, or at an empty first-run state, button color is downstream of nothing that matters.
>
> **Step 4, the unknowns.** To tell you which of those is true I need your weekly signup-page traffic and the step-by-step drop-off through onboarding. One number and one funnel. If that lives in your analytics tool or warehouse, point me at it or paste it and I will come back with where the leak actually is and what test is worth the week.
>
> **Step 5, the decision.** I am not cancelling your test. If you still want the color test after seeing these numbers, say so and I will spec it properly: variant assignment, primary metric definition, guardrail metrics, a fixed sample-size stopping rule instead of peeking, and a pre-registered statement of what we conclude if it is flat.

## After, 139 words, same decision

> I can set it up, but one number first.
>
> At 95% confidence and 80% power, detecting a 2% relative lift needs about 158,000 users per arm at a 20% baseline, or 356,000 at a 10% baseline. Button color effects are usually that small or smaller, so unless your signup page sees six figures of weekly traffic, the test ends at "no significant difference" and you learn nothing either way.
>
> Separately, the signup button is upstream of onboarding. You said onboarding conversion is the problem, and the button is what gets people into the funnel rather than through it.
>
> Send me weekly signup-page traffic and the step-by-step drop-off, and I will tell you which step is actually leaking. If you still want the color test after that, say so and I will spec it with a fixed sample-size stopping rule.

## What was cut, and why it was safe to cut

- The step numbers. They are the private map. A user reading numbered reasoning is reading your notes.
- Three of four table rows. Two computed figures carry the same decision, and the reader has one baseline, not four.
- The route comparison. The user needs the conclusion, not the candidates that lost.
- The full specification list. It becomes an offer of one line, expanded only if the user accepts.
- The hedge about famous exceptions. It defends a claim nobody disputed yet.

Nothing load-bearing was cut. The decision, the two numbers, the scope mismatch, the request for data, and the offer to proceed all survive.

## The test to apply before sending

Count what the user can see. If it is more than what you did, what you did not do, the one assumption most likely to be wrong, and the one thing you need from them, the extra text is your notes leaking out.

Compare lengths with the request. A one-sentence question earns a short answer even when the honest answer is unwelcome. Push-back does not buy extra length; it buys one extra number.

Cut the third supporting argument first. The first is the answer, the second is the proof, and the third reads as a lecture.
