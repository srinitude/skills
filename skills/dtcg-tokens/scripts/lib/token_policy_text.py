"""Validate DTCG policy prose and research receipt structure."""
import re


GENERIC_PATTERNS = (
    r"operation advances or proves its named package state",
    r"operation produces objective progress or a bounded failure",
    r"task exits with current parseable evidence",
    r"work needs [a-z0-9 -]+ ownership to avoid bypassed generic or stale mechanics",
)


def words(value):
    return re.findall(r"[a-z0-9]+", str(value).lower())


def uses_term(value, terms):
    source = words(value)
    for term in terms:
        phrase = words(term)
        width = len(phrase)
        if phrase and any(source[i:i + width] == phrase
                          for i in range(len(source) - width + 1)):
            return True
    return False


def uses_generic_template(value):
    source = " ".join(words(value))
    return any(re.search(pattern, source) for pattern in GENERIC_PATTERNS)


def text_problems(record, fields, terms, label):
    found = []
    for field in fields:
        value = record.get(field) if isinstance(record, dict) else None
        if not isinstance(value, str) or not uses_term(value, terms):
            found.append(f"{label}.{field} needs a DTCG token term")
        elif uses_generic_template(value):
            found.append(f"{label}.{field} uses generic scaffold language")
    return found
