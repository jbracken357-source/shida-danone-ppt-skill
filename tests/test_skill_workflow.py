import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
README = ROOT / "README.md"


class SkillWorkflowTest(unittest.TestCase):
    def test_real_template_native_path_precedes_html_fallback(self):
        text = SKILL.read_text(encoding="utf-8")

        native_idx = text.index("正式可编辑 PPTX")
        html_fallback_idx = text.index("HTML→editable fallback")

        self.assertLess(native_idx, html_fallback_idx)
        self.assertIn("不要无条件进入 HTML 多文件管线", text)
        self.assertIn("不要默认用 `scripts/export_deck_pptx.mjs --mode editable` 替代真实模板 native 生成", text)

    def test_no_stale_html_only_workflow_instruction(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertNotIn("本 skill 只用多文件架构", text)
        self.assertNotIn("PDF + PPTX + 可编辑）决定了多文件是唯一可行的架构", text)

    def test_readme_explains_native_pptx_first(self):
        text = README.read_text(encoding="utf-8")

        self.assertIn("正式可编辑 PPTX 走真实模板 native", text)
        self.assertIn("scripts/brief_to_native_deck.py", text)
        self.assertIn("HTML 分支才生成 `shared/tokens.css`", text)
        self.assertIn("python scripts/build_native_pptx.py --plan plan.json --out deck-native.pptx", text)

    def test_skill_explains_brief_to_native_entrypoint(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("用户只给材料描述或任务描述", text)
        self.assertIn("python scripts/brief_to_native_deck.py", text)
        self.assertIn("out-plan", text)

    def test_skill_explains_structured_notes_entrypoint(self):
        text = SKILL.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("DHT Lab / show case 类结构化 notes", text)
        self.assertIn("python scripts/notes_to_danone_deck.py", text)
        self.assertIn("scripts/notes_to_danone_deck.py", readme)
        self.assertIn("deck-editable-parity.pptx", text)
        self.assertIn("deck-editable-parity.pptx", readme)

    def test_skill_notes_libreoffice_output_directory_requirement(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("LibreOffice 转 PDF 前", text)
        self.assertIn("先创建输出目录", text)


if __name__ == "__main__":
    unittest.main()
