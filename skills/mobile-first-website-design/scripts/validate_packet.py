#!/usr/bin/env python3
"""Validate a deterministic mobile-first website design packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import breakpoint_rules
import prompt_corpus

FORBIDDEN_STYLE = (
    "color",
    "font",
    "typeface",
    "gradient",
    "shadow",
    "texture",
    "decorative",
    "palette",
    "animation",
)
GOOD_MAX = {"LCP": 2.5, "INP": 200, "CLS": 0.1, "FCP": 1.8, "TTFB": 0.8}
ALLOWED_STATUSES = {
    "PASS",
    "UNAVAILABLE_AUTH",
    "UNAVAILABLE_TRANSPORT",
    "UNAVAILABLE_SCHEMA",
    "UNAVAILABLE_SKILL",
    "UNAVAILABLE_DISABLED",
    "NO_MATCH",
}


def canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def contains_style(value: object) -> bool:
    text = canonical(value).decode().lower()
    return any(token in text for token in FORBIDDEN_STYLE)


def check_breakpoints(packet: dict, errors: set[str]) -> list[int]:
    try:
        return breakpoint_rules.validate(packet)
    except ValueError as exc:
        errors.add(str(exc))
        return []


def check_integrations(packet: dict, errors: set[str]) -> None:
    rows = packet.get("integrations", [])
    if any(row.get("status") not in ALLOWED_STATUSES for row in rows):
        errors.add("BLOCKED_CAPABILITY_FLOOR")
    for row in rows:
        if row.get("status") != "PASS" and not row.get("fallback_ran"):
            errors.add("BLOCKED_CAPABILITY_FLOOR")
    if any(section.get("evidence_count", 0) < 1 for section in packet.get("sections", [])):
        errors.add("BLOCKED_CAPABILITY_FLOOR")


def check_visual(packet: dict, widths: list[int], errors: set[str]) -> None:
    evidence = packet.get("visual_evidence", {})
    if any(not evidence.get(str(width)) for width in widths):
        errors.add("BLOCKED_CAPABILITY_FLOOR")


def check_performance(packet: dict, widths: list[int], errors: set[str]) -> None:
    rows = packet.get("performance", {})
    for width in widths:
        metrics = rows.get(str(width), {})
        if any(type(metrics.get(name)) not in (int, float) or metrics[name] > limit for name, limit in GOOD_MAX.items()):
            errors.add("BLOCKED_PERFORMANCE")


def prompt_index() -> dict[str, dict]:
    index = prompt_corpus.load_index()
    return {row["path"]: row for row in index["prompts"]}


def check_images(packet: dict, errors: set[str]) -> None:
    rows = prompt_index()
    for job in packet.get("image_jobs", []):
        source = rows.get(job.get("prompt_path"))
        if source is None or source["sha256"] != job.get("prompt_sha256"):
            errors.add("BLOCKED_PROMPT_HASH")


def check_flora(packet: dict, errors: set[str]) -> None:
    flora = packet.get("flora", {})
    if not flora.get("used"):
        return
    if flora.get("endpoint") != "https://agents.flora.ai/mcp" or flora.get("top_tool") not in {"search_docs", "execute"}:
        errors.add("BLOCKED_FLORA_ROUTING")
    if flora.get("charged") and not flora.get("approval"):
        errors.add("BLOCKED_FLORA_ROUTING")


def validate(packet: dict) -> dict:
    errors: set[str] = set()
    widths = check_breakpoints(packet, errors)
    if contains_style(packet.get("wireframe", {})):
        errors.add("BLOCKED_STYLE_IN_WIREFRAME")
    check_integrations(packet, errors)
    check_visual(packet, widths, errors)
    check_performance(packet, widths, errors)
    check_images(packet, errors)
    check_flora(packet, errors)
    ordered = sorted(errors)
    if ordered:
        status = ordered[0] if len(ordered) == 1 else "BLOCKED_VALIDATION"
    else:
        degraded = any(row.get("status") != "PASS" for row in packet.get("integrations", []))
        status = "PASS_RELEASE_DEGRADED" if degraded else "PASS_RELEASE"
    return {"status": status, "errors": ordered, "packet_sha256": hashlib.sha256(canonical(packet)).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    result = validate(packet)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"].startswith("PASS_RELEASE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
