#!/usr/bin/env python3
"""Name the human factors that every review check must test."""
import argparse
import json

EYE = [
    {"id": "eye-no-sight", "prompt": "Check the path when sight gives no useful input."},
    {"id": "eye-low-detail", "prompt": "Check small detail, blur, and low sharpness."},
    {"id": "eye-contrast", "prompt": "Check low contrast and weak edge change."},
    {"id": "eye-color", "prompt": "Check changed color sense and no color cue."},
    {"id": "eye-light", "prompt": "Check bright sun, dim rooms, and mixed light."},
    {"id": "eye-glare", "prompt": "Check glare, shine, haze, and screen marks."},
    {"id": "eye-field", "prompt": "Check narrow, missing, and uneven fields of view."},
    {"id": "eye-center-edge", "prompt": "Check center and edge sight on their own."},
    {"id": "eye-one-two", "prompt": "Check one-eye and two-eye depth cues."},
    {"id": "eye-depth", "prompt": "Check flat, layered, near, and far space."},
    {"id": "eye-motion-seen", "prompt": "Check slow, fast, slight, and missed motion."},
    {"id": "eye-motion-harm", "prompt": "Check motion strain, sickness, and fear."},
    {"id": "eye-flash", "prompt": "Check flash, flicker, pulse, and quick light change."},
    {"id": "eye-crowding", "prompt": "Check dense marks, clutter, and visual crowding."},
    {"id": "eye-focus-shift", "prompt": "Check near, far, and quick focus shifts."},
    {"id": "eye-track", "prompt": "Check moving focus and hard eye tracking."},
    {"id": "eye-scan", "prompt": "Check scan paths, missed zones, and repeat scans."},
    {"id": "eye-gaze", "prompt": "Check gaze aim, drift, dwell, and rest."},
    {"id": "eye-fatigue", "prompt": "Check tired eyes and long use."},
    {"id": "eye-zoom", "prompt": "Check zoom, large text, and close crop."},
    {"id": "eye-distance", "prompt": "Check hand, desk, room, and far viewing."},
    {"id": "eye-display", "prompt": "Check small, dim, cracked, and low-grade displays."},
    {"id": "eye-angle", "prompt": "Check tilt, side view, posture, and head motion."},
    {"id": "eye-read-order", "prompt": "Check each supported script and reading order."},
    {"id": "eye-symbol", "prompt": "Check words, icons, signs, charts, and images."},
    {"id": "eye-content", "prompt": "Check short, long, blank, local, and made content."},
    {"id": "eye-change", "prompt": "Check added, moved, changed, and lost content."},
    {"id": "eye-device", "prompt": "Check screen, print, glass, space, and no screen."},
]

BRAIN = [
    {"id": "brain-attention", "prompt": "Check narrow, broad, lost, and split attention."},
    {"id": "brain-distraction", "prompt": "Check noise, alerts, people, and task breaks."},
    {"id": "brain-working-memory", "prompt": "Check how much must stay in mind at once."},
    {"id": "brain-recall", "prompt": "Check facts recalled from past steps or use."},
    {"id": "brain-recognition", "prompt": "Check whether people can know a thing when seen."},
    {"id": "brain-learning", "prompt": "Check first use, guided use, and learned use."},
    {"id": "brain-prior-skill", "prompt": "Check no skill, mixed skill, and deep skill."},
    {"id": "brain-model", "prompt": "Check the cause and effect people may learn."},
    {"id": "brain-language", "prompt": "Check plain words, local terms, and weak language skill."},
    {"id": "brain-reading", "prompt": "Check low reading skill and slow reading."},
    {"id": "brain-number", "prompt": "Check count, size, time, money, rate, and chance."},
    {"id": "brain-space", "prompt": "Check maps, layers, depth, order, and place."},
    {"id": "brain-sequence", "prompt": "Check steps, branches, repeats, and return paths."},
    {"id": "brain-time", "prompt": "Check wait, speed, deadline, and unclear time."},
    {"id": "brain-choice", "prompt": "Check choice count, compare work, and defaults."},
    {"id": "brain-control", "prompt": "Check impulse, pause, consent, and safe stop."},
    {"id": "brain-error-seen", "prompt": "Check whether a person can spot the error."},
    {"id": "brain-repair", "prompt": "Check how a person can fix and resume work."},
    {"id": "brain-problem", "prompt": "Check new, rare, and hard problems."},
    {"id": "brain-unknown", "prompt": "Check doubt, mixed truth, stale facts, and conflict."},
    {"id": "brain-stress", "prompt": "Check stress, fear, pressure, and high stakes."},
    {"id": "brain-mood", "prompt": "Check grief, anger, joy, shame, and calm."},
    {"id": "brain-fatigue", "prompt": "Check tired, sick, drugged, and sleepless use."},
    {"id": "brain-interrupt", "prompt": "Check pause, leave, return, and lost place."},
    {"id": "brain-change", "prompt": "Check age, injury, illness, and changing skill."},
    {"id": "brain-thinking-style", "prompt": "Check varied focus, sense, memory, and thought."},
    {"id": "brain-culture", "prompt": "Check local norms, symbols, names, and roles."},
    {"id": "brain-trust", "prompt": "Check trust, doubt, fraud risk, and source truth."},
    {"id": "brain-risk", "prompt": "Check harm, cost, chance, duty, and who bears them."},
    {"id": "brain-agency", "prompt": "Check choice, consent, privacy, undo, and escape."},
    {"id": "brain-social", "prompt": "Check solo, shared, watched, public, and care use."},
]

