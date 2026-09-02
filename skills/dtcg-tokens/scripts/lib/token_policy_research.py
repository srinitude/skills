"""Validate current source-backed DTCG domain research receipts."""
import datetime
from urllib.parse import urlparse


RECEIPT_FIELDS = {"source", "source_class", "claim", "disposition",
                  "checked_at", "limitations", "dimensions"}
COUNTER_FIELDS = {"question", "source", "checked_at", "result", "disposition"}
SOURCE_CLASSES = {"first_party", "standard", "research", "practitioner",
                  "live_owner"}
DISPOSITIONS = {"retained", "adapted", "bounded", "rejected"}
MAX_AGE = datetime.timedelta(days=31)
FUTURE_TOLERANCE = datetime.timedelta(minutes=5)


def web_url(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme in {"http", "https"} and parsed.netloc)


def current_time_problem(value, label, now):
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return f"{label}.checked_at needs a timezone"
    if parsed.tzinfo is None:
        return f"{label}.checked_at needs a timezone"
    checked = parsed.astimezone(datetime.timezone.utc)
    if checked > now + FUTURE_TOLERANCE:
        return f"{label}.checked_at is in the future"
    if now - checked > MAX_AGE:
        return f"{label}.checked_at is not current"
    return None


def receipt_item_problems(item, index, dimensions, now):
    label, found = f"research_receipts.{index}", []
    if not isinstance(item, dict) or not RECEIPT_FIELDS <= set(item):
        return [f"{label} needs complete receipt provenance"]
    if not web_url(item["source"]):
        found.append(f"{label}.source must be a web URL")
    if item["source_class"] not in SOURCE_CLASSES:
        found.append(f"{label}.source_class is invalid")
    if item["disposition"] not in DISPOSITIONS:
        found.append(f"{label}.disposition is invalid")
    for field in ["claim", "limitations"]:
        if not isinstance(item[field], str) or not item[field].strip():
            found.append(f"{label}.{field} is empty")
    values = item["dimensions"]
    if not isinstance(values, list) or not values or not set(values) <= dimensions:
        found.append(f"{label}.dimensions are invalid")
    problem = current_time_problem(item["checked_at"], label, now)
    return found + ([problem] if problem else [])


def receipt_set_problems(receipts, dimensions):
    valid = [item for item in receipts
             if isinstance(item, dict) and RECEIPT_FIELDS <= set(item)]
    sources = {item["source"] for item in valid if web_url(item["source"])}
    hosts = {urlparse(source).netloc for source in sources}
    classes = {item["source_class"] for item in valid}
    covered = {value for item in valid for value in item["dimensions"]
               if isinstance(value, str)}
    found = []
    if len(sources) < 4:
        found.append("DTCG token research needs four distinct web sources")
    if len(hosts) < 2:
        found.append("DTCG token research needs at least two web hosts")
    if len(classes) < 2:
        found.append("DTCG token research needs at least two source classes")
    if covered != dimensions:
        found.append("DTCG token research receipt coverage is incomplete")
    return found


def counter_problems(counters, now):
    if not isinstance(counters, list) or not counters:
        return ["DTCG token research needs current counterevidence"]
    found = []
    for index, item in enumerate(counters):
        label = f"disconfirmation.{index}"
        if not isinstance(item, dict) or not COUNTER_FIELDS <= set(item):
            found.append(f"{label} needs complete provenance")
            continue
        if not web_url(item["source"]):
            found.append(f"{label}.source must be a web URL")
        for field in ["question", "result", "disposition"]:
            if not isinstance(item[field], str) or not item[field].strip():
                found.append(f"{label}.{field} is empty")
        problem = current_time_problem(item["checked_at"], label, now)
        if problem:
            found.append(problem)
    return found


def research_problems(contract, dimensions):
    now, found = datetime.datetime.now(datetime.timezone.utc), []
    questions = contract.get("research_questions", {})
    if not isinstance(questions, dict) or set(questions) != dimensions:
        found.append("research questions must cover every DTCG token aspect")
    receipts = contract.get("research_receipts", [])
    if not isinstance(receipts, list):
        return found + ["DTCG token research receipts must be an array"]
    for index, item in enumerate(receipts):
        found += receipt_item_problems(item, index, dimensions, now)
    found += receipt_set_problems(receipts, dimensions)
    found += counter_problems(contract.get("disconfirmation"), now)
    return found
