import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "notes_to_danone_deck.py"
TEMPLATE = ROOT / "Danone Real Templates" / "Standard Danone Template.pptx"
LAYOUT_MAP = ROOT / "templates" / "layout-map.json"

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


SAMPLE_NOTES = """# Danone Science Lab - Hardware x User Pain Point x Product Link

## 场景 1｜Gut Health（肠道健康）

### Target User
- 普通消费者
- 亚健康人群

### User Pain Points
- 不知道自己的肠道是否正常
- 吃了对肠道好的产品，但不知道有没有效果

### Hardware (Object)
**TOTO Neorest LS-W / AS-W**

### Collected Data
- 粪便形态（Bristol 1-7）
- 颜色

### Interpreted Indicators
- Gut Health Score
- 排便节律稳定性

### Link to Danone Products
- Activia / Alpro / 肠道健康相关乳制品与植物基产品

### Core Message
> 健康的第一步，不是检测一次，而是每天被理解。

---

## 场景 2｜Physical & Recovery Performance（运动与恢复）

### User Pain Points
- 补水、补电解质完全靠经验或感觉

### Hardware (Object)
**AbsolutSweat P1 智能汗液分析系统**

### Collected Data
- 钠离子（Na+）
- 钾离子（K+）

### Interpreted Indicators
- Hydration ID（水合类型）
- 电解质流失等级

### Link to Danone Products
- Danone 电解质饮品 / 功能性饮用水

### Core Message
> 你不是不自律，只是一直在错误地补给。

---

## 场景 3｜Clinical Nutrition / Tube Feeding（管饲营养）

### User Pain Points
- 管饲后不知道身体是否真正吸收

### Hardware (Object)
**Clinical Nutrition Monitoring Station**

### Collected Data
- 体重趋势
- 骨骼肌量变化

### Interpreted Indicators
- Nutrition Adequacy Score
- Recovery Readiness

### Link to Danone Products
- Nutricia Nutrison 管饲全营养系列

### Core Message
> 这不是喂进去多少，而是身体真正用上了多少。

### 总体叙事统一句式（给老板用）
- Gut Health：**Daily signals**
- Physical & Recovery Performance：**Real-time loss**
- Clinical Nutrition / Tube Feeding：**Verified recovery**

### 总结一句
> Danone 不只是提供营养，而是让营养被数据证明。

### Show Case 结构（展厅用）
1. Why we measure - Objective & Pain point
2. How we see the invisible - DHT making the invisible data visible
3. What the body is telling you - Actual insights and animation
4. What you can do next - link to Danone Products
5. What you take home - A lifestyle report
"""


def load_notes_builder():
    spec = importlib.util.spec_from_file_location("notes_to_danone_deck", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NotesToDanoneDeckTest(unittest.TestCase):
    def test_parses_structured_scenarios_without_markdown_artifacts(self):
        builder = load_notes_builder()

        title, scenarios, showcase_flow, summary = builder.parse_notes(SAMPLE_NOTES)
        plan = builder.plan_from_notes(title, scenarios, showcase_flow, summary)

        self.assertEqual(len(scenarios), 3)
        self.assertEqual(len(plan), 6)
        all_text = "\n".join(str(slide["content"]) for slide in plan)
        self.assertIn("Danone Science Lab", all_text)
        self.assertIn("TOTO Neorest", all_text)
        self.assertIn("Hydration ID", all_text)
        self.assertIn("Nutricia Nutrison", all_text)
        self.assertIn("Real-time loss", all_text)
        self.assertIn("Verified recovery", all_text)
        self.assertNotIn("数据用于解释", all_text)
        self.assertNotIn("###", all_text)
        self.assertNotIn("**", all_text)
        self.assertEqual(plan[1]["intent"], "big-message")
        self.assertLessEqual(len(plan[-1]["content"]["title"]), 64)

    def test_builds_html_deck_and_native_pptx_from_notes(self):
        builder = load_notes_builder()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            notes = tmp_path / "notes.md"
            notes.write_text(SAMPLE_NOTES, encoding="utf-8")
            out_dir = tmp_path / "deck"
            pptx = tmp_path / "deck-native.pptx"
            plan = tmp_path / "plan.json"

            builder.build_deck(
                notes_file=notes,
                out_dir=out_dir,
                native_pptx=pptx,
                out_plan=plan,
                template=TEMPLATE,
                layout_map=LAYOUT_MAP,
            )

            self.assertTrue((out_dir / "index.html").exists())
            self.assertEqual(len(list((out_dir / "slides").glob("*.html"))), 6)
            self.assertTrue((out_dir / "shared" / "tokens.css").exists())
            self.assertIn(".slide-blue", (out_dir / "shared" / "tokens.css").read_text(encoding="utf-8"))
            self.assertTrue(pptx.exists())
            self.assertTrue(plan.exists())

            with zipfile.ZipFile(pptx) as zf:
                presentation = ET.fromstring(zf.read("ppt/presentation.xml"))
                self.assertEqual(len(presentation.find("p:sldIdLst", NS)), 6)
                text = "\n".join(
                    node.text or ""
                    for name in zf.namelist()
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml")
                    for node in ET.fromstring(zf.read(name)).findall(".//a:t", NS)
                )
                self.assertIn("Three measurable nutrition journeys", text)
                self.assertIn("Make nutrition measurable", text)


if __name__ == "__main__":
    unittest.main()
