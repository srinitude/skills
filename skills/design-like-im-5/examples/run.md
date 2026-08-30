# Run example

Guess removed: A run may hide the rich scaffold or its files.

## Request

> Build a clear setup flow for new account owners. It must work on wide and narrow web views.

## Visible reply

I will start the fixed run and make the first model packet.

## Commands

```sh
python3 scripts/run_pipeline.py start --intake evals/files/valid-intake.json --run-dir run
python3 scripts/run_pipeline.py packet --run-dir run --action source_meaning
```

## Real output

```text
{"next_action": "source_meaning", "run_id": "48843a797566d628", "status": "READY"}
{"action": "source_meaning", "status": "PACKET_READY"}
```

The first command exits with code `0`. The second command exits with code `0`.

## Every created file

`run/capabilities.json`

```text
{"items":[{"id":"files","state":"UNKNOWN"},{"id":"commands","state":"UNKNOWN"},{"id":"web","state":"UNKNOWN"},{"id":"browser","state":"UNKNOWN"},{"id":"render","state":"UNKNOWN"},{"id":"capture","state":"UNKNOWN"},{"id":"motion","state":"UNKNOWN"},{"id":"vision","state":"UNKNOWN"}],"version":"1.0.0"}
```

`run/dependency-manifest.json`

```text
{"dtcg_run":{"status":"BLOCKED"},"parts":[],"version":"1.0.0"}
```

`run/dtcg-route.json`

```text
{"needs":["tokens","evidence","proof","visual review"],"skill":"dtcg-tokens","state":"NEEDS_DISCOVERY","version":"1.0.0"}
```

`run/packets/source_meaning.json`

```text
{"action":"source_meaning","allowed_decisions":["PASS","REVISE","BLOCKED"],"context_bundle":{"do_not_substitute":"Do not replace source meaning with a remembered pattern or a surface copy. Keep this bar.","load_when":"Before a source is turned into a product rule or design direction. Load it then.","produce":"A source_meaning model record with used paths, gaps, evidence, counterevidence, and uncertainty. Save this proof.","required_paths":["assets/context-bundle.schema.json","assets/model-record.schema.json","evals/context-cases.json","evals/source-mapping.json","examples/context-packets.md","examples/run.md","references/context-routing.md","references/research.md","scripts/check_source_lineage.py","scripts/run_pipeline.py"],"route_id":"CTX-SOURCE-MEANING","route_sha256":"46e4f0d6675cba351bcfde1f2ed5c0d5c6f019daaef4fe96835897eb116183ff","support":{"assets":[{"contribution":"Defines evidence, counterevidence, uncertainty, options, and the chosen direction. Use this map.","path":"assets/model-record.schema.json"},{"contribution":"Requires all routed context classes and their contributions. Use this map.","path":"assets/context-bundle.schema.json"}],"evals":[{"contribution":"Tests source age, rights, location, and counterreading coverage. Try this case.","path":"evals/context-cases.json"},{"contribution":"Links source-backed claims to their canonical evidence owner. Try this case.","path":"evals/source-mapping.json"}],"examples":[{"contribution":"Shows a source packet that acknowledges context before judgment. Match this scene.","path":"examples/context-packets.md"},{"contribution":"Shows the real source packet path and surrounding run state. Match this scene.","path":"examples/run.md"}],"references":[{"contribution":"Defines source gathering, source meaning, rights, gaps, and evidence separation. Read this guide.","path":"references/research.md"},{"contribution":"Adds the questions that expose conflicting readings and missing context. Read this guide.","path":"references/context-routing.md"}],"scripts":[{"contribution":"Builds and records the source action packet without interpreting the source. Run this tool.","path":"scripts/run_pipeline.py"},{"contribution":"Checks that public source paths and hashes remain current. Run this tool.","path":"scripts/check_source_lineage.py"}]}},"forbidden_claims":["unseen pixels","missing sources","causal impact"],"goal":"Make one evidence-backed design judgment.","inputs":{"audience":"New account owners.","outcome":"Build a clear account setup flow.","platform":"Responsive web.","primary_tasks":["Create an account","Fix input errors"],"proof_threshold":"Each task works in wide and narrow views.","source_permissions":["public_web","local_files"]},"item_id":null,"output_schema":"assets/model-record.schema.json","pass_rule":"PASS needs all fields and no open veto.","reason_codes":["CLEAR","NEEDS_PROOF","VETO","STALE","OBJECTIVE_FAILURE","HARM_CHECK","CHECK_MEANING"],"required_evidence":["source","location","observation","reason"],"required_rules":["EYE_FIRST","BRAIN_ONE_STEP","TOUCH_CLEAR","NO_COLOR_ONLY","KEEP_INPUT","MOTION_ALT","WHOLE_SERVICE","SOURCE_IDEA","ADAPT_SPACE","STATE_OPEN","HUMAN_SWEEP","HARM_CHECKS","ONE_CHECK_ONE_MEANING"],"run_id":"48843a797566d628","source_locations":[],"version":"1.0.0","vetoes":["safety","access","understanding","agency"]}
```

