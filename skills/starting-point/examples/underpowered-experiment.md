# The route is valid and cannot produce a detectable result

Resource gate: run `mise run validate` before using package files named here.

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this when the requested route is causally sound but the effect size, sample size, traffic, budget, or time window makes its proof unreachable.

Guess it removes: whether an experiment that is safe and legitimate still counts as a weak route, and whether arithmetic you performed yourself is allowed as the evidence that justifies saying so.

## What the user said

> Our onboarding conversion is bad. Can you A/B test the signup button color this week?

## The check that fires

Resource gate: run `mise run validate` before using package files named here.

No bottleneck is in evidence, no route has stalled, and a color test is safe, so the older signal list would have let this pass. The signal that fires is the sixth one in [`../references/core-loop.md`](../references/core-loop.md): the route is causally plausible and its proof is unreachable in the stated window. Compute the requirement before agreeing.

Arithmetic you can show is allowed evidence. A recalled prior about typical color effects is not the same thing, so it is labeled as a rough expectation and the user is asked for the one number that settles the question.

## The computation

```python
#!/usr/bin/env python3
"""Users per arm needed for a two-proportion test at 95% confidence and 80% power."""
import math
import sys

Z_ALPHA, Z_BETA = 1.959964, 0.841621


def per_arm(baseline, relative_lift):
    treated = baseline * (1 + relative_lift)
    pooled = (baseline + treated) / 2
    numerator = (Z_ALPHA * math.sqrt(2 * pooled * (1 - pooled))
                 + Z_BETA * math.sqrt(baseline * (1 - baseline) + treated * (1 - treated))) ** 2
    return math.ceil(numerator / (treated - baseline) ** 2)


def main():
    lifts = [0.10, 0.05, 0.02]
    print("baseline | " + " | ".join("%+d%% relative" % (lift * 100) for lift in lifts))
    for baseline in (0.05, 0.10, 0.20, 0.40):
        row = [format(per_arm(baseline, lift), ",") for lift in lifts]
        print("%6.0f%%   | %s" % (baseline * 100, " | ".join(row)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```
$ python3 sample_size.py
baseline | +10% relative | +5% relative | +2% relative
     5%   | 31,234 | 122,124 | 752,703
    10%   | 14,751 | 57,763 | 356,334
    20%   | 6,510 | 25,583 | 158,150
    40%   | 2,389 | 9,493 | 59,058
exit=0
```

## The reply the skill should produce

> I can set it up, but one number first.
>
> At 95% confidence and 80% power, detecting a 2% relative lift needs about 158,000 users per arm at a 20% baseline, or 356,000 at a 10% baseline. Button color effects are usually that small or smaller, so unless your signup page sees six figures of weekly traffic, the test ends at "no significant difference" and you learn nothing either way.
>
> Separately, the signup button is upstream of onboarding. You said onboarding conversion is the problem, and the button is what gets people into the funnel rather than through it.
>
> Send me weekly signup-page traffic and the step-by-step drop-off, and I will tell you which step is actually leaking. If you still want the color test after that, say so and I will spec it with a fixed sample-size stopping rule.

That is 139 words. The full analysis behind it is roughly three times longer and stays private.

## Replies that fail

> Sure. Here is how to set up a color test in your experiment tool, step by step.

Serves the request, ignores the outcome, and spends the week to produce a flat result nobody can interpret.

> Button color tests do not work. Your real problem is the onboarding funnel. Here is a six-step audit plan.

Overrides the user's decision without asking, drops the requested work, and replaces it with unrequested strategy work.

> Before we start: what is your baseline conversion, your weekly traffic, your current funnel, your experiment tooling, and your definition of onboarding?

Four questions and no output. Only one of them gates the answer.

## Why the good reply is the right one

It computes the requirement instead of asserting that the test is pointless, and the numbers come from a script that ran rather than from memory. The prior about typical effect sizes is stated as a rough expectation and kept out of the computed numbers.

It names the scope mismatch in one sentence and stops. It asks for the single number that settles the decision. It keeps the requested test on the table with a concrete offer, because dropping requested work needs the user's approval.

It fits the reply budget. Three of the four table rows and the entire statistics discussion stay in the working notes, because the user asked a one-sentence question.
