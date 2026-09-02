#!/usr/bin/env python3
"""Build the deterministic eye, brain, and touch review checklist."""
import argparse
import json

from human_capability_sweep import HUMAN_CAPABILITY_SWEEP

ANSWER_FIELDS = ["scene", "observation", "evidence", "decision", "reason", "alternatives", "uncertainty"]
REVIEW_DECISIONS = {"PASS", "REVISE", "BLOCKED", "NOT_APPLICABLE"}
QUALITY_GATE_CONTRACT = {
    "owner": "model",
    "gate_ids": [
        "truth", "access", "task", "perception", "familiarity",
        "standards", "uniqueness", "craft", "resilience",
    ],
    "checkpoints": ["direction", "artifact", "integrated"],
    "statuses": ["PASS", "REVISE", "BLOCKED"],
    "diagnoses": ["DEFECT", "MEDIOCRE", "SLOP", "PASS"],
    "noncompensating": True,
    "numeric_score_allowed": False,
    "scripts_may_judge": False,
    "rule": "Every applicable gate needs current evidence. One failed gate prevents PASS.",
}
SCENE = ("Picture the exact moment supported by the intake and evidence. Name the person's current goal, prior action, setting, device, input mode, and relevant access or time pressure. Describe what appears where, what the person can notice or control, what changes after action, and what the consequence is. Use exact labels, positions, distances, timings, and transitions when the evidence provides them. Do not invent feelings, intent, ability, culture, or bodily response. Separate the visible or measured scene from your inference. Then answer this review: ")
DECISION_RULES = {
    "PASS": "The named proof shows no listed failure in this scene.",
    "REVISE": "The named proof shows a listed failure or a failed veto.",
    "BLOCKED": "A named proof need is missing, old, or not seen.",
    "NOT_APPLICABLE": "The checked event cannot occur here. Proof and a reason are still needed.",
}
FORBIDDEN_REINTERPRETATIONS = [
    "Do not replace this check with taste or a style score.",
    "Do not answer another check ID in its place.",
    "Do not turn a common answer into a fixed product rule.",
    "Do not treat a filled field as proof that the answer is right.",
]


def item(row):
    item_id, prompt, probes, needs, failures = row
    probe_list = probes.split("|")
    need_list, failure_list = needs.split("|"), failures.split("|")
    meaning = {
        "one_question": prompt,
        "scope": "Answer this one question for the named scene. Do not answer a nearby check.",
        "probe_order": "probes",
        "evidence_boundary": "evidence_needs",
        "failure_meaning": "failure_signals",
        "decision_rules": "decision_rules",
        "forbidden_reinterpretations": "forbidden_reinterpretations",
    }
    return {"id": item_id, "prompt": prompt,
            "human_lenses": ["eye", "brain", "touch"],
            "apply_human_sweep": "ALL",
            "scene_prompt": prompt + " Use these probes. " +
            "; ".join(probe_list) + ".",
            "probes": probe_list, "evidence_needs": need_list,
            "failure_signals": failure_list, "semantic_contract": meaning}


def objective_item(row):
    value = item(row)
    value["proof_rule"] = "PASS needs a direct render and an input check. A claim without both is BLOCKED."
    return value


