#!/usr/bin/env python3
"""Print the per-context validation checks for SKILL.md step 3.

Pass one or more context names; the matching checklists print in full. Pass
--list to see the names. An unrecognized name prints the derivation rule for
contexts this file does not carry. Exit 0 on any successful print, 1 on
usage errors.

Usage:
    python3 context_checks.py coding agentic
    python3 context_checks.py --list
"""
import sys

CHECKS = {
    "coding": [
        "Language and version pinned.",
        "Environment and dependencies stated.",
        "Inputs, outputs, or the interface defined.",
        "Error handling and edge cases mentioned.",
        "Testing or acceptance criteria stated.",
        "Anything that must not be touched, named.",
    ],
    "research": [
        "Scope bounded: time range, region, sources.",
        "Depth and length stated.",
        "Source quality or citation expectations stated.",
        "Sources asked for by name, followable by the reader. No unnamed authority.",
        "The question is actually answerable.",
        "Opinion and fact expectations separated.",
    ],
    "writing": [
        "Audience, tone, and register stated.",
        "Length stated.",
        "Format stated: essay, email, post.",
        "Point of view stated.",
        "What to include and what to leave out.",
        "The output asked for checkable particulars, not general praise.",
        "A position asked for, where the format takes one.",
    ],
    "media": [
        "Subject, style, composition, lighting, mood.",
        "Aspect ratio or duration, if the target supports it.",
        "What must not appear, stated.",
    ],
    "agentic": [
        "Goal separated from method.",
        "A stopping condition.",
        "Permissions and side-effect boundaries.",
        "What to do on failure or ambiguity.",
        "A verification step.",
    ],
    "data": [
        "Input shape described.",
        "Output schema exact: fields, types, order.",
        "Handling for missing or malformed records.",
        "Volume expectations.",
    ],
    "system-prompt": [
        "Persona consistent throughout.",
        "Refusal and boundary behavior defined.",
        "No conflicting rules.",
        "Examples of desired exchanges.",
    ],
}

DERIVE = """No checklist carries this context. Derive your own:
Run the universal checks in SKILL.md, then write two or three checks by
asking how this specific task would fail. A translation prompt: register and
dialect. A proof: what may be assumed. A plan: horizon and constraints.
Name the checks you applied in "What changed"."""


def main() -> int:
    names = [a.lower() for a in sys.argv[1:]]
    if not names:
        print("usage: context_checks.py <context>... | --list", file=sys.stderr)
        print("contexts: " + ", ".join(CHECKS), file=sys.stderr)
        return 1
    if names == ["--list"]:
        print("\n".join(CHECKS))
        return 0
    for name in names:
        print(f"[{name}]")
        for item in CHECKS.get(name, []):
            print(f"- {item}")
        if name not in CHECKS:
            print(DERIVE)
        print()
    print("Apply every matching context, usually one, sometimes two for a "
          "prompt that spans them. Name each in \"What changed\".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
