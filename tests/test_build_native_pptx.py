import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_native_pptx.py"
TEMPLATE = ROOT / "Danone Real Templates" / "Standard Danone Template.pptx"
LAYOUT_MAP = ROOT / "templates" / "layout-map.json"

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def load_builder():
    spec = importlib.util.spec_from_file_location("build_native_pptx", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BuildNativePptxTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            TEMPLATE.exists(),
            f"Real Danone template sample is required for native PPTX tests: {TEMPLATE}",
        )

    def test_resolves_intent_to_available_sample_slide(self):
        builder = load_builder()

        samples = builder.discover_sample_slides(TEMPLATE)
        layout_map = json.loads(LAYOUT_MAP.read_text(encoding="utf-8"))

        opening = builder.resolve_source_slide("opening-cover", layout_map, samples)
        two_column = builder.resolve_source_slide("two-column", layout_map, samples)

        self.assertEqual(opening.slide_number, 1)
        self.assertEqual(opening.layout_name, "标题幻灯片")
        self.assertEqual(two_column.layout_name, "Blue: Two Content Box")

    def test_builds_native_pptx_from_plan_by_cloning_real_sample_slides(self):
        builder = load_builder()
        plan = [
            {
                "intent": "opening-cover",
                "content": {
                    "title": "AI presentation operations",
                    "subtitle_or_date": "May 2026",
                },
            },
            {
                "intent": "two-column",
                "content": {
                    "title": "Native build path",
                    "left_content": "Real template, not recreated HTML",
                    "right_content": "Sample slides are cloned from the Danone PPTX and only editable text is replaced.",
                },
            },
            {
                "intent": "closing",
                "content": {
                    "title": "Thank you",
                },
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "native-danone.pptx"
            builder.build_presentation(TEMPLATE, LAYOUT_MAP, plan, out)

            self.assertTrue(out.exists())
            with zipfile.ZipFile(out) as zf:
                presentation = ET.fromstring(zf.read("ppt/presentation.xml"))
                slide_ids = presentation.find("p:sldIdLst", NS)
                self.assertEqual(len(slide_ids), 3)

                rels = ET.fromstring(zf.read("ppt/_rels/presentation.xml.rels"))
                targets = [rel.attrib["Target"] for rel in rels if rel.attrib["Type"].endswith("/slide")]
                self.assertIn("slides/slide1.xml", targets)
                self.assertIn("slides/slide2.xml", targets)
                self.assertIn("slides/slide3.xml", targets)

                slide_1 = ET.fromstring(zf.read("ppt/slides/slide1.xml"))
                texts = [node.text for node in slide_1.findall(".//a:t", NS) if node.text]
                self.assertIn("AI presentation operations", texts)
                self.assertIn("May 2026", texts)
                self.assertNotIn("SLIDE title", texts)

                slide_2 = ET.fromstring(zf.read("ppt/slides/slide2.xml"))
                slide_2_text = "\n".join(node.text or "" for node in slide_2.findall(".//a:t", NS))
                self.assertIn("Native build path", slide_2_text)
                self.assertIn("Real template, not recreated HTML", slide_2_text)
                self.assertIn("Sample slides are cloned from the Danone PPTX", slide_2_text)
                self.assertNotIn("DANONE COMPANY BRAND PPT TEMPLATE", slide_2_text)
                self.assertNotIn("If your file is too large", slide_2_text)
                self.assertEqual(len(slide_2.findall(".//p:pic", NS)), 0)
                self.assertEqual(len(slide_2.findall(".//p:cxnSp", NS)), 0)
                shape_names = [
                    node.attrib.get("name", "")
                    for node in slide_2.findall(".//p:cNvPr", NS)
                ]
                self.assertFalse(any("Chevron" in name for name in shape_names))

    def test_chart_or_table_preserves_insight_content(self):
        builder = load_builder()
        plan = [
            {
                "intent": "chart-or-table",
                "content": {
                    "title": "Governance metrics",
                    "chart_or_table": "40% faster first drafts\n3 quality gates",
                    "insight": "INSIGHT SHOULD APPEAR",
                },
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "chart-insight.pptx"
            builder.build_presentation(TEMPLATE, LAYOUT_MAP, plan, out)

            with zipfile.ZipFile(out) as zf:
                slide = ET.fromstring(zf.read("ppt/slides/slide1.xml"))
                text = "\n".join(node.text or "" for node in slide.findall(".//a:t", NS))
                self.assertIn("Governance metrics", text)
                self.assertIn("40% faster first drafts", text)
                self.assertIn("INSIGHT SHOULD APPEAR", text)

    def test_image_native_intents_fail_fast_until_image_replacement_exists(self):
        builder = load_builder()
        plan = [
            {
                "intent": "image-content",
                "content": {
                    "title": "Product proof",
                    "body": "Use real packshot",
                    "image": "assets/product.png",
                },
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "image-native.pptx"
            with self.assertRaisesRegex(NotImplementedError, "HTML fallback"):
                builder.build_presentation(TEMPLATE, LAYOUT_MAP, plan, out)


if __name__ == "__main__":
    unittest.main()
