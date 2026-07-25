"""Rules for the recorded viability judgment of a rendered design system.

Schema validation proves shape. Viability proves the system works on a
page, so the document must record a judgment made by looking at a
screenshot of the rendered preview: which file was rendered, which
screenshot was read, how many revision rounds ran, and a verdict per named
criterion with the observed reason. A missing criterion, an empty reason,
or a criterion that did not pass all fail the document.
"""
from __future__ import annotations

from extraction_schema import is_text

CRITERIA = ("legibility", "contrast", "hierarchy", "font_pairing",
            "spacing_rhythm", "color_harmony", "state_distinction",
            "reference_fidelity")
RECORD_FIELDS = ("rendered_file", "screenshot_file", "iterations", "verdict",
                 "criteria")
MAX_ITERATIONS = 3
PASS_WORD = "pass"
BASE = "meta.viability"


def block_of(document):
    """Return the recorded viability block, or None."""
    meta = document.get("meta")
    found = meta.get("viability") if isinstance(meta, dict) else None
    return found if isinstance(found, dict) else None


def check_shape(block, errors):
    """Require every field of the viability record."""
    for field in RECORD_FIELDS:
        if field not in block:
            errors.append(f"{BASE} missing required field: {field}")
    for field in ("rendered_file", "screenshot_file"):
        if field in block and not is_text(block[field]):
            errors.append(f"{BASE}.{field} must name the file that was produced.")
    rounds = block.get("iterations")
    if "iterations" in block and not isinstance(rounds, int):
        errors.append(f"{BASE}.iterations must be the number of render rounds run.")
    elif isinstance(rounds, int) and not 1 <= rounds <= MAX_ITERATIONS:
        errors.append(f"{BASE}.iterations is {rounds}; the loop runs at least once "
                      f"and stops after {MAX_ITERATIONS}.")


def entries_of(block):
    """Return the recorded criteria entries, keyed by criterion name."""
    found = {}
    for item in block.get("criteria") or []:
        if isinstance(item, dict) and is_text(item.get("criterion")):
            found[item["criterion"].strip()] = item
    return found


def check_entry(name, entry, errors):
    """Require one criterion entry to pass with an observed reason."""
    path = f"{BASE}.criteria.{name}"
    if str(entry.get("verdict", "")).strip().casefold() != PASS_WORD:
        errors.append(f"{path}.verdict is {entry.get('verdict')!r}; every "
                      "criterion must pass before the extraction is reported.")
    if not is_text(entry.get("observed")):
        errors.append(f"{path}.observed must say what you saw in the screenshot.")


def check_criteria(block, errors):
    """Require a passing verdict with a reason for every named criterion."""
    entries = entries_of(block)
    for name in CRITERIA:
        entry = entries.get(name)
        if entry is None:
            errors.append(f"{BASE}.criteria is missing the {name} verdict.")
            continue
        check_entry(name, entry, errors)


def check_viability(document, errors):
    """Run every viability rule and return whether a judgment was recorded."""
    block = block_of(document)
    if block is None:
        errors.append(f"{BASE} must record the judgment of the rendered preview: "
                      "render, screenshot, look, then record a verdict per "
                      "criterion. Schema validation alone does not prove the "
                      "system works.")
        return False
    check_shape(block, errors)
    check_criteria(block, errors)
    return True


def verdict_of(document):
    """Return the recorded overall verdict, or an empty string."""
    block = block_of(document) or {}
    return str(block.get("verdict", "")).strip().casefold()
