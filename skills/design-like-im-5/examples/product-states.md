# Product state example

Guess removed: Common state names are a closed product state list.

## Request

> Find the account setup states before choosing a response.

## Commands

```sh
python3 scripts/run_pipeline.py start --intake evals/files/valid-intake.json --run-dir run
python3 scripts/run_pipeline.py packet --run-dir run --action source_meaning
python3 scripts/run_pipeline.py record --run-dir run --result evals/files/valid-context-record.json
python3 scripts/run_pipeline.py packet --run-dir run --action state_judgment
```

## Real output

```text
{"next_action": "source_meaning", "run_id": "48843a797566d628", "status": "READY"}
{"action": "source_meaning", "status": "PACKET_READY"}
{"action": "source_meaning", "status": "RECORDED"}
{"action": "state_judgment", "status": "PACKET_READY"}
```

The commands exit with codes `0`, `0`, `0`, and `0`.

## Open state scaffold

`run/state-matrix.json`

```text
{"coverage_prompts":["no content","work in progress","partial result","failure","repair","offline","permission","interruption","success"],"discovery_dimensions":["user_goal","task","data","system","environment","device","input","access","time","risk","content","social_setting","prior_action"],"exhaustive":false,"items":[],"required_lenses":["eye","brain","touch","objective failure","bad design","bad output","bad practice","access","agency"],"rule":"Add, split, merge, or retire items when evidence changes.","state_set":"OPEN_CONTEXT_DERIVED","version":"1.0.0"}
```

## Full model packet

`run/packets/state_judgment.json`

```text
{"action":"state_judgment","allowed_decisions":["PASS","REVISE","BLOCKED"],"context_bundle":{"do_not_substitute":"Do not replace found states with a fixed happy-path list. Keep this bar.","load_when":"After source meaning is recorded and whenever new evidence changes a state. Load it then.","produce":"A state_judgment record with open states, causes, transitions, reviews, options, and uncertainty. Save this proof.","required_paths":["assets/simplicity-contract.json","assets/state-record.schema.json","evals/context-cases.json","evals/evals.json","examples/context-packets.md","examples/run.md","references/context-routing.md","references/decisions.md","scripts/human_capability_sweep.py","scripts/review_checklist.py","scripts/run_scaffold.py"],"route_id":"CTX-STATE-JUDGMENT","route_sha256":"686b3db1241fe7b5df45508eed2675e47428af777623903570e742c6e5bc03d8","support":{"assets":[{"contribution":"Defines open state items, causes, transitions, alternatives, and uncertainty. Use this map.","path":"assets/state-record.schema.json"},{"contribution":"Adds fixed human, harm, access, and one-meaning rules. Use this map.","path":"assets/simplicity-contract.json"}],"evals":[{"contribution":"Tests that prompt states are not treated as a closed set. Try this case.","path":"evals/context-cases.json"},{"contribution":"Tests state discovery, alternatives, and full review coverage. Try this case.","path":"evals/evals.json"}],"examples":[{"contribution":"Shows how state context stays attached to the model record. Match this scene.","path":"examples/context-packets.md"},{"contribution":"Shows the open state matrix produced at run start. Match this scene.","path":"examples/run.md"}],"references":[{"contribution":"Defines conflict handling, open options, and the veto order. Read this guide.","path":"references/decisions.md"},{"contribution":"Supplies rich eye, brain, touch, context, and counterexample questions. Read this guide.","path":"references/context-routing.md"}],"scripts":[{"contribution":"Creates the open state matrix and discovery dimensions. Run this tool.","path":"scripts/run_scaffold.py"},{"contribution":"Supplies stable review IDs without choosing state meaning. Run this tool.","path":"scripts/review_checklist.py"},{"contribution":"Supplies the open eye, brain, and touch sweep. Run this tool.","path":"scripts/human_capability_sweep.py"}]}},"exploration_contract":{"choice_owner":"model","constraints_are_vetoes":true,"exploration_axes":["state model","task structure","sequence","disclosure","content","interaction","visual form","motion","sound","touch and haptics","access path","platform fit","service and human effects"],"maximum_options":null,"may_add_directions":true,"may_combine_directions":true,"may_split_directions":true,"method":["Make unlike options before one choice.","A required direction is a starting point, not a box.","Add, split, reverse, or combine directions when the product calls for it.","Give each option a concrete scene, proof, tradeoff, veto check, and test.","Keep a bold option alive until evidence or a veto rejects it.","Choose with stated reasons. The script does not choose."],"minimum_options":4,"option_owner":"model","required_directions":["known pattern","product-shaped form","true reverse","experimental edge"],"required_option_fields":["id","direction","scene","hypothesis","product_fit","evidence","tradeoffs","veto_check","test","novelty"],"script_role":"Require the option fields and veto checks. Never rank or choose."},"forbidden_claims":["unseen pixels","missing sources","causal impact"],"goal":"Find and judge context-derived product states.","human_sweep_command":"python3 scripts/human_capability_sweep.py","inputs":{"audience":"New account owners.","outcome":"Build a clear account setup flow.","platform":"Responsive web.","primary_tasks":["Create an account","Fix input errors"],"proof_threshold":"Each task works in wide and narrow views.","source_permissions":["public_web","local_files"]},"item_id":null,"judgment_context":[{"path":"run.json","use":"Use the frozen goal, people, tasks, rights, proof, and rules."},{"path":"source-queue.json","use":"Use source facts, locations, gaps, and rights."},{"path":"retrieval-manifest.json","use":"Use current source bytes and dates."},{"path":"state-matrix.json","use":"Use found states, context, causes, change, and unknowns."},{"path":"review-checklist.json","use":"Use every eye, brain, touch, objective failure, bad design, bad output, and bad practice prompt."},{"path":"render-plan.json","use":"Use each needed state, view, mode, and motion path."},{"path":"viewport-matrix.json","use":"Use each needed size, crop, zoom, and space."},{"path":"dependency-manifest.json","use":"Use proved low parts and affected high parts."},{"path":"rebuild-queue.json","use":"Use stale links and work that must be rebuilt."}],"output_schema":"assets/state-record.schema.json","pass_rule":"PASS needs all fields and no open veto.","reason_codes":["CLEAR","NEEDS_PROOF","VETO","STALE","OBJECTIVE_FAILURE","HARM_CHECK","CHECK_MEANING"],"required_evidence":["source","location","observation","context","transition","eye","brain","touch","human sweep","objective failure","bad design","bad output","bad practice","reason"],"required_rules":["EYE_FIRST","BRAIN_ONE_STEP","TOUCH_CLEAR","NO_COLOR_ONLY","KEEP_INPUT","MOTION_ALT","WHOLE_SERVICE","SOURCE_IDEA","ADAPT_SPACE","STATE_OPEN","HUMAN_SWEEP","HARM_CHECKS","ONE_CHECK_ONE_MEANING"],"review_checklist":"review-checklist.json","review_checklist_command":"python3 scripts/review_checklist.py","review_owner":"model","run_id":"48843a797566d628","source_locations":[],"version":"1.0.0","vetoes":["safety","access","understanding","agency"]}
```

The listed states are prompts. The model may find overlapping, mixed, brief, or person-specific states.

For each found state, the model records causes, change, proof, options, tradeoffs, vetoes, choice, and doubt.

The source fixture proves only ordered packet mechanics. It does not prove a product source or design choice.