TOUCH = [
    {"id": "touch-no-touch", "prompt": "Check the full task with no direct touch."},
    {"id": "touch-precision", "prompt": "Check low aim, drift, and edge hits."},
    {"id": "touch-tremor", "prompt": "Check shake, repeat taps, and stray motion."},
    {"id": "touch-dexterity", "prompt": "Check limited finger and hand control."},
    {"id": "touch-strength", "prompt": "Check low force, weak grip, and light contact."},
    {"id": "touch-reach", "prompt": "Check short reach and hard screen edges."},
    {"id": "touch-range", "prompt": "Check limited joint and body motion."},
    {"id": "touch-one-hand", "prompt": "Check either hand and one-hand use."},
    {"id": "touch-limb", "prompt": "Check limb loss, difference, and changed use."},
    {"id": "touch-pain", "prompt": "Check pain, strain, and guarded motion."},
    {"id": "touch-fatigue", "prompt": "Check weak, tired, and long use."},
    {"id": "touch-speed", "prompt": "Check slow starts, slow motion, and slow release."},
    {"id": "touch-repeat", "prompt": "Check repeated taps, holds, drags, and reach."},
    {"id": "touch-slip", "prompt": "Check stray contact and wrong target hits."},
    {"id": "touch-cover", "prompt": "Check fingers, hands, tools, and body hiding the view."},
    {"id": "touch-glove", "prompt": "Check gloves, wet skin, dry skin, and cold."},
    {"id": "touch-posture", "prompt": "Check seated, stood, held, worn, and fixed use."},
    {"id": "touch-size", "prompt": "Check small, near, edge, and packed targets."},
    {"id": "touch-haptic", "prompt": "Check strong, weak, absent, and unwanted haptics."},
    {"id": "touch-time", "prompt": "Check tap, hold, dwell, delay, and time limits."},
    {"id": "touch-pointer", "prompt": "Check mouse, pad, pen, stylus, and remote."},
    {"id": "touch-keyboard", "prompt": "Check keys, switch, controller, and short cuts."},
    {"id": "touch-voice", "prompt": "Check voice, breath, sound, and no speech."},
    {"id": "touch-gaze", "prompt": "Check gaze, head, face, and space input."},
    {"id": "touch-mode-change", "prompt": "Check a change of input during the task."},
    {"id": "touch-cancel", "prompt": "Check safe start, pause, cancel, undo, and retry."},
    {"id": "touch-response", "prompt": "Check seen, heard, felt, and stated response."},
    {"id": "touch-aid", "prompt": "Check each supported access tool and setting."},
    {"id": "touch-shake", "prompt": "Check travel, bumps, shake, and moving use."},
    {"id": "touch-social", "prompt": "Check private, public, shared, and watched action."},
]

HUMAN_CAPABILITY_SWEEP = {
    "version": "1.0.0",
    "open_world": True,
    "exhaustive": False,
    "per_check_rule": "Apply every named eye, brain, and touch factor to every check. Add any factor found in current proof.",
    "extension_rule": "The catalog is a required floor. It never closes the human set.",
    "lenses": {"eye": EYE, "brain": BRAIN, "touch": TOUCH},
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print(json.dumps(HUMAN_CAPABILITY_SWEEP, sort_keys=True,
                     separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
