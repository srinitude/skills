"""Command-line parser for the execution pipeline."""
import argparse

from lib.pipeline import command_block, command_init, command_packet
from lib.pipeline import command_pass, command_start, command_status


def base_command(commands, name, help_text, handler):
    command = commands.add_parser(name, help=help_text)
    command.add_argument("--run", required=True)
    command.set_defaults(handler=handler)
    return command


def add_init(commands):
    text = "Create a run record with 25 PENDING steps and hashed inputs."
    command = base_command(commands, "init", text, command_init)
    for name in ["run-id", "name", "request", "anchor"]:
        command.add_argument(f"--{name}", required=True)
    command.add_argument("--source", action="append", required=True)
    command.add_argument("--force", action="store_true")


def add_start(commands):
    text = "Check inputs and predecessor state, then mark one step RUNNING."
    command = base_command(commands, "start", text, command_start)
    command.add_argument("--step", required=True)


def add_pass(commands):
    text = "Hash every named output and mark one RUNNING step PASS."
    command = base_command(commands, "pass", text, command_pass)
    command.add_argument("--step", required=True)
    command.add_argument("--output", action="append", default=[])
    command.add_argument("--check", action="append", default=[])
    command.add_argument("--evidence", action="append", default=[])


def add_block(commands):
    text = "Record one allowed error, reason, and recovery for a RUNNING step."
    command = base_command(commands, "block", text, command_block)
    for name in ["step", "code", "reason", "recovery"]:
        command.add_argument(f"--{name}", required=True)
    command.add_argument("--check", action="append", default=[])
    command.add_argument("--evidence", action="append", default=[])


def add_packet(commands):
    text = "Write the exact input, output, support, and owner packet for one step."
    command = base_command(commands, "packet", text, command_packet)
    command.add_argument("--step", required=True)
    command.add_argument("--output", required=True)


def add_status(commands):
    text = "Report current step counts and whole-run completion state."
    base_command(commands, "status", text, command_status)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Create and enforce the deterministic 25-step run scaffold.")
    commands = root.add_subparsers(dest="command", required=True)
    builders = [add_init, add_start, add_pass, add_block, add_packet, add_status]
    for builder in builders:
        builder(commands)
    return root
