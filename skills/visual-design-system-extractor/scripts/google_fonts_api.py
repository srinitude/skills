"""Live Google Fonts catalog access and rarity math.

Reads the public family metadata feed at request time so rarity is
measured against current data instead of a stored font list. Every
family record keeps its popularity rank, trending rank, date added,
variable-axis flag, subsets, and designers.

Rarity percentile runs from 0.0 for the single most popular family to
100.0 for the least popular one, computed from the live rank and the
live family count.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import date

FEED_URL = "https://fonts.google.com/metadata/fonts"
DEFAULT_TIMEOUT = 30


class FeedError(RuntimeError):
    """The live feed could not be read or did not parse."""


def fetch_feed(url=FEED_URL, timeout=DEFAULT_TIMEOUT):
    """Return the decoded feed payload, or raise FeedError."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise FeedError(f"live font feed unreachable: {error}") from error
    return parse_feed(raw)


def parse_feed(raw):
    """Return the family list from a raw feed body, or raise FeedError."""
    try:
        payload = json.loads(raw.lstrip(")]}'\n"))
    except json.JSONDecodeError as error:
        raise FeedError(f"live font feed did not parse: {error}") from error
    families = payload.get("familyMetadataList")
    if not isinstance(families, list) or not families:
        raise FeedError("live font feed carried no family metadata")
    return families


def record(entry):
    """Return one normalized family record from a feed entry."""
    return {
        "family": entry.get("family", ""),
        "category": entry.get("category", ""),
        "popularity_rank": entry.get("popularity"),
        "trending_rank": entry.get("trending"),
        "date_added": entry.get("dateAdded", ""),
        "variable": bool(entry.get("axes")),
        "subsets": [item for item in entry.get("subsets", []) if item != "menu"],
        "designers": entry.get("designers", []),
        "is_noto": bool(entry.get("isNoto")),
    }


def build_catalog(families, url=FEED_URL, retrieved_at=None):
    """Return a catalog snapshot with normalized records and provenance."""
    records = [record(entry) for entry in families if entry.get("family")]
    total = len(records)
    for item in records:
        item["total_families"] = total
        item["rarity_percentile"] = rarity_percentile(item["popularity_rank"], total)
    return {
        "source": url,
        "retrieved_at": retrieved_at or date.today().isoformat(),
        "total_families": total,
        "families": records,
    }


def load_catalog(url=FEED_URL, timeout=DEFAULT_TIMEOUT):
    """Fetch the live feed and return a catalog snapshot."""
    return build_catalog(fetch_feed(url, timeout), url)


def rarity_percentile(popularity_rank, total):
    """Return 0.0 for the most popular family and 100.0 for the least."""
    if not isinstance(popularity_rank, int) or total < 2:
        return 0.0
    clamped = min(max(popularity_rank, 1), total)
    return round((clamped - 1) / (total - 1) * 100, 1)


def find(catalog, family):
    """Return the record for a family name, matched without case, or None."""
    wanted = family.strip().casefold()
    for item in catalog["families"]:
        if item["family"].casefold() == wanted:
            return item
    return None


def rarity_block(item, catalog):
    """Return the rarity mapping an extraction must carry for a family."""
    return {
        "popularity_rank": item["popularity_rank"],
        "total_families": catalog["total_families"],
        "rarity_percentile": item["rarity_percentile"],
        "trending_rank": item["trending_rank"],
        "date_added": item["date_added"],
        "variable": item["variable"],
        "source": catalog["source"],
        "retrieved_at": catalog["retrieved_at"],
    }
