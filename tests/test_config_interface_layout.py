import os
import sys
import unittest
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PyQt6.QtWidgets import QApplication

from textpolish.config import RecognitionRule
from textpolish.ui.config_interface import RecognitionRulesCard


class AdvancedRegexLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_advanced_regex_row_is_readable_at_settings_panel_width(self):
        card = RecognitionRulesCard()
        card.setFixedWidth(470)

        while card.rules_layout.count():
            item = card.rules_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        rule = RecognitionRule(
            id="advanced_regex_layout",
            name="自定义正则",
            matcher_type="advanced_regex",
            target_level="h3",
            enabled=True,
            priority=10,
            params={"pattern": r"^附录[A-Z]?\s+.+"},
        )
        row = card.create_rule_widget(rule)
        card.rules_layout.addWidget(row)

        card.show()
        self.app.processEvents()

        self.assertGreaterEqual(row.name_edit.width(), 190)
        self.assertGreaterEqual(row.pattern_edit.width(), 320)
        self.assertEqual("上移", row.move_up_button.text())
        self.assertEqual("下移", row.move_down_button.text())
        self.assertEqual("删除", row.remove_button.text())


if __name__ == "__main__":
    unittest.main()
