import io
import json
import unittest
from contextlib import redirect_stdout

import context  # noqa: F401
import rare_google_fonts as cli


def call(argv):
    """Run the command line and return its exit code and parsed output."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = cli.main(argv)
    text = buffer.getvalue().strip()
    return code, json.loads(text) if text else None


class CatalogCommandTests(unittest.TestCase):
    def test_catalog_reports_the_live_family_count(self):
        code, payload = call(["catalog"])
        self.assertEqual(code, 0)
        self.assertGreater(payload["total_families"], 500)

    def test_an_unreachable_feed_exits_one(self):
        code, _ = call(["catalog", "--url", "https://fonts.invalid/feed", "--timeout", "5"])
        self.assertEqual(code, 1)


class DiscoverCommandTests(unittest.TestCase):
    def test_discover_returns_ranked_rare_candidates(self):
        code, payload = call(["discover", "--limit", "5"])
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["candidates"]), 5)

    def test_every_candidate_clears_the_floor(self):
        _, payload = call(["discover", "--limit", "5", "--min-rarity-percentile", "90"])
        floors = [item["rarity"]["rarity_percentile"] for item in payload["candidates"]]
        self.assertTrue(all(value >= 90 for value in floors), floors)

    def test_the_category_filter_reaches_the_results(self):
        _, payload = call(["discover", "--limit", "3", "--category", "Monospace"])
        self.assertEqual({item["category"] for item in payload["candidates"]}, {"Monospace"})


class VerifyCommandTests(unittest.TestCase):
    def test_a_common_family_fails(self):
        code, payload = call(["verify", "--family", "Roboto"])
        self.assertEqual(code, 1)
        self.assertEqual(payload["verdicts"][0]["status"], "FAIL")

    def test_a_family_outside_the_catalog_fails(self):
        code, payload = call(["verify", "--family", "Not A Real Family"])
        self.assertEqual(code, 1)
        self.assertIn("not a Google Fonts family", payload["verdicts"][0]["reason"])

    def test_a_discovered_family_passes_verification(self):
        _, found = call(["discover", "--limit", "1"])
        family = found["candidates"][0]["family"]
        code, payload = call(["verify", "--family", family])
        self.assertEqual(code, 0, payload)

    def test_mixed_input_fails_and_reports_both_verdicts(self):
        _, found = call(["discover", "--limit", "1"])
        family = found["candidates"][0]["family"]
        code, payload = call(["verify", "--family", family, "--family", "Roboto"])
        self.assertEqual((code, payload["checked"], payload["failed"]), (1, 2, 1))


if __name__ == "__main__":
    unittest.main()
