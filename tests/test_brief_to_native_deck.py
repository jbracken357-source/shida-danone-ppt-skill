import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "brief_to_native_deck.py"
TEMPLATE = ROOT / "Danone Real Templates" / "Standard Danone Template.pptx"
LAYOUT_MAP = ROOT / "templates" / "layout-map.json"

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def load_brief_builder():
    spec = importlib.util.spec_from_file_location("brief_to_native_deck", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BriefToNativeDeckTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            TEMPLATE.exists(),
            f"Real Danone template sample is required for brief-to-native tests: {TEMPLATE}",
        )

    def test_converts_task_description_to_supported_native_plan(self):
        brief_builder = load_brief_builder()

        plan = brief_builder.plan_from_brief(
            "Danone AI knowledge operations",
            """
            Audience: regional leadership team.
            Goal: explain why AI-assisted presentation operations can reduce cycle time.
            Key points: template consistency; reusable governance; editable PowerPoint handoff.
            Metrics: 40% faster first drafts; 3 quality gates; 8 pilot teams.
            Next step: approve a 60-day pilot.
            """,
            slide_count=6,
        )

        self.assertEqual(len(plan), 6)
        self.assertEqual(plan[0]["intent"], "opening-cover")
        self.assertEqual(plan[-1]["intent"], "closing")
        self.assertTrue(
            {slide["intent"] for slide in plan}.issubset(
                {
                    "opening-cover",
                    "contents",
                    "big-message",
                    "two-column",
                    "three-column",
                    "chart-or-table",
                    "closing",
                }
            )
        )
        all_text = "\n".join(str(slide["content"]) for slide in plan)
        self.assertIn("Danone AI knowledge operations", all_text)
        self.assertIn("40% faster first drafts", all_text)
        self.assertIn("approve a 60-day pilot", all_text)

    def test_builds_editable_pptx_directly_from_task_description(self):
        brief_builder = load_brief_builder()

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "brief-native.pptx"
            plan_path = Path(tmp) / "brief-plan.json"
            brief_builder.build_from_brief(
                title="Danone hydration launch readiness",
                brief="Prepare a blue-white Danone corporate deck for a product launch readiness review. Cover consumer insight, channel risks, operating metrics, and a final decision ask.",
                out_pptx=out,
                out_plan=plan_path,
                slide_count=5,
                template=TEMPLATE,
                layout_map=LAYOUT_MAP,
            )

            self.assertTrue(out.exists())
            self.assertTrue(plan_path.exists())
            with zipfile.ZipFile(out) as zf:
                presentation = ET.fromstring(zf.read("ppt/presentation.xml"))
                self.assertEqual(len(presentation.find("p:sldIdLst", NS)), 5)
                text = "\n".join(
                    node.text or ""
                    for name in zf.namelist()
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml")
                    for node in ET.fromstring(zf.read(name)).findall(".//a:t", NS)
                )
                self.assertIn("Danone hydration launch readiness", text)
                self.assertIn("product launch readiness", text)


if __name__ == "__main__":
    unittest.main()
