import unittest

import context  # noqa: F401
import google_fonts_api as api


class RarityMathTests(unittest.TestCase):
    def test_most_popular_family_scores_zero(self):
        self.assertEqual(api.rarity_percentile(1, 1000), 0.0)

    def test_least_popular_family_scores_one_hundred(self):
        self.assertEqual(api.rarity_percentile(1000, 1000), 100.0)

    def test_rank_beyond_the_count_clamps(self):
        self.assertEqual(api.rarity_percentile(1200, 1000), 100.0)

    def test_missing_rank_scores_zero(self):
        self.assertEqual(api.rarity_percentile(None, 1000), 0.0)


class FeedParsingTests(unittest.TestCase):
    def test_bad_json_raises_feed_error(self):
        with self.assertRaises(api.FeedError):
            api.parse_feed("not json")

    def test_empty_family_list_raises_feed_error(self):
        with self.assertRaises(api.FeedError):
            api.parse_feed('{"familyMetadataList": []}')

    def test_unreachable_host_raises_feed_error(self):
        with self.assertRaises(api.FeedError):
            api.fetch_feed("https://fonts.invalid/metadata/fonts", timeout=5)


class LiveCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = api.load_catalog()

    def test_catalog_carries_provenance_and_families(self):
        self.assertEqual(self.catalog["source"], api.FEED_URL)
        self.assertGreater(self.catalog["total_families"], 500)
        self.assertEqual(len(self.catalog["families"]), self.catalog["total_families"])

    def test_a_known_common_family_is_present_and_popular(self):
        item = api.find(self.catalog, "roboto")
        self.assertIsNotNone(item)
        self.assertLess(item["rarity_percentile"], 10.0)

    def test_an_absent_family_returns_none(self):
        self.assertIsNone(api.find(self.catalog, "Definitely Not A Font Family"))

    def test_rarity_block_holds_every_recorded_field(self):
        block = api.rarity_block(api.find(self.catalog, "roboto"), self.catalog)
        self.assertEqual(
            sorted(block),
            ["date_added", "popularity_rank", "rarity_percentile", "retrieved_at",
             "source", "total_families", "trending_rank", "variable"],
        )


if __name__ == "__main__":
    unittest.main()
