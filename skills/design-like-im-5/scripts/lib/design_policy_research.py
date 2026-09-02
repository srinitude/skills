"""Check fresh design source receipts."""
import datetime
from urllib.parse import urlparse


RECEIPT_FIELDS = {
    "source", "source_class", "claim", "disposition", "checked_at",
    "limitations", "dimensions",
}
COUNTER_FIELDS = {"question", "source", "checked_at", "result", "disposition"}
SOURCE_CLASSES = {"first_party", "standard", "research", "practitioner",
                  "live_owner"}
DISPOSITIONS = {"retained", "adapted", "bounded", "rejected"}
MAX_AGE = datetime.timedelta(days=31)
FUTURE_TOLERANCE = datetime.timedelta(minutes=5)


def web_url(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme in {"http", "https"} and parsed.netloc)


def time_problem(value, label, now):
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return f"{label}.checked_at needs a time zone"
    if parsed.tzinfo is None:
        return f"{label}.checked_at needs a timezone"
    checked = parsed.astimezone(datetime.timezone.utc)
    if checked > now + FUTURE_TOLERANCE:
        return f"{label}.checked_at is in the future"
    if now - checked > MAX_AGE:
        return f"{label}.checked_at is not current"
    return None


def receipt_problems(item, index, dimensions, now):
    label, found = f"research_receipts.{index}", []
    if not isinstance(item, dict) or not RECEIPT_FIELDS <= set(item):
        return [f"{label} lacks design source fields"]
    if not web_url(item["source"]):
        found.append(f"{label}.source needs a web URL")
    if item["source_class"] not in SOURCE_CLASSES:
        found.append(f"{label}.source_class is not valid")
    if item["disposition"] not in DISPOSITIONS:
        found.append(f"{label}.disposition is not valid")
    if any(not str(item[field]).strip() for field in ["claim", "limitations"]):
        found.append(f"{label} has blank design proof")
    values = item["dimensions"]
    if not isinstance(values, list) or not values or not set(values) <= dimensions:
        found.append(f"{label}.dimensions are not valid")
    issue = time_problem(item["checked_at"], label, now)
    return found + ([issue] if issue else [])


def set_problems(receipts, dimensions):
    valid = [item for item in receipts
             if isinstance(item, dict) and RECEIPT_FIELDS <= set(item)]
    sources = {item["source"] for item in valid if web_url(item["source"])}
    hosts = {urlparse(source).netloc for source in sources}
    classes = {item["source_class"] for item in valid}
    covered = {value for item in valid for value in item["dimensions"]}
    found = []
    if len(valid) != len(sources):
        found.append("design source receipts must not repeat a source")
    if len(sources) < 4:
        found.append("design research needs four web sources")
    if len(hosts) < 2:
        found.append("design research needs two web hosts")
    if len(classes) < 2:
        found.append("design research needs two source types")
    if covered != dimensions:
        found.append("design research does not cover each part")
    return found


def counter_problems(counters, now):
    if not isinstance(counters, list) or not counters:
        return ["design research needs fresh proof against its claim"]
    found = []
    for index, item in enumerate(counters):
        label = f"disconfirmation.{index}"
        if not isinstance(item, dict) or not COUNTER_FIELDS <= set(item):
            found.append(f"{label} lacks design source fields")
            continue
        if not web_url(item["source"]):
            found.append(f"{label}.source needs a web URL")
        issue = time_problem(item["checked_at"], label, now)
        if issue:
            found.append(issue)
    return found


def research_problems(contract, dimensions):
    now, found = datetime.datetime.now(datetime.timezone.utc), []
    questions = contract.get("research_questions", {})
    if not isinstance(questions, dict) or set(questions) != dimensions:
        found.append("source questions must cover each design part")
    receipts = contract.get("research_receipts", [])
    if not isinstance(receipts, list):
        return found + ["design source receipts must be a list"]
    for index, item in enumerate(receipts):
        found += receipt_problems(item, index, dimensions, now)
    return found + set_problems(receipts, dimensions) + counter_problems(
        contract.get("disconfirmation"), now)