`run/rebuild-queue.json`

```text
{"items":[],"reason_codes":["STALE_DEP","LAYER_SKIP"],"version":"1.0.0"}
```

`run/render-plan.json`

```text
{"items":[],"prompts_are_exhaustive":false,"state_source":"state-matrix.json#items","version":"1.0.0","view_prompts":["wide","narrow","whole","close"]}
```

`run/retrieval-manifest.json`

```text
{"content_hashes":[],"items":[],"version":"1.0.0"}
```

`run/review-checklist.json`

```text
{"decision_rules":{"BLOCKED":"A named proof need is missing, old, or not seen.","NOT_APPLICABLE":"The checked event cannot occur here. Proof and a reason are still needed.","PASS":"The named proof shows no listed failure in this scene.","REVISE":"The named proof shows a listed failure or a failed veto."},"human_source_command":"python3 scripts/human_capability_sweep.py","human_source_script":"scripts/human_capability_sweep.py","invariants":{"brain":["brain-current","brain-next","brain-model","brain-memory","brain-choice","brain-language","brain-feedback","brain-risk","brain-context","brain-unknown"],"eye":["eye-first","eye-order","eye-group","eye-state","eye-reading","eye-color","eye-focus","eye-range","eye-motion","eye-content"],"touch":["touch-target","touch-spacing","touch-reach","touch-input","touch-affordance","touch-response","touch-gesture","touch-repair","touch-settings","touch-effort"]},"item_count":70,"meaning_lock":"Each ID uses the one question, probe order, proof list, failure signs, and result rules in the source script.","negative_invariants":{"bad_design":["bad-design-hidden-state","bad-design-false-priority","bad-design-misleading-control","bad-design-no-feedback","bad-design-lost-work","bad-design-inaccessible-core","bad-design-danger-close","bad-design-fixed-context","bad-design-fragmented-system","bad-design-shifted-burden"],"bad_output":["bad-output-ungrounded-claim","bad-output-unseen-pass","bad-output-missing-state","bad-output-fixed-state-set","bad-output-incomplete-checklist","bad-output-no-options","bad-output-script-judgment","bad-output-stale-proof","bad-output-broken-lineage","bad-output-vague-result"],"bad_practice":["bad-practice-style-first","bad-practice-surface-copy","bad-practice-screen-first","bad-practice-premature-choice","bad-practice-no-counterevidence","bad-practice-happy-path-only","bad-practice-access-late","bad-practice-hidden-cost","bad-practice-metric-overreach","bad-practice-false-polish"],"objective_failure":["objective-text-overlap","objective-image-overlap","objective-clipped-meaning","objective-covered-control","objective-off-view","objective-target-collision","objective-focus-trap","objective-cue-loss","objective-state-conflict","objective-task-dead-end"]},"open_human_set":true,"owner":"script","required_answer_fields":["scene","observation","evidence","decision","reason","alternatives","uncertainty"],"review_owner":"model","source_command":"python3 scripts/review_checklist.py","source_script":"scripts/review_checklist.py","version":"1.0.0"}
```

`run/run-log.json`

```text
{"events":[{"kind":"START","run_id":"48843a797566d628"}],"version":"1.0.0"}
```

`run/run.json`

```text
{"context_routing_sha256":"46e4f0d6675cba351bcfde1f2ed5c0d5c6f019daaef4fe96835897eb116183ff","intake":{"audience":"New account owners.","outcome":"Build a clear account setup flow.","platform":"Responsive web.","primary_tasks":["Create an account","Fix input errors"],"proof_threshold":"Each task works in wide and narrow views.","source_permissions":["public_web","local_files"]},"next":"source_meaning","rules":["EYE_FIRST","BRAIN_ONE_STEP","TOUCH_CLEAR","NO_COLOR_ONLY","KEEP_INPUT","MOTION_ALT","WHOLE_SERVICE","SOURCE_IDEA","ADAPT_SPACE","STATE_OPEN","HUMAN_SWEEP","HARM_CHECKS","ONE_CHECK_ONE_MEANING"],"run_id":"48843a797566d628","status":"READY","version":"1.0.0"}
```

`run/source-queue.json`

```text
{"items":[],"permissions":["public_web","local_files"],"version":"1.0.0"}
```

`run/state-matrix.json`

```text
{"coverage_prompts":["no content","work in progress","partial result","failure","repair","offline","permission","interruption","success"],"discovery_dimensions":["user_goal","task","data","system","environment","device","input","access","time","risk","content","social_setting","prior_action"],"exhaustive":false,"items":[],"required_lenses":["eye","brain","touch","objective failure","bad design","bad output","bad practice","access","agency"],"rule":"Add, split, merge, or retire items when evidence changes.","state_set":"OPEN_CONTEXT_DERIVED","version":"1.0.0"}
```

`run/viewport-matrix.json`

```text
{"items":[],"prompts_are_exhaustive":false,"version":"1.0.0","view_prompts":["wide","narrow","whole","close"]}
```

No value was guessed. Open lists stay ready for current proof.
