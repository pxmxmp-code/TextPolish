import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from textpolish.config import RecognitionRule, user_config_manager


class RecognitionRulesTest(unittest.TestCase):
    def setUp(self):
        self.original_rules = user_config_manager._recognition_rules

    def tearDown(self):
        user_config_manager._recognition_rules = self.original_rules

    def set_rules(self, *rules: RecognitionRule):
        user_config_manager._recognition_rules = list(rules)

    def classify(self, line: str):
        return user_config_manager.classify_line(
            line,
            {"h1", "h2", "h3", "special_format"},
        )

    def hierarchical_rule(self, start_level: str = "h1", priority: int = 10):
        return RecognitionRule(
            id="hierarchical_numeric",
            name="层级数字编号",
            matcher_type="hierarchical_numeric",
            target_level=start_level,
            enabled=True,
            priority=priority,
            params={"start_level": start_level},
        )

    def test_hierarchical_numeric_numbering_maps_depth_to_title_level(self):
        self.set_rules(self.hierarchical_rule("h1"))

        cases = {
            "1 背景": "h1",
            "1. 标题": "h1",
            "1、标题": "h1",
            "1.1 现状": "h2",
            "1.1. 标题": "h2",
            "1.1.1 数据来源": "h3",
            "1.1.1.1 更深层级": "h3",
        }

        for line, expected_level in cases.items():
            with self.subTest(line=line):
                match = self.classify(line)
                self.assertIsNotNone(match)
                self.assertEqual(expected_level, match.target_level)
                self.assertEqual(line, match.matched_text)

    def test_hierarchical_numeric_numbering_can_start_at_second_level(self):
        self.set_rules(self.hierarchical_rule("h2"))

        cases = {
            "1 背景": "h2",
            "1.1 现状": "h3",
            "1.1.1 数据来源": "h3",
        }

        for line, expected_level in cases.items():
            with self.subTest(line=line):
                match = self.classify(line)
                self.assertIsNotNone(match)
                self.assertEqual(expected_level, match.target_level)

    def test_hierarchical_numeric_numbering_requires_title_text(self):
        self.set_rules(self.hierarchical_rule("h1"))

        for line in ("1", "1.", "1.1", "1.1.", "2026.07.03 工作"):
            with self.subTest(line=line):
                self.assertIsNone(self.classify(line))

    def test_hierarchical_numeric_numbering_precedes_legacy_arabic_dot(self):
        self.set_rules(
            self.hierarchical_rule("h1", priority=10),
            RecognitionRule(
                id="arabic_dot",
                name="1. 2. 3.",
                matcher_type="arabic_dot",
                target_level="h3",
                enabled=True,
                priority=20,
                params={},
            ),
        )

        match = self.classify("1. 标题")

        self.assertIsNotNone(match)
        self.assertEqual("h1", match.target_level)
        self.assertEqual("hierarchical_numeric", match.rule_id)

    def test_advanced_regex_is_a_whole_line_fallback_after_builtins(self):
        self.set_rules(
            self.hierarchical_rule("h1", priority=10),
            RecognitionRule(
                id="advanced_regex_custom",
                name="附录标题",
                matcher_type="advanced_regex",
                target_level="h2",
                enabled=True,
                priority=100,
                params={"pattern": r"^附录[A-Z]?\s+.+"},
            ),
            RecognitionRule(
                id="advanced_regex_broad",
                name="宽泛数字规则",
                matcher_type="advanced_regex",
                target_level="h3",
                enabled=True,
                priority=110,
                params={"pattern": r"^\d+\..+"},
            ),
        )

        appendix = self.classify("附录A 补充材料")
        numbered = self.classify("1. 标题")

        self.assertIsNotNone(appendix)
        self.assertEqual("h2", appendix.target_level)
        self.assertEqual("advanced_regex_custom", appendix.rule_id)

        self.assertIsNotNone(numbered)
        self.assertEqual("h1", numbered.target_level)
        self.assertEqual("hierarchical_numeric", numbered.rule_id)

    def test_advanced_regex_cannot_shadow_builtins_with_lower_priority(self):
        self.set_rules(
            RecognitionRule(
                id="advanced_regex_broad",
                name="宽泛数字规则",
                matcher_type="advanced_regex",
                target_level="h3",
                enabled=True,
                priority=1,
                params={"pattern": r"^\d+\..+"},
            ),
            self.hierarchical_rule("h1", priority=10),
        )

        match = self.classify("1. 标题")

        self.assertIsNotNone(match)
        self.assertEqual("h1", match.target_level)
        self.assertEqual("hierarchical_numeric", match.rule_id)

    def test_enabled_targets_include_dynamic_hierarchical_outputs(self):
        self.set_rules(
            self.hierarchical_rule("h2", priority=10),
            RecognitionRule(
                id="prefix_symbol",
                name="段首到符号",
                matcher_type="prefix_symbol",
                target_level="special_format",
                enabled=True,
                priority=20,
                params={"delimiters": ["："]},
            ),
        )

        self.assertEqual(
            {"h2", "h3", "special_format"},
            user_config_manager.get_enabled_recognition_target_levels(),
        )


if __name__ == "__main__":
    unittest.main()
