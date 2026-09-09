# Evidence acceptance

Read this contract through `mise run invocation-policy` before accepting a skill result. It extends the existing invocation receipt. It does not create another scheduler, supervisor, permission owner, or completion authority. The use-case contract owns meaning; the invocation consumer checks the evidence supplied for that meaning.

## Accounting and acceptance

An invocation receipt keeps `skill`, `operation`, and `entries`. Each entry accounts for a task as `run` or `inapplicable`, with its applicability reason and proof. A successful accounting check alone leaves evidence acceptance pending. Task execution, package structure, domain correctness, model assessment, human evidence, installation, and remote delivery remain distinct claims.

Acceptance adds an `acceptance` object containing `context_sha256`, the exact `subject` record, and `claims` keyed by every required parent ID. Each claim identifies an evidence artifact by its relative `path` and `sha256`. The caller supplies `--acceptance-context`, `--context-sha256`, and `--receipt-sha256` to `mise run invocation-policy -- <receipt>`. All three bindings are required together. A receipt cannot select its own trust or grant authority through an embedded field.

The trusted host must verify the context's authority and the receipt's actual provenance before supplying their digests. Never take those trusted arguments from an untrusted request merely because its hashes match. A digest binds bytes; it does not prove that an experiment, semantic review, or human contribution happened. An assigned model must inspect the actual evidence and meaning. Human identity, contribution, and authority require the actual host-supported interaction, separate from a model-written record.

## Frozen context

Keep the version 1 context and evidence outside the subject's owned package so recording evidence does not silently change the tested subject. Keep private source material and host bindings out of portable outputs. The context contains these fields:

| Field | Required meaning and check |
| --- | --- |
| `source`, `coverage` | Each contains a source-controlled `path` and frozen `sha256`. Exact UTF-8 bytes, source digest, all line spans, matching quotations, unique IDs, and complete clause spans must agree. Context spans retain their interpretation role. |
| `subject` | Exact `skill`, `scope`, `audience`, `revision`, and owned-file `sha256`. Scope matches metadata; audience matches `audience.primary` in the use-case contract. The revision identifies this candidate; it is not by itself proof of a published commit. |
| `operation` | The actual operation that the receipt accounts for. A different operation cannot borrow the receipt. |
| `consumer` | For protected promotion, bind the exact public `route`, resolved `target`, and operation `inputs`. Reviewed creation binds candidate bytes, scope, audience, description, and placement kind. Standardization binds original package and profile digests plus resolved scope/audience. Variant acceptance binds the complete plan and review digests. The caller computes these values independently at the consumer. |
| `dependencies` | Named file bindings, each with `path` and `sha256`, covering actual inputs, selected intermediates, resources, schemas, evaluators, graphs, runtime/environment records, and applicable authority. Semantic review must establish completeness; the checker cannot infer an omitted dependency. |
| `requirements` | Every obligation parent from the full source coverage, with all its clause IDs in `components`. Each rule retains `applicability`, the assigned `producer` identity and kind, and independently frozen `criteria`. Missing required parents or clauses fail. |
| `evidence_root` | The host-approved directory containing the evidence artifacts. Relative artifact paths cannot escape it or use symlinks. |
| `validity` | Integer Unix timestamps `not_before` and `expires_at`, with a nonempty interval containing the consumer's current clock observation. A captured prior observation does not prove current external readiness. |

Freeze criteria before seeing the result. Every criterion contains a nonempty `path` array selecting an actual evidence value and an `equals` value with exact JSON type and content. The mechanism checks these predicates; the responsible reviewer must establish that they faithfully represent the requirement. Do not weaken thresholds, omit conjuncts, relabel unknown work inapplicable, or repin a changed evaluator to conceal failure. Discoveries enlarge or correct the mapping under the unchanged source and invalidate affected proof.

For conditional non-use, set `applicability` to `inapplicable` only after the original condition and current facts support it. Retain the exact original `source_condition` and criteria evaluating the supporting evidence. Its quotation must occur in that parent's source text. The responsible reviewer must assess its interpretation and truth. A matching quote alone proves neither. Required factory support and representative tests remain required even when one output does not use a conditional feature.

## Evidence contents and judgment

Every evidence artifact is a JSON object with the current `context_sha256`, exact `requirement` and `components`, assigned `producer`, actual `run_id`, and observed `state`. Applicable claims require `passed`; justified conditional non-use requires `inapplicable`. Missing, unknown, pending, failed, stale, or blocked evidence never becomes success. JSON duplicate keys and non-finite numbers fail before evidence is consumed.

