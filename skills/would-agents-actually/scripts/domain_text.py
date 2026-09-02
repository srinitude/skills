"""Exact normalized phrase matching for skill-domain contracts."""
import re

GENERIC_TASK_PATTERNS = (
    r"operation advances or proves its named package state",
    r"operation produces objective progress or a bounded failure",
    r"task exits with current parseable evidence",
    r"work needs [a-z0-9 -]+ ownership to avoid bypassed generic or stale mechanics",
)


def words(value):
    return re.findall(r"[a-z0-9]+", str(value).lower())


def phrase_in_words(source, term):
    phrase = words(term)
    if not phrase:
        return False
    width = len(phrase)
    return any(source[index:index + width] == phrase
               for index in range(len(source) - width + 1))


def uses_term(value, terms):
    source = words(value)
    return any(phrase_in_words(source, term) for term in terms)


def uses_generic_task_template(value):
    """Return whether domain words merely decorate a generic task record."""
    source = " ".join(words(value))
    return any(re.search(pattern, source) for pattern in GENERIC_TASK_PATTERNS)
