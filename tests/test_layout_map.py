import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "templates" / "danone-template-manifest.json"
LAYOUT_MAP = ROOT / "templates" / "layout-map.json"


class LayoutMapTest(unittest.TestCase):
    def test_layout_map_targets_exist_in_manifest(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        layout_map = json.loads(LAYOUT_MAP.read_text(encoding="utf-8"))
        known_layouts = {layout["name"] for layout in manifest["layouts"]}

        self.assertEqual(layout_map["template_manifest"], "danone-template-manifest.json")
        self.assertEqual(layout_map["default_template"], "Danone Real Templates/Standard Danone Template.pptx")

        for intent, config in layout_map["intents"].items():
            with self.subTest(intent=intent):
                self.assertIn(config["preferred_layout"], known_layouts)
                self.assertGreaterEqual(len(config["fallback_layouts"]), 1)
                for fallback in config["fallback_layouts"]:
                    self.assertIn(fallback, known_layouts)


if __name__ == "__main__":
    unittest.main()
