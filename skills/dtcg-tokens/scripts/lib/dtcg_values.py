"""DTCG 2025.10 value checks used by the command line validator."""
import re

TYPES = {
    "color", "dimension", "fontFamily", "fontWeight", "duration",
    "cubicBezier", "number", "strokeStyle", "border", "transition",
    "shadow", "gradient", "typography",
}
COLOR_SPACES = {
    "srgb", "srgb-linear", "hsl", "hwb", "lab", "lch", "oklab",
    "oklch", "display-p3", "a98-rgb", "prophoto-rgb", "rec2020",
    "xyz-d65", "xyz-d50",
}
WEIGHTS = {
    "thin", "hairline", "extra-light", "ultra-light", "light", "normal",
    "regular", "book", "medium", "semi-bold", "demi-bold", "bold",
    "extra-bold", "ultra-bold", "black", "heavy", "extra-black",
    "ultra-black",
}
STROKES = {"solid", "dashed", "dotted", "double", "groove", "ridge", "outset", "inset"}
REFERENCE = re.compile(r"^\{[^${}.][^{}.]*(?:\.[^${}.][^{}.]*)*\}$")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_reference(value):
    return isinstance(value, str) and bool(REFERENCE.fullmatch(value))


def problem(path, message):
    return [f"{path}: {message}"]


def object_properties(value, allowed, path):
    extra = sorted(set(value) - set(allowed))
    return problem(path, f"unsupported properties: {', '.join(extra)}") if extra else []


def dimension(value, path):
    if not isinstance(value, dict):
        return problem(path, "dimension value must be an object")
    errors = object_properties(value, {"value", "unit"}, path)
    if not is_number(value.get("value")) or value.get("unit") not in {"px", "rem"}:
        errors += problem(path, "dimension needs numeric value and unit px or rem")
    return errors


def component(value, low=None, high=None, exclusive=False):
    if value == "none" or isinstance(value, dict) and set(value) == {"$ref"}:
        return True
    if not is_number(value) or low is not None and value < low:
        return False
    return high is None or (value < high if exclusive else value <= high)


def component_rules(space):
    if space in {"srgb", "srgb-linear", "display-p3", "a98-rgb", "prophoto-rgb", "rec2020", "xyz-d65", "xyz-d50"}:
        return [(0, 1, False)] * 3
    if space in {"hsl", "hwb"}:
        return [(0, 360, True), (0, 100, False), (0, 100, False)]
    if space == "lab":
        return [(0, 100, False), (None, None, False), (None, None, False)]
    if space == "lch":
        return [(0, 100, False), (0, None, False), (0, 360, True)]
    if space == "oklab":
        return [(0, 1, False), (None, None, False), (None, None, False)]
    return [(0, 1, False), (0, None, False), (0, 360, True)]


def color(value, path):
    if not isinstance(value, dict):
        return problem(path, "color value must be an object")
    errors = object_properties(value, {"colorSpace", "components", "alpha", "hex"}, path)
    if value.get("colorSpace") not in COLOR_SPACES:
        errors += problem(path, "colorSpace is not a DTCG 2025.10 value")
    parts = value.get("components")
    if not isinstance(parts, list) or len(parts) != 3:
        errors += problem(path, "color components must hold three items")
    if isinstance(parts, list) and len(parts) == 3:
        rules = component_rules(value.get("colorSpace"))
        if not all(component(item, *rule) for item, rule in zip(parts, rules)):
            errors += problem(path, "color component is outside its color-space range")
    if "alpha" in value and (not is_number(value["alpha"]) or not 0 <= value["alpha"] <= 1):
        errors += problem(path, "color alpha must be from 0 to 1")
    if "hex" in value and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(value["hex"])):
        errors += problem(path, "color hex must hold six digits")
    return errors


def font_family(value, path):
    valid = isinstance(value, str) or isinstance(value, list) and value and all(isinstance(item, str) for item in value)
    return [] if valid else problem(path, "fontFamily must be a string or nonempty string array")


def font_weight(value, path):
    valid = is_number(value) and 1 <= value <= 1000 or isinstance(value, str) and value in WEIGHTS
    return [] if valid else problem(path, "fontWeight must be 1 to 1000 or a standard alias")


def duration(value, path):
    if not isinstance(value, dict):
        return problem(path, "duration value must be an object")
    errors = object_properties(value, {"value", "unit"}, path)
    valid = is_number(value.get("value")) and value.get("value", -1) >= 0 and value.get("unit") in {"ms", "s"}
    return errors if valid else errors + problem(path, "duration needs nonnegative value and unit ms or s")