EYE = [
    ("eye-first", "Judge what draws sight first and whether that lead matches the person's current goal and risk.", "name the first three noticed elements. |compare intended and seen priority. |check whether risk or status is missed", "whole-view render. |first-attention observation", "decoration leads the view. |the main state or action is found late"),
    ("eye-order", "Judge whether visual order supports a clear scan from current state to needed facts and next action.", "trace the scan path. |check heading and action order. |compare order across sizes and reading directions", "annotated whole view. |wide and narrow renders where applicable", "the eye loops without progress. |layout order conflicts with task order"),
    ("eye-group", "Judge whether proximity, boundaries, alignment, and repeated form group related things without false ties.", "name each perceived group. |check separation between unlike actions. |check whether repeated forms imply the same meaning", "close render. |group and boundary observations", "unrelated items look joined. |one task is split across distant groups"),
    ("eye-state", "Judge whether the present state, recent change, progress, and result are visible without relying on color alone.", "compare before and after. |check added, changed, and removed content. |check focus and status cues", "transition views. |status and focus evidence", "change is easy to miss. |status exists only as color or motion"),
    ("eye-reading", "Judge legibility and reading flow for real words, numbers, labels, and dense content.", "check type size and line length. |check labels near their controls. |check numbers, units, and truncation", "close text render. |content-range samples", "key text is clipped or faint. |reading order breaks meaning"),
    ("eye-color", "Judge contrast, color meaning, image treatment, and visibility under changed display conditions.", "check text and control contrast. |remove color as a cue. |check dark, bright, dim, and forced-color conditions where applicable", "contrast evidence. |non-color cue evidence", "meaning disappears without color. |state boundaries vanish in a changed display mode"),
    ("eye-focus", "Judge focus, selection, hover, pointer, and attention cues for each supported input mode.", "follow focus order. |compare focus and selection. |check off-screen or obscured focus", "focus-path evidence. |input-mode views", "focus is not visible. |focus moves without a clear cause"),
    ("eye-range", "Judge whether meaning and control survive every needed size, crop, zoom, orientation, and spatial distance.", "compare whole and close views. |check wide and narrow forms. |check zoom, resize, fold, crop, or distance where applicable", "view matrix. |changed-size renders", "content hides or overlaps. |the main task moves out of view"),
    ("eye-motion", "Judge whether motion and spatial change explain cause, continuity, direction, depth, and result without discomfort.", "trace source and destination. |check reduced-motion behavior. |check peripheral and repeated motion", "motion capture or timed frames. |reduced-motion view", "motion hides the result. |movement distracts, delays, or causes discomfort"),
    ("eye-content", "Judge the state with short, long, missing, local, user-made, and unexpected content where those cases can occur.", "replace sample copy with content bounds. |check local reading direction and text growth. |check images, icons, and non-text alternatives", "content-range renders. |locale or alternative-content evidence", "layout works only for sample content. |meaning depends on an unexplained image or icon"),
]
BRAIN = [
    ("brain-current", "Judge whether a person can tell what happened, what is true now, and why the state appeared.", "state the current condition in plain words. |link it to the prior event. |check whether system and user causes are confused", "state copy. |event and transition evidence", "the state has no clear cause. |the person may blame the wrong action"),
    ("brain-next", "Judge whether the next safe action, its expected result, and other valid paths are clear.", "name the likely first action. |predict the result from the label. |find escape, defer, and help paths", "action labels. |interaction result evidence", "several actions look primary. |the action result is a surprise"),
    ("brain-model", "Judge whether system behavior fits a learnable cause-and-effect model across states and repeated use.", "compare the same action across contexts. |check object and action consistency. |check whether hidden rules change outcomes", "cross-state comparison. |repeated-task evidence", "the same cue has different effects. |a hidden rule controls the result"),
    ("brain-memory", "Judge recognition, recall, history, and return-to-task needs without making people remember avoidable details.", "list facts carried from another view. |check whether prior work and choices remain visible. |check resume after interruption", "task-flow views. |interruption and return evidence", "a code, term, or choice must be remembered. |returning users lose place or prior work"),
    ("brain-choice", "Judge choice count, comparison effort, defaults, and progressive disclosure for the current task and skill level.", "separate needed from optional choices. |check default meaning and undo. |compare first use and repeat use", "choice inventory. |first-use and repeat-use evidence", "optional detail blocks the task. |a default hides a cost or needed choice"),
    ("brain-language", "Judge whether terms, instructions, errors, numbers, and labels are direct, local, and consistent.", "replace internal terms with user terms. |check one term per concept. |check reading level, units, date, and number forms", "full plain read. |locale and terminology evidence", "one idea has several names. |an error says what failed but not how to fix it"),
    ("brain-feedback", "Judge whether feedback is timely, proportional, tied to the action, and clear about progress or completion.", "time action to response. |separate wait, progress, success, and failure. |check whether feedback interrupts more than needed", "timed interaction evidence. |status message evidence", "silence looks like failure. |feedback is late, noisy, or detached from the action"),
    ("brain-risk", "Judge whether cost, risk, permission, privacy, reversibility, and responsibility are clear before commitment.", "name what changes and for whom. |check cost and data use. |check confirm, cancel, undo, and receipt", "decision-state render. |risk and policy source", "harm is hidden until after action. |the safe exit is weaker or unclear"),
    ("brain-context", "Judge fit for the person's goal, knowledge, access needs, time pressure, setting, culture, and social condition.", "change one context factor at a time. |compare novice and repeat use. |check public, private, noisy, mobile, and interrupted settings where relevant", "context record. |task observation or source evidence", "the design assumes one skill level. |the setting makes a private or timed action unsafe"),
    ("brain-unknown", "Judge ambiguity, mixed states, partial truth, stale data, and unknown system conditions without false certainty.", "name what is known and unknown. |check partial and stale data. |check conflicting signals and concurrent events", "unknown-state evidence. |data freshness or conflict evidence", "the interface claims certainty it lacks. |mixed states are collapsed into a false binary"),
]
TOUCH = [
    ("touch-target", "Judge target size, active area, precision, and tolerance for the current device and motor context.", "measure active bounds. |check small icons and edge targets. |try low-precision and one-handed input where relevant", "target measurements. |device and input context", "the visible and active areas differ. |a common action needs fine precision"),
    ("touch-spacing", "Judge spacing, competing targets, destructive adjacency, and accidental activation risk.", "map nearest targets. |compare safe and destructive actions. |check crowded and changed-size views", "spacing measurements. |error-risk observation", "adjacent actions are easy to confuse. |resize makes hit areas overlap"),
    ("touch-reach", "Judge reach, posture, hand use, device hold, spatial distance, and body comfort for the task.", "trace repeated reach. |check one-hand and alternate-hand use. |check seated, standing, wearable, controller, or spatial posture where relevant", "reach map. |body and device context", "frequent action needs a hard reach. |the task assumes one posture or hand"),
    ("touch-input", "Judge every supported input mode, switch between modes, and an access path that does not depend on touch.", "list touch, pointer, keyboard, voice, switch, controller, stylus, gaze, or gesture as applicable. |change modes mid-task. |check focus and labels for assistive input", "input inventory. |mode-specific interaction evidence", "one mode cannot finish the task. |mode switching loses state or focus"),
    ("touch-affordance", "Judge whether each control suggests how to act, its current value, and whether it is available.", "identify controls without instructions. |compare enabled, disabled, selected, pressed, and dragged forms. |check custom gestures and hidden hit areas", "control-state views. |interaction observation", "non-controls look active. |a control has no visible state or use cue"),
    ("touch-response", "Judge visual, tactile, audio, and state response at contact, during work, and at completion.", "check immediate contact response. |check delay and repeated activation. |compare feedback modes and user settings", "timed input capture. |multimodal feedback evidence", "input has no immediate response. |feedback occurs but does not reveal the result"),
    ("touch-gesture", "Judge gesture discoverability, alternatives, conflict with system gestures, and safe cancellation.", "list every non-basic gesture. |find a visible alternative. |check edge, drag, hold, multi-finger, and spatial gesture conflicts", "gesture inventory. |alternative-control evidence", "a key action exists only as a hidden gesture. |the gesture cannot be canceled or reversed"),
    ("touch-repair", "Judge prevention, validation, cancel, undo, retry, and preservation of safe work after an error.", "cause likely input errors. |check where the error appears. |retry after partial work, timeout, offline use, and changed permission where relevant", "error and repair flow. |preserved-work evidence", "valid work is lost. |retry repeats harm or hides the cause"),
    ("touch-settings", "Judge motor, sensory, motion, haptic, timing, and assistive settings that can change interaction.", "apply larger text and reduced motion. |change haptic, sound, contrast, and hold timing where supported. |check assistive control and target settings", "settings matrix. |changed-setting interaction evidence", "a setting removes the only cue. |the control ignores a system access preference"),
    ("touch-effort", "Judge repeated effort, fatigue, dwell, hold time, path length, and task frequency over real use.", "count actions and repeated movement. |check long press, drag, dwell, and time limits. |compare first use, frequent use, and long sessions", "action count or path trace. |frequency and duration context", "repeat use causes avoidable strain. |a time or hold demand blocks slower input"),
]
OBJECTIVE_FAILURES = [
    ("objective-text-overlap", "Find any text collision that hides, mixes, or blocks words in a needed view.", "inspect every text edge at needed sizes. |zoom each collision. |check reading order and any covered target", "whole and close renders. |size and input checks", "two text blocks cover needed words. |a label becomes hard to read or use"),
    ("objective-image-overlap", "Find any image collision that hides required content, meaning, state, or control.", "inspect image edges and layers. |compare intended depth with the render. |try every control near the overlap", "layer view. |whole and close renders", "one image hides another needed image. |an image covers content or a control"),
    ("objective-clipped-meaning", "Find text, images, icons, values, or focus cues cut before their needed meaning is clear.", "check every edge and crop. |use longest real content. |zoom, resize, rotate, and change text size", "content range. |changed view renders", "a key word or value is cut. |a crop removes the subject or cue"),
    ("objective-covered-control", "Find any control covered by content, chrome, a layer, a keyboard, or another control.", "open each layer and input panel. |try the full active area. |check focus, pointer, and alternate input", "layer states. |input test", "a visible control cannot be used. |an unseen layer takes the input"),
    ("objective-off-view", "Find required content or actions placed outside the view with no clear way to reach them.", "check each needed size. |follow all scroll paths. |use zoom, large text, and orientation changes", "whole view matrix. |scroll and focus trace", "a needed action is off canvas. |scroll or focus cannot reach it"),
    ("objective-target-collision", "Find active areas that overlap or send one input to the wrong action.", "map active bounds. |try the shared edge. |check pointer, touch, keyboard, switch, and gaze where supported", "target map. |input event trace", "one point triggers two actions. |the shown and active targets do not match"),
    ("objective-focus-trap", "Find any focus path that gets lost, trapped, hidden, or blocked from a needed task.", "enter and leave each region. |follow focus in both ways. |open and close every layer", "focus trace. |layer and input states", "focus cannot leave a region. |focus moves behind a visible layer"),
    ("objective-cue-loss", "Find a needed fact or state that vanishes when one sense, cue, or setting changes.", "remove color, sound, motion, and haptics in turn. |change contrast and text size. |use an alternate input path", "changed setting views. |access path check", "one lost cue removes meaning. |a setting removes the only response"),
    ("objective-state-conflict", "Find two visible or spoken cues that claim different current states or action results.", "read all status cues together. |compare label, control, data, and message. |check stale and concurrent events", "state capture. |event and data trace", "success and failure show together without meaning. |a label conflicts with the real value"),
    ("objective-task-dead-end", "Find any reachable point where the task cannot continue, stop, repair, return, or get help.", "enter each branch. |remove network, rights, data, or time. |try cancel, back, retry, undo, and help", "full task trace. |failure and repair states", "no safe action remains. |the only action repeats the same failure"),
]
BAD_DESIGN = [
    ("bad-design-hidden-state", "Check whether the design hides a key state, cost, rule, risk, or control.", "name what is hard to see. |trace who gains from that gap. |show when the fact becomes clear", "decision view. |state, cost, or policy proof", "a key fact appears after commitment. |a safe control is hard to find"),
    ("bad-design-false-priority", "Check whether style, growth, or noise leads the eye before the real task or risk.", "name the first three seen things. |compare seen and needed order. |remove the loudest style cue", "whole view. |first-sight notes", "decoration leads the task. |a sale cue outranks a warning"),
    ("bad-design-misleading-control", "Check whether a control looks, reads, or acts unlike its true use.", "predict the result before use. |compare label, form, and result. |check enabled and disabled states", "control states. |action result", "a control gives a surprise. |a non-control looks active"),
    ("bad-design-no-feedback", "Check whether any action, wait, change, success, or failure can seem silent or unclear.", "act once and wait. |trace contact, progress, and result. |check every supported sense and input", "timed task capture. |status evidence", "silence looks like failure. |feedback does not name the result"),
    ("bad-design-lost-work", "Check whether error, timeout, exit, conflict, or repair can erase safe work.", "cause each likely break. |return after the break. |check saved, stale, and partial work", "repair flow. |before and after data", "valid input is lost. |retry can repeat harm"),
    ("bad-design-inaccessible-core", "Check whether a key task depends on one sense, one motion, one input, or one body setup.", "list each path to finish. |change access and device settings. |try a path without touch or sight", "access path matrix. |changed setting proof", "one person cannot finish. |one cue carries all meaning"),
    ("bad-design-danger-close", "Check whether risky and safe actions are too close, too alike, or hard to undo.", "map nearby targets. |compare risk labels and weight. |test cancel, confirm, undo, and receipt", "risk view. |repair evidence", "a slip can cause harm. |the safe exit is weaker"),
    ("bad-design-fixed-context", "Check whether the design assumes one person, device, place, pace, language, or data state.", "change one context fact at a time. |compare first and repeat use. |check mixed and unknown states", "context matrix. |changed state views", "the task fails outside one setup. |the design claims false certainty"),
    ("bad-design-fragmented-system", "Check whether one-off parts or rules make the product hard to learn, change, or trust.", "trace each part to its owner. |compare same actions across views. |find style added only for one screen", "part lineage. |cross-view comparison", "the same cue acts differently. |a screen invents a new rule"),
    ("bad-design-shifted-burden", "Check whether a calm view moves time, work, cost, risk, or care to someone else.", "name every affected person. |trace work before and after the screen. |check service and support effects", "service map. |affected-person evidence", "one person gains by hiding another's work. |cost leaves the visible frame"),
]
BAD_OUTPUT = [
    ("bad-output-ungrounded-claim", "Check whether any result claims more quality, access, use, value, or impact than its proof shows.", "match each claim to proof. |name the proved layer. |remove causal words without causal proof", "claim list. |current evidence", "a code pass claims good design. |a mock claims real use"),
    ("bad-output-unseen-pass", "Check whether any visual, motion, touch, or state claim passed without direct review.", "list every needed view. |match each view to a current capture. |name tool or sight gaps", "view matrix. |review records", "unseen pixels pass. |motion passes from still frames"),
    ("bad-output-missing-state", "Check whether the output omits a state that current context, events, data, or risk can create.", "replay the task with changed facts. |trace all known transitions. |look for mixed and short states", "state matrix. |event evidence", "only the happy path exists. |a repair state has no response"),
    ("bad-output-fixed-state-set", "Check whether prompts became a closed state list that blocks new evidence.", "find language that claims the set is complete. |add one context change. |test nested and concurrent states", "state record. |context change", "common labels act as an enum. |unknown states are forced into old names"),
    ("bad-output-incomplete-checklist", "Check whether any required invariant, field, view, option, or owner is absent.", "compare exact ids. |check each required answer field. |check owner and schema", "generated checklist. |saved record", "one id is missing. |a blank field passes"),
    ("bad-output-no-options", "Check whether the output chose too soon or made options that differ only in surface style.", "compare option structure and action. |find a true reverse. |ask what bold path was dropped", "option set. |choice reason", "four skins count as four ideas. |one answer appears before search"),
    ("bad-output-script-judgment", "Check whether a script ranked, chose, scored, or praised a design result.", "trace each decision to its owner. |read script output words. |separate shape checks from judgment", "owner map. |script output", "a score chooses the design. |a filled record becomes a quality pass"),
    ("bad-output-stale-proof", "Check whether a claim rests on old bytes, old rules, old views, or changed parts.", "compare dates and hashes. |trace changed low parts. |reopen linked high views", "source hash. |stale part list", "old proof is called current. |a changed atom leaves screens passed"),
    ("bad-output-broken-lineage", "Check whether any screen fact lacks a proved path through its lower parts and sources.", "trace each visible rule down. |find unused and one-off parts. |check cycles and stale links", "lineage graph. |file manifest", "a screen invents a token. |a high part points to stale proof"),
    ("bad-output-vague-result", "Check whether the result hides exact scenes, evidence, tradeoffs, doubt, or blocked claims behind broad praise.", "replace each broad claim with a scene. |name the source and location. |state what could change the choice", "final report. |model records", "good or clean stands alone. |a blocker is softened into advice"),
]
BAD_PRACTICE = [
    ("bad-practice-style-first", "Check whether work began with a style choice before product meaning, states, tasks, and risk were known.", "trace the first design choice. |find its source meaning. |ask which task fact shaped it", "work log. |source record", "a mood leads without meaning. |style fixes structure late"),
    ("bad-practice-surface-copy", "Check whether a reference was copied by look while its reason, setting, and product fit were ignored.", "name the source idea. |compare source and target context. |show the changed product form", "source ledger. |target rationale", "the target repeats a surface detail. |the source reason is absent"),
    ("bad-practice-screen-first", "Check whether a screen created rules that belong in tokens, atoms, parts, states, or service design.", "trace each new choice down. |find one-off parts. |check the full task outside the frame", "part graph. |screen diff", "the screen owns a low rule. |the frame hides service work"),
    ("bad-practice-premature-choice", "Check whether the model chose before making unlike, viable, and well-tested options.", "count true structural differences. |find a reverse and edge. |check why each option stayed or left", "option record. |choice record", "the favorite appears first and wins. |bold options lack equal detail"),
    ("bad-practice-no-counterevidence", "Check whether review sought only support and ignored facts that could reject the favored choice.", "state the main claim. |seek one disproof path. |name evidence that would reverse the choice", "counterevidence field. |test result", "only praise is logged. |uncertainty has no effect"),
    ("bad-practice-happy-path-only", "Check whether review tested only ideal content, data, access, input, timing, and system health.", "change each context axis. |cause partial and failed work. |return after delay and interruption", "view matrix. |changed-context tasks", "sample content always fits. |repair and unknown states are absent"),
    ("bad-practice-access-late", "Check whether access needs were added after structure, interaction, motion, and content were fixed.", "find when access entered the work. |compare early options. |check whether one path was patched later", "work log. |access review", "access is a final audit. |the main path needs a separate weak copy"),
    ("bad-practice-hidden-cost", "Check whether a design gain hides build, service, support, privacy, or human cost.", "list costs by person and team. |trace data and care work. |compare short and long use", "service evidence. |cost record", "visual calm creates support work. |a metric hides a harmed group"),
    ("bad-practice-metric-overreach", "Check whether a metric, test, score, or proxy replaced the outcome it can only partly show.", "name what the measure proves. |name what it cannot prove. |seek a conflicting human result", "metric contract. |human review", "speed alone means good use. |engagement stands in for value"),
    ("bad-practice-false-polish", "Check whether finish, novelty, or smooth motion masks weak truth, control, repair, or product fit.", "remove polish and replay the task. |inspect hard states first. |compare delight with delay and control", "unpolished task flow. |hard-state render", "shine hides a broken task. |motion delays needed truth"),
]
LENSES = {"eye": [item(row) for row in EYE],
          "brain": [item(row) for row in BRAIN],
          "touch": [item(row) for row in TOUCH]}
