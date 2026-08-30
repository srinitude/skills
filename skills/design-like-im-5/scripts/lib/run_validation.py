"""Check run forms. Keep each field. Keep each link. Do not pick the design."""
from check_context_routing import record_context_issues
from review_checklist import ANSWER_FIELDS, REVIEW_CHECKLIST, REVIEW_DECISIONS


def valid_state_record(record):
    missing = []
    if record.get("open_world") is not True or record.get("exhaustive") is not False:
        missing.append("open state set")
    items = record.get("state_items")
    if not isinstance(items, list) or not items:
        return missing + ["state item"]
    needed = [
        "id", "scope", "context", "causes", "transitions", "model_reviews",
        "negative_reviews", "best_response", "alternatives", "evidence",
        "uncertainty",
    ]
    for item in items:
        missing.extend(key for key in needed if not item.get(key))
    return missing


def valid_review_groups(record, record_key, checklist_key):
    missing = []
    reviews = record.get(record_key, {})
    for lens, checks in REVIEW_CHECKLIST[checklist_key].items():
        answers = reviews.get(lens, [])
        by_id = {answer.get("id"): answer for answer in answers
                 if isinstance(answer, dict)}
        if len(answers) != len(checks) or set(by_id) != {
                item["id"] for item in checks}:
            missing.append(f"{lens} review checklist")
        for check in checks:
            answer = by_id.get(check["id"])
            if not answer:
                missing.append(f"{check['id']} model review")
                continue
            missing.extend(f"{check['id']} {key}" for key in ANSWER_FIELDS
                           if not answer.get(key))
            if answer.get("decision") not in REVIEW_DECISIONS:
                missing.append(f"{check['id']} decision")
    return missing


def valid_model_reviews(record):
    positive = valid_review_groups(record, "model_reviews", "lenses")
    negative = valid_review_groups(
        record, "negative_reviews", "negative_checks")
    return positive + negative


def valid_exploration(record, packet):
    options = record.get("options")
    if not isinstance(options, list) or len(options) < 4:
        return ["four design options", "model choice"]
    needed = packet["exploration_contract"]["required_option_fields"]
    missing = [f"option {key}" for option in options for key in needed
               if not option.get(key)]
    ids = [option.get("id") for option in options]
    if len(set(ids)) != len(ids):
        missing.append("unique option ids")
    chosen = record.get("chosen_direction")
    if not isinstance(chosen, dict) or not chosen.get("reason"):
        missing.append("model choice")
    elif not set(chosen.get("source_option_ids", [])) <= set(ids):
        missing.append("chosen source option ids")
    return missing


def valid_record(record, packet):
    needed = [
        "action", "decision", "evidence", "reason", "counterevidence",
        "uncertainty", "affected",
    ]
    missing = [key for key in needed if key not in record]
    if record.get("action") != packet.get("action"):
        missing.append("matching action")
    if record.get("decision") not in packet["allowed_decisions"]:
        missing.append("allowed decision")
    if not isinstance(record.get("evidence"), list) or not record.get("evidence"):
        missing.append("evidence item")
    if packet.get("action") == "state_judgment":
        missing.extend(valid_state_record(record))
        for item in record.get("state_items", []):
            missing.extend(valid_model_reviews(item))
    if packet.get("action") == "visual_review":
        missing.extend(valid_model_reviews(record))
    if packet.get("exploration_contract"):
        missing.extend(valid_exploration(record, packet))
    missing.extend(record_context_issues(record, packet.get("context_bundle", {})))
    return sorted(set(missing))
