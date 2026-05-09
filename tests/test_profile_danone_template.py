import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "profile_danone_template.py"
TEMPLATE = ROOT / "Danone Real Templates" / "Standard Danone Template.pptx"


def load_profiler():
    spec = importlib.util.spec_from_file_location("profile_danone_template", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProfileDanoneTemplateTest(unittest.TestCase):
    def setUp(self):
        if not TEMPLATE.exists():
            self.skipTest(f"Real Danone template sample not found: {TEMPLATE}")

    def test_profile_template_extracts_brand_system_and_layout_inventory(self):
        profiler = load_profiler()

        manifest = profiler.profile_template(TEMPLATE)

        self.assertEqual(manifest["source"]["file"], "Standard Danone Template.pptx")
        self.assertEqual(manifest["slide_size"]["width_in"], 13.333)
        self.assertEqual(manifest["slide_size"]["height_in"], 7.5)
        self.assertEqual(manifest["counts"]["slides"], 55)
        self.assertGreaterEqual(manifest["counts"]["layouts"], 200)
        self.assertEqual(manifest["counts"]["masters"], 12)
        self.assertEqual(manifest["counts"]["themes"], 14)
        self.assertEqual(manifest["counts"]["media"], 49)

        theme_names = {theme["name"] for theme in manifest["themes"]}
        self.assertIn("Danone Template - Blue", theme_names)
        self.assertIn("Danone Template - Red", theme_names)

        first_theme = manifest["themes"][0]
        self.assertEqual(first_theme["fonts"]["major_latin"], "Danone One Condensed")
        self.assertEqual(first_theme["fonts"]["minor_latin"], "Danone One Light")
        self.assertEqual(first_theme["colors"]["accent1"], "005EB8")

        layout_names = {layout["name"] for layout in manifest["layouts"]}
        self.assertIn("Blue: Two Content", layout_names)
        self.assertIn("Blue: Three Column", layout_names)
        self.assertIn("Blue: Full Image", layout_names)

        two_content = next(layout for layout in manifest["layouts"] if layout["name"] == "Blue: Two Content")
        self.assertEqual(two_content["family"], "two-content")
        self.assertGreaterEqual(len(two_content["placeholders"]), 5)
        self.assertTrue(any(ph["type"] == "sldNum" for ph in two_content["placeholders"]))

    def test_write_manifest_outputs_stable_json(self):
        profiler = load_profiler()
        out = ROOT / "tests" / "_tmp_manifest.json"

        try:
            manifest = profiler.profile_template(TEMPLATE)
            profiler.write_manifest(manifest, out)

            saved = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(saved["source"]["file"], manifest["source"]["file"])
            self.assertTrue(saved["layouts"][0]["id"].startswith("slideLayout"))
        finally:
            out.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