def bezier(value, path):
    valid = isinstance(value, list) and len(value) == 4 and all(is_number(item) for item in value)
    if not valid:
        return problem(path, "cubicBezier must hold four numbers")
    return [] if 0 <= value[0] <= 1 and 0 <= value[2] <= 1 else problem(path, "cubicBezier x coordinates must be from 0 to 1")


def stroke(value, path):
    if isinstance(value, str):
        return [] if value in STROKES else problem(path, "strokeStyle string is not standard")
    if not isinstance(value, dict) or value.get("lineCap") not in {"round", "butt", "square"}:
        return problem(path, "strokeStyle object needs a standard lineCap")
    errors = object_properties(value, {"dashArray", "lineCap"}, path)
    dashes = value.get("dashArray")
    if not isinstance(dashes, list) or not dashes:
        return errors + problem(path, "strokeStyle dashArray must be nonempty")
    return errors + sum((dimension(item, f"{path}.dashArray[{index}]") for index, item in enumerate(dashes)), [])


def border(value, path):
    if not isinstance(value, dict):
        return problem(path, "border value must be an object")
    errors = object_properties(value, {"color", "width", "style"}, path)
    errors += validate_value("color", value.get("color"), f"{path}.color")
    errors += validate_value("dimension", value.get("width"), f"{path}.width")
    errors += validate_value("strokeStyle", value.get("style"), f"{path}.style")
    return errors


def transition(value, path):
    if not isinstance(value, dict):
        return problem(path, "transition value must be an object")
    errors = object_properties(value, {"duration", "delay", "timingFunction"}, path)
    errors += validate_value("duration", value.get("duration"), f"{path}.duration")
    errors += validate_value("duration", value.get("delay"), f"{path}.delay")
    errors += validate_value("cubicBezier", value.get("timingFunction"), f"{path}.timingFunction")
    return errors


def one_shadow(value, path):
    if not isinstance(value, dict):
        return problem(path, "shadow layer must be an object")
    errors = object_properties(value, {"color", "offsetX", "offsetY", "blur", "spread", "inset"}, path)
    errors += validate_value("color", value.get("color"), f"{path}.color")
    for key in ("offsetX", "offsetY", "blur", "spread"):
        errors += validate_value("dimension", value.get(key), f"{path}.{key}")
    if "inset" in value and not isinstance(value["inset"], bool):
        errors += problem(path, "shadow inset must be boolean")
    return errors


def shadow(value, path):
    layers = value if isinstance(value, list) else [value]
    if not layers:
        return problem(path, "shadow array must be nonempty")
    return sum(([] if is_reference(item) else one_shadow(item, f"{path}[{index}]") for index, item in enumerate(layers)), [])


def gradient(value, path):
    if not isinstance(value, list) or not value:
        return problem(path, "gradient must hold at least one stop")
    errors = []
    for index, stop in enumerate(value):
        here = f"{path}[{index}]"
        if not isinstance(stop, dict):
            errors += problem(here, "gradient stop must be an object")
            continue
        errors += object_properties(stop, {"color", "position"}, here)
        errors += validate_value("color", stop.get("color"), f"{here}.color")
        if not is_number(stop.get("position")):
            errors += problem(here, "gradient position must be numeric")
    return errors


def typography(value, path):
    if not isinstance(value, dict):
        return problem(path, "typography value must be an object")
    fields = {"fontFamily": "fontFamily", "fontSize": "dimension", "fontWeight": "fontWeight", "letterSpacing": "dimension", "lineHeight": "number"}
    return object_properties(value, fields, path) + sum((validate_value(kind, value.get(key), f"{path}.{key}") for key, kind in fields.items()), [])


VALIDATORS = {
    "color": color, "dimension": dimension, "fontFamily": font_family,
    "fontWeight": font_weight, "duration": duration, "cubicBezier": bezier,
    "strokeStyle": stroke, "border": border, "transition": transition,
    "shadow": shadow, "gradient": gradient, "typography": typography,
}


def validate_value(kind, value, path):
    if is_reference(value) or isinstance(value, dict) and set(value) == {"$ref"}:
        return []
    if kind == "number":
        return [] if is_number(value) else problem(path, "number value must be numeric")
    validator = VALIDATORS.get(kind)
    return validator(value, path) if validator else problem(path, f"unknown type {kind}")
