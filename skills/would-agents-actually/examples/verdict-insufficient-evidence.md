# Example: researched verdict with insufficient evidence

## User says

```text
/would-agents-actually verdict Will the pinned system send a message and verify delivery?
```

## Executor replies

```text
Verdict: INSUFFICIENT EVIDENCE. The checked primary sources define evaluation requirements but provide no target-system run or destination readback. I created the verdict artifact and its validator passed.
```

## Commands run

```text
$ python3 - <<'PY'
import html, re, urllib.request
urls = [
  'https://arxiv.org/abs/2407.01502',
  'https://arxiv.org/abs/2406.12045',
]
for url in urls:
    request = urllib.request.Request(url, headers={'User-Agent': 'srinitude-skills-example/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode('utf-8', errors='replace')
        match = re.search(r'<title>(.*?)</title>', body, re.I | re.S)
        title = ' '.join(html.unescape(match.group(1)).split()) if match else 'title unavailable'
        print(f'{response.status} {url} {title}')
PY
200 https://arxiv.org/abs/2407.01502 [2407.01502] AI Agents That Matter
200 https://arxiv.org/abs/2406.12045 [2406.12045] $τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains
exit 0

$ mise run validate-verdict --input ../../.artifacts/example-runs/agent-verdict.md
{"errors": [], "input": "../../.artifacts/example-runs/agent-verdict.md", "status": "PASS"}
exit 0
```

## Files created

Resource gate: run `mise run validate` before using package files named here.

`../../.artifacts/example-runs/agent-verdict.md`

```markdown
# Agent action verdict: send and verify a message

## Exact action

Under an approved send request, the target system would call the configured messaging tool, receive transport acceptance, and independently read back the message at the intended destination within the declared budget. The request did not provide a versioned system pin, task set, destination, permissions, trials, or readback mechanism.

## Verdict

**Verdict:** INSUFFICIENT EVIDENCE
**Confidence:** None
**Scope:** An unpinned system, unspecified messaging environment, and no completed trials.

## Pinned system card

Model identifier, provider route, prompts, runtime, tools, schemas, permissions, memory, environment, retries, fallbacks, budgets, comparator, and success readback were not supplied. A substantive verdict is blocked until these fields are pinned.

## Evidence ledger

| Conclusion                                                             | Direct or inference | Evidence class | System and tasks                | Metric and denominator | Independent support                                                     | Bias and transport limits       | Verdict effect                |
| ---------------------------------------------------------------------- | ------------------- | -------------- | ------------------------------- | ---------------------- | ----------------------------------------------------------------------- | ------------------------------- | ----------------------------- |
| The full system and cost should be evaluated together                  | Inference           | Method source  | No match to target system       | No target denominator  | [Cost-aware evaluation paper](https://arxiv.org/abs/2407.01502/)        | Method only; no target run      | Requires a system pin         |
| Tool interaction should be checked against environment state and rules | Inference           | Method source  | Different tasks and environment | No target denominator  | [State-based tool interaction study](https://arxiv.org/abs/2406.12045/) | Benchmark transport is unproved | Requires destination readback |

## Trial metrics

No target tasks or trials were run. Single-run outcome, propensity, pass@k, pass^k, cost, latency, uncertainty, and failure concentration are not estimable.

## Outcome, trace, and constraints

No tool trace, transport receipt, destination state, permission record, grader check, or infrastructure status was supplied. A completion claim would not substitute for destination readback.

## Outside view and transport

The checked papers provide evaluation methods, not a matched base rate for the target messaging system. The target runtime, task source, permissions, destination, tool schema, budgets, and grader differ or are unknown.

## Mechanisms

| Mechanism                             | Direction         | Evidence             | Competing explanation                   | Separating observation                                |
| ------------------------------------- | ----------------- | -------------------- | --------------------------------------- | ----------------------------------------------------- |
| Tool selection and argument formation | Raises or lowers  | No target trace      | Transport failure after a correct call  | Inspect call payload and transport receipt separately |
| Independent destination readback      | Raises confidence | Method evidence only | A receipt may not mean visible delivery | Query destination state after each eligible attempt   |

## Limits and safety boundary

This result does not establish that any system can or will send the message, that delivery is authorized, or that the content and destination are safe. It is an action-evidence verdict only.

## What would change the verdict

A pinned system and repeated representative trials with visible opportunity counts, complete traces, transport status, permission checks, independent destination readback, and two independent task sets could support a direction.

## Next safe test

Use a sandbox destination, synthetic content, least-privileged credentials, representative frozen tasks, a disjoint holdout, prespecified trials and reset rules, deterministic receipt and destination graders, permission checks, cost and latency budgets, timeouts, a kill switch, idempotency, readback, rollback, and cleanup.

## Sources

1. [AI Agents That Matter](https://arxiv.org/abs/2407.01502/) for full-system and cost-aware evaluation concerns.
2. [A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045/) for state-based outcome and policy evaluation.

## Research log

Primary records opened on 2026-07-29: both source URLs returned HTTP 200 and their titles matched the records. No target system trace or environment was available. Validator output is recorded in the example run.
```

## What the run proves

The completed artifact follows the public contract and the bundled validator exits 0 with `"status": "PASS"`.
