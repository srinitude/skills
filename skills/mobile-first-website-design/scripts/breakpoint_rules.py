#!/usr/bin/env python3
"""Deterministic breakpoint checks for website design packets."""

from __future__ import annotations


def widths(packet: dict) -> list[int]:
    """Return declared widths or raise a stable validation error."""
    points = packet.get("breakpoints", [])
    values = [item.get("width") for item in points]
    if not values or any(type(value) is not int or value <= 0 for value in values):
        raise ValueError("BLOCKED_BREAKPOINT_ORDER")
    if values != sorted(set(values)):
        raise ValueError("BLOCKED_BREAKPOINT_ORDER")
    return values


def check_stage_order(packet: dict, values: list[int]) -> None:
    """Require every responsive stage to traverse the same ascending widths."""
    stages = packet.get("stage_breakpoints", {})
    required = ("structure", "style", "implementation", "motion", "validation")
    for stage in required:
        if stages.get(stage) != values:
            raise ValueError("BLOCKED_BREAKPOINT_ORDER")


def validate(packet: dict) -> list[int]:
    """Validate declarations and stage traversal."""
    values = widths(packet)
    check_stage_order(packet, values)
    return values
