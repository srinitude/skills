"""Validate screen, product-state, viewport, and orientation proof."""

def is_typescript(value):
    return isinstance(value, str) and value.endswith((".ts", ".tsx"))


def is_parserless_mapping(value):
    return isinstance(value, str) and value.endswith(".figma.ts")


def screens_apply(record):
    for stage in record.get("stages", []):
        if stage.get("id") == "compose-screens":
            return stage.get("status") == "pass"
    return False


def check_orientation_groups(inventory, contract, problems):
    grouped = {}
    for item in inventory:
        if item.get("form_factor") not in contract["paired_orientation_form_factors"]:
            continue
        key = (item.get("screen"), item.get("product_state"),
               item.get("form_factor"), item.get("input_path"))
        grouped.setdefault(key, set()).add(item.get("orientation"))
    if any(value != {"portrait", "landscape"} for value in grouped.values()):
        problems.append("mobile and tablet contexts need portrait and landscape")


def check_render_contexts(record, contract, problems):
    if not screens_apply(record):
        return
    inventory = record.get("render_context_inventory", [])
    proof = record.get("render_context_proof", [])
    required_context = set(contract["render_context_fields"])
    required_proof = set(contract["render_proof_fields"])
    inventory_ids = [item.get("id") for item in inventory]
    proof_ids = [item.get("id") for item in proof]
    if (not inventory_ids or inventory_ids != proof_ids
            or len(inventory_ids) != len(set(inventory_ids))):
        problems.append("render context coverage must match the current inventory")
    for index, item in enumerate(inventory):
        if not required_context <= set(item):
            problems.append(f"render context inventory {index} is incomplete")
        if item.get("orientation") not in contract["orientation_values"]:
            problems.append(f"render context inventory {index} has invalid orientation")
    for index, item in enumerate(proof):
        if not required_proof <= set(item) or item.get("status") != "pass":
            problems.append(f"render context proof {index} is incomplete")
        if not all(item.get(field) for field in required_proof - {"id", "status"}):
            problems.append(f"render context proof {index} has empty evidence")
        if not is_typescript(item.get("code_evidence")):
            problems.append(f"render context proof {index} needs TypeScript evidence")
        if not is_parserless_mapping(item.get("mapping_evidence")):
            problems.append(f"render context proof {index} needs parserless .figma.ts evidence")
    check_orientation_groups(inventory, contract, problems)
