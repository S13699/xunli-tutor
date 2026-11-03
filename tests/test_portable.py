import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PortableBuildTests(unittest.TestCase):
    def setUp(self):
        temp_base = ROOT / ".test-tmp"
        temp_base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_base)
        self.root = Path(self.temp.name)
        self.assertTrue(self.root.resolve().is_relative_to(temp_base.resolve()))
        self.addCleanup(self.temp.cleanup)
        shutil.copytree(ROOT / "plugins", self.root / "plugins")
        shutil.copyfile(ROOT / "LICENSE", self.root / "LICENSE")
        module = ROOT / "tools/build_portable.py"
        self.assertTrue(module.exists(), "Portable builder is missing")
        spec = importlib.util.spec_from_file_location("portable_builder", module)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)

    def test_standalone_skill_keeps_all_references_without_plugin_dependency(self):
        self.builder.build(self.root)
        target = self.root / "skills/learn-with-feedback"
        self.assertTrue((target / "SKILL.md").exists())
        self.assertTrue((target / "references/progress.md").exists())
        self.assertTrue((target / "assets/learning-record.md").exists())
        self.assertTrue((target / "LICENSE").exists())
        self.assertFalse((target / "agents/openai.yaml").exists())
        self.assertFalse((target / "plugin.json").exists())
        skill = (target / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/teaching-protocol.md", skill)
        for line in skill.splitlines():
            self.assertNotIn("../plugins/", line)

    def test_single_file_contains_rules_and_templates_without_local_links(self):
        self.builder.build(self.root)
        text = (self.root / "portable/xunli-tutor.md").read_text(encoding="utf-8")
        self.assertIn("等待用户回答", text)
        self.assertIn("学习记录模板", text)
        self.assertIn("学科", text)
        self.assertNotRegex(text, r"\]\((?:references|assets|\.\.)/")

    def test_check_detects_missing_and_changed_outputs(self):
        self.assertTrue(self.builder.build(self.root, check=True))
        self.builder.build(self.root)
        self.assertEqual([], self.builder.build(self.root, check=True))
        target = self.root / "skills/learn-with-feedback/references/progress.md"
        target.write_text("outdated", encoding="utf-8")
        self.assertIn(target.relative_to(self.root).as_posix(), self.builder.build(self.root, check=True))

    def test_source_change_propagates_and_build_is_repeatable(self):
        source = self.root / "plugins/xunli-tutor/skills/learn-with-feedback/references/teaching-protocol.md"
        source.write_text(source.read_text(encoding="utf-8") + "\n更新后的教学约束。\n", encoding="utf-8")
        self.builder.build(self.root)
        target = self.root / "portable/xunli-tutor.md"
        before = target.read_bytes()
        self.assertIn("更新后的教学约束", before.decode())
        self.builder.build(self.root)
        self.assertEqual(before, target.read_bytes())


if __name__ == "__main__":
    unittest.main()
