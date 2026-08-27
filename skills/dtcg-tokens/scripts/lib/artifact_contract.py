"""Structural contract for one vision-authored standalone proof artifact."""
import hashlib
import re
from html.parser import HTMLParser

OBLIGATIONS = {
    "conformance", "inputs", "intent", "possibilities", "narrowing",
    "coverage", "token-specimens", "experiments", "permutations", "metrics",
    "perceptual-motor-invariants", "taste", "originality",
    "corpus-uniqueness", "non-ai-slop", "visual-review", "failures",
    "boundary", "embedded-data",
}
FORBIDDEN_MARKERS = {
    "data-style-fingerprint": "style fingerprints do not prove design quality",
    "data-content-fingerprint": "content fingerprints do not prove source specificity",
    "data-generation-method=\"token-directed\"": "automatic visual generation is prohibited",
}
HIDDEN_TAGS = {"head", "script", "style", "template"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
RUNTIME_ATTRIBUTES = {"script": {"src"}, "img": {"src", "srcset"}, "iframe": {"src"}, "audio": {"src"}, "video": {"src", "poster"}, "source": {"src", "srcset"}, "link": {"href"}, "object": {"data"}, "embed": {"src"}, "image": {"href", "xlink:href"}, "use": {"href", "xlink:href"}}


def element_hidden(tag, attributes, parent_hidden):
    attrs = dict(attributes)
    style = str(attrs.get("style", "")).lower().replace(" ", "")
    return parent_hidden or tag in HIDDEN_TAGS or "hidden" in attrs or "inert" in attrs or attrs.get("aria-hidden") == "true" or tag == "input" and attrs.get("type") == "hidden" or any(marker in style for marker in ("display:none", "visibility:hidden", "opacity:0"))


class VisibleAttributeParser(HTMLParser):
    def __init__(self, attribute):
        super().__init__(convert_charrefs=True)
        self.attribute = attribute
        self.stack = []
        self.values = []

    def handle_starttag(self, tag, attrs):
        hidden = element_hidden(tag, attrs, self.stack[-1][1] if self.stack else False)
        values = dict(attrs)
        if not hidden and self.attribute in values:
            self.values.append(values[self.attribute])
        if tag not in VOID_TAGS:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag, attrs):
        hidden = element_hidden(tag, attrs, self.stack[-1][1] if self.stack else False)
        values = dict(attrs)
        if not hidden and self.attribute in values:
            self.values.append(values[self.attribute])

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


class RuntimeAssetParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.external = False

    def inspect(self, tag, attrs):
        for name, value in attrs:
            if name in RUNTIME_ATTRIBUTES.get(tag, set()) and not str(value).startswith(("data:", "#")):
                self.external = True

    def handle_starttag(self, tag, attrs):
        self.inspect(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.inspect(tag, attrs)


def obligation_counts(text):
    names = re.findall(r'data-proof-obligation=["\']([^"\']+)["\']', text)
    return {name: names.count(name) for name in set(names)}


def check_obligations(text, errors):
    counts = obligation_counts(text)
    for name in sorted(OBLIGATIONS):
        if counts.get(name) != 1:
            errors.append(f"artifact obligation {name} must appear exactly once")
    unknown = sorted(set(counts) - OBLIGATIONS)
    if unknown:
        errors.append(f"unknown artifact obligations: {', '.join(unknown)}")


def check_external_assets(text, errors):
    parser = RuntimeAssetParser()
    parser.feed(text)
    parser.close()
    urls = [item.strip().strip('"\'') for item in re.findall(r"url\(([^)]+)\)", text, re.IGNORECASE)]
    external_css = re.search(r"@import\b", text, re.IGNORECASE) or any(item and not item.startswith(("data:", "#")) for item in urls)
    if parser.external or external_css:
        errors.append("external runtime asset blocks the standalone artifact")


def check_candidate(text):
    errors = []
    lowered = text.lower()
    if "<!doctype html>" not in lowered:
        errors.append("candidate needs an HTML doctype")
    if 'data-dtcg-proof="2.0"' not in text:
        errors.append("candidate needs data-dtcg-proof 2.0")
    if 'data-artifact-authorship="vision-authored"' not in text:
        errors.append("candidate must declare vision-authored artifact direction")
    if text.count("__DTCG_PROOF_DATA__") != 1 or text.count("__DTCG_RUN_ID__") != 1:
        errors.append("candidate needs one proof-data and one run-id placeholder")
    if text.count("__DTCG_PROOF_VERDICT__") != 1 or text.count("__DTCG_VERDICT_STATE__") != 1:
        errors.append("candidate needs one visible and one machine verdict placeholder")
    if text.count("data-verdict") != 1 or any(marker in text for marker in ("[data-verdict", "dataset.verdict", "getAttribute('data-verdict", 'getAttribute("data-verdict')):
        errors.append("candidate must not make rendering depend on the machine verdict state")
    if text.count("proof-data") != 1:
        errors.append("rendering must not depend on embedded proof data")
    for marker, reason in FORBIDDEN_MARKERS.items():
        if marker in text:
            errors.append(reason)
    check_obligations(text, errors)
    check_external_assets(text, errors)
    return errors


def check_experimental_specimens(text, expected_paths):
    actual = re.findall(r'data-experimental-token=["\']([^"\']+)["\']', text)
    if len(actual) != len(set(actual)) or set(actual) != set(expected_paths):
        return ["experimental specimen coverage mismatch"]
    return []


def attribute_values(text, name):
    parser = VisibleAttributeParser(name)
    parser.feed(text)
    parser.close()
    return parser.values


def coverage_set(text, attribute, expected, label, errors):
    actual = attribute_values(text, attribute)
    duplicates = len(actual) != len(set(actual))
    missing = set(expected) - set(actual)
    unexpected = set(actual) - set(expected)
    if duplicates or missing or unexpected:
        errors.append(f"{label} coverage mismatch: expected {len(expected)}, found {len(actual)}")
    return {"expected": len(expected), "found": len(actual), "missing": len(missing), "unexpected": len(unexpected), "duplicates": duplicates}


def check_visible_coverage(text, coverage):
    errors = []
    tokens = [item["path"] for item in coverage["token_paths"]]
    stress = [item["id"] for item in coverage["stress_groups"]]
    permutations = [cell["id"] for group in coverage["variant_groups"] for cell in group["cells"]]
    report = {
        "tokens": coverage_set(text, "data-token-path", tokens, "token specimen", errors),
        "stress_cells": coverage_set(text, "data-stress-cell", stress, "stress-cell", errors),
        "permutation_cells": coverage_set(text, "data-permutation-cell", permutations, "permutation-cell", errors),
    }
    report["status"] = "pass" if not errors else "fail"
    return report, errors


def reviewed_surface_sha256(text):
    surface = re.sub(r'(<script\b[^>]*\bid=["\']proof-data["\'][^>]*>).*?(</script>)', r"\1__DTCG_PROOF_DATA__\2", text, flags=re.IGNORECASE | re.DOTALL)
    surface = re.sub(r'data-verdict=["\'][^"\']*["\']', 'data-verdict="__DTCG_VERDICT_STATE__"', surface, count=1)
    surface = surface.replace("RECORDED VISUAL REVIEW · BOUNDED PASS", "__DTCG_PROOF_VERDICT__")
    surface = surface.replace("PENDING VISUAL REVIEW", "__DTCG_PROOF_VERDICT__")
    return hashlib.sha256(surface.encode("utf-8")).hexdigest()


def assemble(text, payload, run_id, verdict="pending"):
    packed = payload.replace("<", "\\u003c")
    result = text.replace("__DTCG_PROOF_DATA__", packed)
    result = result.replace("__DTCG_RUN_ID__", run_id)
    label = "RECORDED VISUAL REVIEW · BOUNDED PASS" if verdict == "recorded-pass" else "PENDING VISUAL REVIEW"
    result = result.replace("__DTCG_VERDICT_STATE__", verdict)
    return result.replace("__DTCG_PROOF_VERDICT__", label)
