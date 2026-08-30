# Context packet example

Guess removed: A short action may omit needed judgment context.

## Request

> Review the narrow error state and its covered action.

## Command

```sh
python3 scripts/run_pipeline.py packet --run-dir run --action visual_review --item-id narrow-error
```

## Real output

```text
{"action": "visual_review", "status": "PACKET_READY"}
```

The command exits with code `0`. It creates one packet file.

`run/packets/visual_review--narrow-error.json`

```text
{"action":"visual_review","allowed_decisions":["PASS","REVISE","BLOCKED"],"context_bundle":{"do_not_substitute":"Do not replace direct current render and input inspection with code, captions, or a prior review. Keep this bar.","load_when":"After current renders exist and after every repair rerender. Load it then.","produce":"A visual_review record with every exact check, current proof, alternatives, doubt, and repair result. Save this proof.","required_paths":["assets/context-bundle.schema.json","assets/review-record.schema.json","evals/context-cases.json","evals/evals.json","examples/context-packets.md","examples/run.md","references/context-routing.md","references/review.md","scripts/human_capability_sweep.py","scripts/review_checklist.py","scripts/run_pipeline.py"],"route_id":"CTX-VISUAL-REVIEW","route_sha256":"46e4f0d6675cba351bcfde1f2ed5c0d5c6f019daaef4fe96835897eb116183ff","support":{"assets":[{"contribution":"Defines current views, model reviews, negative reviews, evidence, and decision. Use this map.","path":"assets/review-record.schema.json"},{"contribution":"Requires every support class and path acknowledgement in the packet. Use this map.","path":"assets/context-bundle.schema.json"}],"evals":[{"contribution":"Tests text overlap, image overlap, covered controls, and false checklist passes. Try this case.","path":"evals/context-cases.json"},{"contribution":"Supplies objective failure, bad design, bad output, and bad work cases. Try this case.","path":"evals/evals.json"}],"examples":[{"contribution":"Shows a narrow error review and its missing-render blocked branch. Match this scene.","path":"examples/context-packets.md"},{"contribution":"Shows the full canonical checklist and render plan created for review. Match this scene.","path":"examples/run.md"}],"references":[{"contribution":"Defines whole, close, state, input, relation, and rerender inspection. Read this guide.","path":"references/review.md"},{"contribution":"Supplies rich eye, brain, touch, conflict, and negative-control questions. Read this guide.","path":"references/context-routing.md"}],"scripts":[{"contribution":"Supplies every stable positive and negative review check. Run this tool.","path":"scripts/review_checklist.py"},{"contribution":"Supplies the open human factor sweep for every check. Run this tool.","path":"scripts/human_capability_sweep.py"},{"contribution":"Builds the review packet and validates answer coverage. Run this tool.","path":"scripts/run_pipeline.py"}]}},"forbidden_claims":["unseen pixels","missing sources","causal impact"],"goal":"Make one evidence-backed design judgment.","human_sweep_command":"python3 scripts/human_capability_sweep.py","inputs":{"audience":"New account owners.","outcome":"Build a clear account setup flow.","platform":"Responsive web.","primary_tasks":["Create an account","Fix input errors"],"proof_threshold":"Each task works in wide and narrow views.","source_permissions":["public_web","local_files"]},"item_id":"narrow-error","output_schema":"assets/review-record.schema.json","pass_rule":"PASS needs all fields and no open veto.","reason_codes":["CLEAR","NEEDS_PROOF","VETO","STALE","OBJECTIVE_FAILURE","HARM_CHECK","CHECK_MEANING"],"required_evidence":["source","location","observation","eye","brain","touch","human sweep","objective failure","bad design","bad output","bad practice","reason"],"required_rules":["EYE_FIRST","BRAIN_ONE_STEP","TOUCH_CLEAR","NO_COLOR_ONLY","KEEP_INPUT","MOTION_ALT","WHOLE_SERVICE","SOURCE_IDEA","ADAPT_SPACE","STATE_OPEN","HUMAN_SWEEP","HARM_CHECKS","ONE_CHECK_ONE_MEANING"],"review_checklist":"review-checklist.json","review_checklist_command":"python3 scripts/review_checklist.py","review_owner":"model","run_id":"48843a797566d628","source_locations":[],"version":"1.0.0","vetoes":["safety","access","understanding","agency"]}
```

## Passing context record

`run/../evals/files/valid-context-record.json`

```text
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
    "scripts/check_source_lineage.py",
    "scripts/run_pipeline.py"
  ],
  "missing_context": []
}
```

## Blocked context record

`run/../evals/files/missing-context-record.json`

```text
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
    "scripts/check_source_lineage.py",
    "scripts/run_pipeline.py"
  ],
  "missing_context": ["references/research.md"]
}
```

The model reads each named path. Missing required context keeps the affected claim blocked.

The script checks that accounting. It does not judge the control.
