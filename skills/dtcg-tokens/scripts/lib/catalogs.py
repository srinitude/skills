"""Stable catalog expansion helpers."""


def catalog_leaves(catalog):
    leaves = []
    for domain, values in catalog.get("domains", {}).items():
        leaves.extend(f"{domain}/{value}" for value in values)
    return leaves


def enum_values(catalog, section, facet):
    return set(catalog.get(section, {}).get(facet, []))


def check_enum(value, allowed, path, errors):
    if value not in allowed:
        errors.append(f"{path} has unknown value {value}")


def check_enum_list(values, allowed, path, errors):
    if not isinstance(values, list) or not values:
        errors.append(f"{path} must be a nonempty array")
        return
    for value in values:
        check_enum(value, allowed, path, errors)