NEGATIVE_CHECKS = {"objective_failure": [objective_item(row)
                                         for row in OBJECTIVE_FAILURES],
                   "bad_design": [item(row) for row in BAD_DESIGN],
                   "bad_output": [item(row) for row in BAD_OUTPUT],
                   "bad_practice": [item(row) for row in BAD_PRACTICE]}

REVIEW_CHECKLIST = {
    "version": "1.0.0", "owner": "script", "review_owner": "model",
    "invariant_rule": "Every named item must always be reviewed. Each answer is context-bound and may differ by state.",
    "invariants": {lens: [entry["id"] for entry in items]
                   for lens, items in LENSES.items()},
    "negative_invariant_rule": "Every named harm check must always be checked. It is not a fixed taste rule. Objective failures use direct render and input proof. Other answers use the current scene, proof, and context.",
    "negative_invariants": {group: [entry["id"] for entry in items]
                            for group, items in NEGATIVE_CHECKS.items()},
    "required_answer_fields": ANSWER_FIELDS,
    "scene_prompt_template": SCENE,
    "decision_rules": DECISION_RULES,
    "forbidden_reinterpretations": FORBIDDEN_REINTERPRETATIONS,
    "response_style": ["Write a concrete scene, not a short score or generic design rule.", "Name the person, goal, setting, device, input, prior event, and current state when known.", "Describe exact words, objects, positions, changes, timing, touch, motion, and feedback when seen.", "Use measured values when available and label any estimate.", "Keep direct observation, source fact, inference, and proposed change separate.", "Show the strongest alternative and counterevidence before the decision.", "End with doubt, missing proof, and the event that would change the decision."],
    "method": ["Review one found product state in one real context at a time.", "Use rendered pixels, interaction evidence, source facts, and known limits.", "Keep observation apart from inference and proposed change.", "Check whole use, close detail, transitions, and changed context when they apply.", "Name counterevidence, alternatives, doubt, and missing proof for every item.", "Use NOT_APPLICABLE only with evidence and a reason."],
    "context_fields": ["person", "goal", "task", "prior_action", "data", "system", "setting", "device", "input", "access", "time", "content", "social_setting", "risk"],
    "answer_contract": {"scene": "Give a detailed, evidence-bound account of the person, context, action, change, and consequence.", "observation": "State only what the evidence shows.", "evidence": "Name each source, view, location, event, or interaction used.", "decision": "Use PASS, REVISE, BLOCKED, or NOT_APPLICABLE.", "reason": "Link the evidence to the decision and current context.", "alternatives": "Name at least one other valid response and its tradeoff.", "uncertainty": "Name doubt, missing proof, and what could change the decision."},
    "quality_gate_contract": QUALITY_GATE_CONTRACT,
    "human_capability_sweep": HUMAN_CAPABILITY_SWEEP,
    "lenses": LENSES, "negative_checks": NEGATIVE_CHECKS,
}
REVIEW_INDEX = {
    "version": "1.0.0",
    "owner": "script",
    "review_owner": "model",
    "source_script": "scripts/review_checklist.py",
    "source_command": "python3 scripts/review_checklist.py",
    "human_source_script": "scripts/human_capability_sweep.py",
    "human_source_command": "python3 scripts/human_capability_sweep.py",
    "open_human_set": True,
    "required_answer_fields": ANSWER_FIELDS,
    "decision_rules": DECISION_RULES,
    "invariants": REVIEW_CHECKLIST["invariants"],
    "negative_invariants": REVIEW_CHECKLIST["negative_invariants"],
    "item_count": sum(len(items) for items in LENSES.values()) +
    sum(len(items) for items in NEGATIVE_CHECKS.values()),
    "meaning_lock": "Each ID uses the one question, probe order, proof list, failure signs, and result rules in the source script.",
    "quality_gate_contract": QUALITY_GATE_CONTRACT,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print(json.dumps(REVIEW_CHECKLIST, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
