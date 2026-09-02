"""Check design rule text and receipt shape."""
import re


GENERIC_PATTERNS = (
    r"work moves or proves its named file state",
    r"work makes real progress or a clear stop",
    r"task exits with fresh proof that code can read",
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


def text_problems(record, fields, terms, label):
    found, values = [], []
    for field in fields:
        value = record.get(field) if isinstance(record, dict) else None
        source = " ".join(words(value)) if isinstance(value, str) else ""
        if not isinstance(value, str) or not uses_term(value, terms):
            found.append(f"{label}.{field} needs a design term")
        elif any(re.search(pattern, source) for pattern in GENERIC_PATTERNS):
            found.append(f"{label}.{field} uses stock tool text")
        if source:
            values.append(source)
    if len(values) != len(set(values)):
        found.append(f"{label} fields must not repeat one claim")
    return found
