"""Tests for complete standardization change reporting."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from standardize_registry_skill import planned_paths


class TestChangeInventory(unittest.TestCase):
    def test_includes_formatter_owned_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            extra = root / "examples/formatter-owned.json"
            extra.parent.mkdir(parents=True)
            extra.write_text('{"value":true}\n', encoding="utf-8")
            self.assertIn(extra, planned_paths(root, {}))


if __name__ == "__main__":
    unittest.main()
