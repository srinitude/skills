# Example: researched verdict with insufficient evidence

## User says

```text
/would-humans-actually verdict Would remote workers post a public weekly goal for eight weeks?
```

## Executor replies

```text
Verdict: INSUFFICIENT EVIDENCE. The checked primary sources support mechanism questions but do not observe the target action or provide a matched denominator. I created the verdict artifact and its validator passed.
```

## Commands run

```text
$ python3 - <<'PY'
import html, re, urllib.request
urls = [
  'https://pubmed.ncbi.nlm.nih.gov/11795063/',
  'https://pubmed.ncbi.nlm.nih.gov/17907866/',
]
for url in urls:
    request = urllib.request.Request(url, headers={'User-Agent': 'srinitude-skills-example/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode('utf-8', errors='replace')
        match = re.search(r'<title>(.*?)</title>', body, re.I | re.S)
        title = ' '.join(html.unescape(match.group(1)).split()) if match else 'title unavailable'
        print(f'{response.status} {url} {title}')
PY
200 https://pubmed.ncbi.nlm.nih.gov/11795063/ Efficacy of the Theory of Planned Behaviour: a meta-analytic review - PubMed
200 https://pubmed.ncbi.nlm.nih.gov/17907866/ A new look at habits and the habit-goal interface - PubMed
exit 0

$ python3 scripts/validate_verdict.py --input ../../.artifacts/example-runs/human-verdict.md
{"errors": [], "input": "../../.artifacts/example-runs/human-verdict.md", "status": "PASS"}
exit 0
```

## Files created

`../../.artifacts/example-runs/human-verdict.md`

```markdown
# Human action verdict: public weekly goal posts

## Exact behavior

Remote knowledge workers would publish one personally meaningful work goal to a team-visible board every Monday and leave it visible through Friday for eight consecutive weeks, instead of keeping goals private. The request did not define employer rules, incentive, privacy controls, or target population beyond remote work.

## Verdict

**Verdict:** INSUFFICIENT EVIDENCE
**Confidence:** None
**Why not higher:** The checked sources discuss intention and habit mechanisms but do not observe the target behavior, population, setting, cost, denominator, or eight-week window.

## Evidence ledger

| Load-bearing claim                               | Direct or inference | Supporting sources                                                   | Opposing sources                 | Independence check             | Fit and limit                                 | Verdict effect                 |
| ------------------------------------------------ | ------------------- | -------------------------------------------------------------------- | -------------------------------- | ------------------------------ | --------------------------------------------- | ------------------------------ |
| Intent does not establish repeated public action | Inference           | [Planned behavior review](https://pubmed.ncbi.nlm.nih.gov/11795063/) | None found in this bounded check | One source only for this claim | Broad behavior review; no public-goal outcome | Prevents a directional verdict |
| Stable cues and repetition may matter            | Inference           | [Habit-goal review](https://pubmed.ncbi.nlm.nih.gov/17907866/)       | None found in this bounded check | Independent author team        | Mechanism only; no target completion rate     | Shapes the proposed test only  |

## Reference class and transport

No matched reference class with the same action, population, team visibility, privacy cost, frequency, and eight-week window was found in the bounded source check. No numerator, denominator, or probability is defensible.

## Mechanisms

| Mechanism                                     | Support                             | Opposition                                         | Distinguishing observation                                         |
| --------------------------------------------- | ----------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------ |
| Stable weekly cue may support repetition      | Habit-goal review, mechanism only   | Public visibility may add privacy and status costs | Compare private and team-visible posting under the same weekly cue |
| Public commitment may increase follow-through | Not verified in the checked sources | Workers may avoid exposing uncertain goals         | Measure eligible weekly posts and opt-outs by condition            |

## Evidence and scope limits

The checked sources do not study remote workers posting goals to coworkers for eight weeks. No direct target outcome, independent replication, matched denominator, employer-policy context, or cultural subgroup evidence was found. This result does not predict every workplace or establish that public posting improves performance.

## What would change the verdict

Two independent field datasets with the same observable action, eligible denominator, privacy conditions, and eight-week retention window could support a direction. Strong refusal or attrition under a close field test could support an unlikely verdict.

## Next ethical test

Recruit consenting remote workers from the target setting. Randomize a private-goal board and a team-visible board only after employer and participant approval. Count every eligible participant and each of eight weekly opportunities. Prespecify completion, attrition, opt-out, privacy, deletion, and stop rules. Use no employment consequences. The result changes whether a public default is considered.

## Sources

1. [Efficacy of the Theory of Planned Behaviour: a meta-analytic review](https://pubmed.ncbi.nlm.nih.gov/11795063/) for the intent and behavior distinction.
2. [A new look at habits and the habit-goal interface](https://pubmed.ncbi.nlm.nih.gov/17907866/) for cue, repetition, and mechanism questions.

## Research log

Query: remote workers public weekly goal posting eight weeks. Primary records opened on 2026-07-29: both source URLs returned HTTP 200 and their titles matched the records. Excluded: no target field study was identified in this bounded example. Validator output is recorded in the example run.
```

## What the run proves

The completed artifact follows the public contract and the bundled validator exits 0 with `"status": "PASS"`.
