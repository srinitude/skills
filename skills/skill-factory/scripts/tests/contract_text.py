"""Read root-routed task rules for document guards, not semantic acceptance."""
import re
import sys
from cli import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from task_definitions import load_tasks


def rule_work(tasks, name):
    task = tasks[name]
    if task["run"] != "node scripts/run_rule.ts " + name:
        raise ValueError("root rule has no matching workflow: " + name)
    work = task["description"].split("## Work\n\n", 1)[1].split("\n## Proof", 1)[0]
    return " ".join(work.split())


def contract_text(path):
    text = path.read_text(encoding="utf-8")
    if path.name != "SKILL.md":
        return text
    tasks = load_tasks(path.parent)
    lines = []
    for line in text.splitlines():
        names = re.findall(r"mise run (rule:[a-z0-9-]+)", line)
        lines.append(line)
        for name in dict.fromkeys(names):
            lines.append(rule_work(tasks, name))
    return "\n".join(lines) + "\n"
