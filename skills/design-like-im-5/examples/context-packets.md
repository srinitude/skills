# Context packet example

Guess removed: A short action may omit needed judgment context.

## Request

> Prepare the source meaning packet before any product judgment.

## Commands

```sh
mise run run-start --intake evals/files/valid-intake.json --run-dir run
mise run run-packet --run-dir run --action source_meaning
```

## Real output

```text
{"next_action": "source_meaning", "run_id": "48843a797566d628", "status": "READY"}
{"action": "source_meaning", "status": "PACKET_READY"}
```

The commands exit with codes `0` and `0`. The second creates one packet file.

`run/packets/source_meaning.json` via `mise run run-scaffold`

```text
Mise owner: mise run run-scaffold
{"action":"source_meaning","allowed_decisions":["PASS","REVISE","BLOCKED"],"context_bundle":{"do_not_substitute":"Do not replace source meaning with a remembered pattern or a surface copy. Keep this bar.","load_when":"Before a source is turned into a product rule or design direction. Load it then.","produce":"A source_meaning model record with used paths, gaps, evidence, counterevidence, and uncertainty. Save this proof.","required_paths":["assets/context-bundle.schema.json","assets/model-record.schema.json","evals/context-cases.json","evals/source-mapping.json","examples/context-packets.md","examples/run.md","references/context-routing.md","references/research.md","mise run source-lineage","mise run run-packet"],"route_id":"CTX-SOURCE-MEANING","route_sha256":"686b3db1241fe7b5df45508eed2675e47428af777623903570e742c6e5bc03d8","support":{"assets":[{"contribution":"Defines evidence, counterevidence, uncertainty, options, and the chosen direction. Use this map.","path":"assets/model-record.schema.json"},{"contribution":"Requires all routed context classes and their contributions. Use this map.","path":"assets/context-bundle.schema.json"}],"evals":[{"contribution":"Tests source age, rights, location, and counterreading coverage. Try this case.","path":"evals/context-cases.json"},{"contribution":"Links source-backed claims to their canonical evidence owner. Try this case.","path":"evals/source-mapping.json"}],"examples":[{"contribution":"Shows a source packet that acknowledges context before judgment. Match this scene.","path":"examples/context-packets.md"},{"contribution":"Shows the real source packet path and surrounding run state. Match this scene.","path":"examples/run.md"}],"references":[{"contribution":"Defines source gathering, source meaning, rights, gaps, and evidence separation. Read this guide.","path":"references/research.md"},{"contribution":"Adds the questions that expose conflicting readings and missing context. Read this guide.","path":"references/context-routing.md"}],"scripts":[{"contribution":"Builds and records the source action packet without interpreting the source. Run this tool.","path":"mise run run-packet"},{"contribution":"Checks that public source paths and hashes remain current. Run this tool.","path":"mise run source-lineage"}]}},"forbidden_claims":["unseen pixels","missing sources","causal impact"],"goal":"Make one evidence-backed design judgment.","inputs":{"audience":"New account owners.","outcome":"Build a clear account setup flow.","platform":"Responsive web.","primary_tasks":["Create an account","Fix input errors"],"proof_threshold":"Each task works in wide and narrow views.","source_permissions":["public_web","local_files"]},"item_id":null,"output_schema":"assets/model-record.schema.json","pass_rule":"PASS needs all fields and no open veto.","reason_codes":["CLEAR","NEEDS_PROOF","VETO","STALE","OBJECTIVE_FAILURE","HARM_CHECK","CHECK_MEANING"],"required_evidence":["source","location","observation","reason"],"required_rules":["EYE_FIRST","BRAIN_ONE_STEP","TOUCH_CLEAR","NO_COLOR_ONLY","KEEP_INPUT","MOTION_ALT","WHOLE_SERVICE","SOURCE_IDEA","ADAPT_SPACE","STATE_OPEN","HUMAN_SWEEP","HARM_CHECKS","ONE_CHECK_ONE_MEANING"],"run_id":"48843a797566d628","source_locations":[],"version":"1.0.0","vetoes":["safety","access","understanding","agency"]}
```

## Passing context record

`run/../evals/files/valid-context-record.json` via `mise run run-scaffold`

```text
Mise owner: mise run run-scaffold
{
  "action": "source_meaning",
  "decision": "PASS",
  "evidence": ["source:current"],
  "reason": "Current source facts, rights, gaps, and counterreadings support the claim.",
  "counterevidence": ["No conflicting current source was found."],
  "uncertainty": "The next product state may add more source context.",
  "affected": ["state_judgment"],
  "context_acknowledgements": [
    "assets/context-bundle.schema.json",
    "assets/model-record.schema.json",
    "evals/context-cases.json",
    "evals/source-mapping.json",
    "examples/context-packets.md",
    "examples/run.md",
    "references/context-routing.md",
    "references/research.md",
    "mise run source-lineage",
    "mise run run-packet"
  ],
  "missing_context": []
}
```

## Blocked context record

`run/../evals/files/missing-context-record.json` via `mise run run-scaffold`

```text
Mise owner: mise run run-scaffold
{
  "action": "source_meaning",
  "decision": "BLOCKED",
  "evidence": ["route:CTX-SOURCE-MEANING"],
  "reason": "A needed research file is not here, so the source claim must wait.",
  "counterevidence": ["The packet and source map are here."],
  "uncertainty": "The lost file may change how the source is read.",
  "affected": ["state_judgment", "select_rules"],
  "context_acknowledgements": [
    "assets/context-bundle.schema.json",
    "assets/model-record.schema.json",
    "evals/context-cases.json",
    "evals/source-mapping.json",
    "examples/context-packets.md",
    "examples/run.md",
    "references/context-routing.md",
    "mise run source-lineage",
    "mise run run-packet"
  ],
  "missing_context": ["references/research.md"]
}
```

The model reads each named path. Missing required context keeps the affected claim blocked.

The owning Mise task checks that accounting. It does not judge the control.