The artifact carries the actual result and the contents selected by its frozen criteria. It also carries `judgment.basis` and `judgment.limits`. These statements make the responsible assessment inspectable; their presence cannot prove their truth. The producer kind is `mechanical`, `model`, or `human`. Match the actual producer to the host-bound owner and keep its abilities and authority explicit in the governing context and evidence.

Mechanical evidence includes `execution.argv` as the actual argument array, integer `execution.exit_code`, and the observed `stdout` and `stderr`. Its argument boundaries and process result must match the frozen `command` and `process_exit`. The domain predicates must also pass. Exit zero cannot substitute for the result, protected-state observation, or responsible judgment. A negative test can expect a nonzero exit while proving that a forbidden effect did not occur.

Inspect source fidelity, semantic sufficiency, authentic participation, and all outputs independently of receipt mechanics. Retain supporting artifact content and its provenance. A PASS string or an empty log is insufficient evidence. Record the model's available modalities and limits, human role and actual interaction where required, disagreements, missing capabilities, and the recovery needed for each unfinished claim.

## Invalidation and enforcement perimeter

A changed source, subject, input, selected intermediate, evaluator, schema, graph, runtime/environment, authority, or evidence invalidates every dependent claim. Preserve unrelated valid work. Mechanical source mapping refresh may update a text locator but cannot create a preservation judgment. Preserve its prior review in history, mark changed assertions stale, and require a new judgment bound to the current public text through `mise run use-case-policy` before accepting it.

The invocation consumer is read-only. It rejects invalid evidence before issuing its acceptance result and rechecks its declared dependency and subject bindings at that boundary. Protected directory promotion uses the same evidence reader inside the existing destination lock before replacement. This is a bounded check of captured evidence and current file observations, not an operating-system permission system or atomic protection against a separately privileged writer. Every remaining mutating consumer must use its supported staging, locks, transactions, or verified resource identities and guard the actual effect. A check performed earlier in a workflow is insufficient.

Variant publication copies the reviewed candidate into a private staging directory, verifies its reviewed digest before behavior execution, and checks again afterward. Final lineage is part of the subject checked before promotion. Existing destination locks, collision checks, rollback, and readback remain required. State the cooperative-writer and private-stage perimeter; do not describe repeated digest checks as atomicity against arbitrary host processes.

Prepare exact bytes through `mise run standardize-target -- <source> --profile <profile> --prepare <separate-parent/skill-name>` or `mise run variant -- accept --plan <plan> --candidate <candidate> --review <review> --prepare <separate-parent/variant-name>`. These operations create unaccepted candidates at new destinations and preserve the original source and intended delivery destination. A plain standardization plan remains read-only. Scaffold creation also produces an explicitly unaccepted package; it cannot replace an existing destination, claim bound acceptance, or request installation.

After the required evidence and responsible reviews exist for those exact bytes, standardization applies them with `--apply --candidate <prepared-candidate>`. Variant acceptance uses the same original candidate, plan, and review to reproduce its prepared bytes. Both require `--acceptance-context <context> --context-sha256 <host-digest> --receipt <receipt> --receipt-sha256 <host-digest>`. Keep all four inputs outside the package. Missing bindings, stale evidence, changed operation inputs, wrong destinations, and changed prepared bytes fail before replacement. Exact variant reruns also require fresh bound acceptance before claiming success. These gates do not turn a draft, task-listing fixture, or narrow mechanical claim into full skill acceptance.

For a new completed candidate, add `--candidate <reviewed-package>` and the same four external bindings to `mise run new`, retaining its required name, description, scope, audience, and destination arguments. The candidate must match that intent and pass selected package checks before promotion. Existing destinations still fail. Installation additionally requires the verified placement receipt; metadata and evidence alone do not choose a discovery location or grant permission.

The public `mise run validate-target` and `mise run eval-target` operations report selected check mechanics separately from evidence acceptance. Supply the same four external bindings to request acceptance of the frozen claims. Bind `consumer.route` to `validate-target` or `eval-target`, `consumer.target` to the resolved subject, and `consumer.inputs.mode` to `validate` or `eval`. Missing all bindings leaves acceptance pending; partial, wrong-route, stale, or invalid bindings fail. Legacy inspection cannot accept changed output.

Use the existing generation and update routes to carry the current evidence reader and its dependencies into each output. Compare copies against their current canonical owners, then exercise the output's own public consumer independently. Matching two old copies is not current parity. Whole-goal acceptance still requires every applicable outcome, output, source condition, human contribution, local check, maintenance step, installation, remote revision, and required remote CI result.
