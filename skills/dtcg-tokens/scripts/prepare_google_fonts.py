#!/usr/bin/env python3
"""Verify live Google Font rarity and emit self-contained WOFF2 CSS."""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from lib.google_fonts import FONT_URL_RE, evaluate_candidates, inline_font_css, validate_catalog_response_date, validate_selection


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Mozilla/5.0 AppleWebKit/537.36 Chrome/120 Safari/537.36"


def arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", required=True, help="eligible family; repeat at least three times")
    parser.add_argument("--select-spec", action="append", required=True, help="CSS2 family spec, such as 'Victor Mono:wght@400;700'")
    parser.add_argument("--required-subset", action="append", default=[], help="required catalog subset; defaults to latin; repeat as needed")
    parser.add_argument("--run-date", required=True, help="fresh local run date in YYYY-MM-DD form")
    parser.add_argument("--output-catalog", required=True, help="saved exact live catalog JSON")
    parser.add_argument("--output-manifest", required=True, help="font selection and asset evidence JSON")
    parser.add_argument("--output-css", required=True, help="self-contained @font-face CSS")
    return parser.parse_args(argv)


def fetch(url, code):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read(), dict(response.headers.items())
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError(f"{code} failed to fetch {url}: {error}") from error


def selected_family(spec):
    return spec.split(":", 1)[0].strip()


def css_request(base, specs):
    params = [("family", spec) for spec in specs] + [("display", "swap")]
    return base + "?" + urllib.parse.urlencode(params)


def font_slug(family):
    return re.sub(r"[^a-z0-9]", "", family.lower())


def try_fetch(url):
    try:
        return fetch(url, "E_FONT_ASSET")[0]
    except ValueError:
        return None


def license_record(repository, family):
    raw = repository.replace("https://github.com/", "https://raw.githubusercontent.com/") + "/main"
    slug = font_slug(family)
    for directory, license_id, filenames in [("ofl", "OFL-1.1", ["OFL.txt"]), ("apache", "Apache-2.0", ["LICENSE.txt", "APACHE2.txt"]), ("ufl", "UFL-1.0", ["UFL.txt", "LICENSE.txt"])]:
        metadata = try_fetch(f"{raw}/{directory}/{slug}/METADATA.pb")
        if metadata is None:
            continue
        for filename in filenames:
            url = f"{raw}/{directory}/{slug}/{filename}"
            text = try_fetch(url)
            if text is not None:
                return {"id": license_id, "source_url": url, "sha256": hashlib.sha256(text).hexdigest(), "text": text.decode("utf-8")}
    raise ValueError(f"E_FONT_ASSET license unavailable for {family}")


def live_catalog(policy):
    raw, headers = fetch(policy["catalog"]["url"], "E_FONT_CURRENT")
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"E_FONT_CURRENT catalog is not JSON: {error}") from error
    response_date = headers.get("Date") or headers.get("date")
    if not response_date:
        raise ValueError("E_FONT_CURRENT catalog response has no Date header")
    return raw, document, response_date


def live_css(policy, specs):
    url = css_request(policy["catalog"]["css_api_url"], specs)
    raw, _ = fetch(url, "E_FONT_ASSET")
    css = raw.decode("utf-8")
    urls = sorted({match.group(2) for match in FONT_URL_RE.finditer(css)})
    if not urls:
        raise ValueError("E_FONT_ASSET Google Fonts CSS has no WOFF2 URLs")
    assets = {url: fetch(url, "E_FONT_ASSET")[0] for url in urls}
    return url, inline_font_css(css, assets)


def selected_records(result, asset_records, licenses):
    by_family = {item["family"]: item for item in result["candidates"]}
    records = []
    for family in result["selected_families"]:
        item = dict(by_family[family])
        item.update({"token_paths": [], "license": licenses[family], "assets": [asset for asset in asset_records if asset["family"] == family], "visual_review": {"status": "pending_visual_review", "specimens": [], "rationale": ""}})
        if not item["assets"]:
            raise ValueError(f"E_FONT_ASSET no WOFF2 assets returned for {family}")
        records.append(item)
    return records


def write(path, data, binary=False):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data) if binary else output.write_text(data, encoding="utf-8")


def main(argv=None):
    args = arguments(argv)
    policy = json.loads((ROOT / "assets" / "google-font-policy.json").read_text(encoding="utf-8"))
    selected = [selected_family(spec) for spec in args.select_spec]
    required_subsets = args.required_subset or ["latin"]
    try:
        raw, catalog, response_date = live_catalog(policy)
        validate_catalog_response_date(response_date, args.run_date, maximum_age_seconds=policy["catalog"]["maximum_age_seconds"])
        result = evaluate_candidates(catalog, args.candidate, selected, policy["uncommon_threshold"], required_subsets)
        errors = validate_selection(result, policy["selection"]["minimum_candidates"])
        if errors:
            raise ValueError(" | ".join(errors))
        css_url, (css, assets) = live_css(policy, args.select_spec)
        licenses = {family: license_record(policy["catalog"]["repository_url"], family) for family in selected}
        manifest = {"policy_version": policy["policy_version"], "run_date": args.run_date, "catalog_url": policy["catalog"]["url"], "catalog_response_date": response_date, "catalog_sha256": hashlib.sha256(raw).hexdigest(), **result, "required_subsets": required_subsets, "css_request_url": css_url, "selected": selected_records(result, assets, licenses), "selection_review": {"status": "pending_visual_review", "comparison": ""}}
        write(args.output_catalog, raw, binary=True)
        write(args.output_css, css)
        write(args.output_manifest, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "prepared-pending-visual-review", "catalog_sha256": manifest["catalog_sha256"], "total_families": manifest["total_families"], "cutoff_rank": manifest["cutoff_rank"], "selected": selected}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
