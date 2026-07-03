#!/usr/bin/env python3
"""
配置界面页面 - 按标题级别组织的简洁配置界面
"""

import re
import uuid
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, 
    QGroupBox, QFrame, QLabel, QSizePolicy, QSpacerItem, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    ScrollArea, PrimaryPushButton, PushButton, TransparentPushButton,
    LineEdit, ComboBox, EditableComboBox, BodyLabel, StrongBodyLabel, TitleLabel,
    CardWidget, CheckBox, TextEdit, FluentIcon as FIF, InfoBar, 
    InfoBarPosition, MessageBox, SubtitleLabel, CaptionLabel,
    Pivot, qconfig, setTheme, Theme, isDarkTheme, ExpandLayout,
    setCustomStyleSheet, HeaderCardWidget, IconWidget
)

from ..config import (
    RECOGNITION_TARGET_LABELS,
    SEGMENT_DELIMITER_OPTIONS,
    RecognitionRule,
    user_config_manager,
    StyleConfig,
    RegexPattern,
)


class BodyClickableComboBox(ComboBox):
    """点击下拉框任意位置都展开菜单"""

    def _show_menu_from_body_click(self):
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        if hasattr(self, '_showComboMenu'):
            self._showComboMenu()
        elif hasattr(self, 'showMenu'):
            self.showMenu()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._show_menu_from_body_click()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class BodyClickableEditableComboBox(EditableComboBox):
    """点击可编辑下拉框任意位置都展开菜单"""

    def _show_menu_from_body_click(self):
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        if hasattr(self, '_showComboMenu'):
            self._showComboMenu()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._show_menu_from_body_click()
            event.accept()
            return
        super().mouseReleaseEvent(event)


@dataclass(frozen=True)
class RuleTemplate:
    """面向用户的规则模板，最终仍生成底层正则表达式"""

    id: str
    label: str
    sample: str
    pattern: str = ""
    placeholder: str = ""
    parameter_required: bool = False


ADVANCED_RULE_TEMPLATE = RuleTemplate(
    id="advanced",
    label="高级正则",
    sample="自定义表达式",
    placeholder="输入正则表达式",
)

RULE_TEMPLATES = {
    'h1': [
        RuleTemplate("chapter", "第 X 章", "第一章", r"^第[一二三四五六七八九十\d]+章"),
        RuleTemplate("exact_text", "固定文本", "前言", parameter_required=True, placeholder="前言"),
    ],
    'h2': [
        RuleTemplate("section", "第 X 节", "第一节", r"^第[一二三四五六七八九十\d]+节"),
        RuleTemplate("cn_list", "一、二、三、", "一、基本情况", r"^[一二三四五六七八九十]+、"),
        RuleTemplate("exact_text", "固定文本", "结语", parameter_required=True, placeholder="结语"),
    ],
    'h3': [
        RuleTemplate("bracket_number", "（一）（二）", "（一）政策支持", r"^（[一二三四五六七八九十\d]+）"),
        RuleTemplate("exact_text", "固定文本", "补充说明", parameter_required=True, placeholder="补充说明"),
    ],
    'special_format': [
        RuleTemplate("bracket_sentence", "（一）到句号", "（一）政策支持。正文", r"^（([一二三四五六七八九十\d]+)）([^。]+。)(.*)"),
        RuleTemplate("first_sentence", "特殊句式到句号", "一是产业扩大。正文", r"^([一二三四五六七八九十\d]+[是的][^。]*。)(.*)"),
        RuleTemplate("colon_title", "冒号前重点", "技术创新能力：正文", r"^([^：]*：)(.*)"),
    ],
}

FONT_FAMILY_OPTIONS = [
    "方正小标宋_GBK",
    "方正黑体_GBK",
    "方正楷体_GBK",
    "方正仿宋_GBK",
    "宋体",
    "黑体",
    "楷体",
    "仿宋",
]

FONT_SIZE_OPTIONS = [
    ("小二 18pt", "18.0000pt"),
    ("三号 16pt", "16.0000pt"),
    ("四号 14pt", "14.0000pt"),
    ("小四 12pt", "12.0000pt"),
]

FONT_WEIGHT_OPTIONS = [
    ("常规", "normal"),
    ("加粗", "bold"),
]

ALIGNMENT_OPTIONS = [
    ("左对齐", "left"),
    ("居中", "center"),
    ("右对齐", "right"),
    ("两端对齐", "justify"),
]

TEXT_INDENT_OPTIONS = [
    ("无缩进", "0.0000pt"),
    ("首行缩进 2 字符", "36.0000pt"),
]


class TitleLevelCard(CardWidget):
    """标题级别配置卡片 - 包含样式和匹配规则"""
    
    config_changed = pyqtSignal(str)  # level
    
    def __init__(self, level: str, title: str, parent=None):
        super().__init__(parent)
        self.level = level
        self.title = title
        self.config = user_config_manager.get_config(level)
        self.rule_widgets = []
        
        self.setup_ui()
        self.load_config()
        self.apply_card_style()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)
        
        # 标题 - 使用 HeaderCardWidget 替代
        # 根据级别选择不同图标
        icon_map = {
            'h1': FIF.LABEL,
            'h2': FIF.TAG,  
            'h3': FIF.BOOK_SHELF,
            'normal': FIF.DOCUMENT,
            'special_format': FIF.PALETTE
        }
        
        title_row = QWidget(self)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        icon_widget = IconWidget(icon_map.get(self.level, FIF.SETTING), self)
        icon_widget.setFixedSize(20, 20)
        title_layout.addWidget(icon_widget)

        title_label = SubtitleLabel(self.title, self)
        title_layout.addWidget(title_label)

        description_label = CaptionLabel("样式设置", self)
        description_label.setStyleSheet("color: #777777;")
        title_layout.addWidget(description_label)
        title_layout.addStretch()
        layout.addWidget(title_row)
        
        # 样式配置区域
        style_group = self.create_style_section()
        layout.addWidget(style_group)
        
        layout.addStretch()

    def _set_combo_text(self, combo: ComboBox, value: str):
        """设置可编辑下拉框文本"""
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        elif hasattr(combo, 'setText'):
            combo.setText(value)

    def _set_mapped_combo(self, combo: ComboBox, options: list[tuple[str, str]], value: str):
        """按保存值设置映射下拉框"""
        for index, (_, option_value) in enumerate(options):
            if option_value == value:
                combo.setCurrentIndex(index)
                return
        if hasattr(combo, 'setText'):
            combo.setText(value)

    def _combo_text(self, combo: ComboBox) -> str:
        """读取下拉框当前文本"""
        return combo.currentText().strip()

    def _mapped_combo_value(self, combo: ComboBox, options: list[tuple[str, str]]) -> str:
        """读取映射下拉框保存值"""
        current_text = combo.currentText().strip()
        for label, value in options:
            if current_text == label:
                return value
        return current_text

    def _template_options(self) -> list[RuleTemplate]:
        """获取当前级别可用规则模板"""
        return [*RULE_TEMPLATES.get(self.level, []), ADVANCED_RULE_TEMPLATE]
    
    def create_style_section(self):
        """创建样式配置区域"""
        group = QFrame(self)
        group.setObjectName("ConfigSection")

        section_layout = QVBoxLayout(group)
        section_layout.setContentsMargins(14, 12, 14, 12)
        section_layout.setSpacing(8)
        section_layout.addWidget(StrongBodyLabel("样式设置", group))

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(12)
        grid_layout.setVerticalSpacing(8)
        
        # 第一行：字体设置
        grid_layout.addWidget(BodyLabel("字体"), 0, 0)
        self.font_family_edit = BodyClickableEditableComboBox()
        self.font_family_edit.addItems(FONT_FAMILY_OPTIONS)
        self.font_family_edit.setMinimumWidth(150)
        grid_layout.addWidget(self.font_family_edit, 0, 1)
        
        grid_layout.addWidget(BodyLabel("字号"), 0, 2)
        self.font_size_edit = BodyClickableEditableComboBox()
        self.font_size_edit.addItems([label for label, _ in FONT_SIZE_OPTIONS])
        self.font_size_edit.setMinimumWidth(110)
        grid_layout.addWidget(self.font_size_edit, 0, 3)
        
        # 第二行：样式设置
        grid_layout.addWidget(BodyLabel("粗细"), 1, 0)
        self.font_weight_combo = BodyClickableComboBox()
        self.font_weight_combo.addItems([label for label, _ in FONT_WEIGHT_OPTIONS])
        self.font_weight_combo.setMinimumWidth(110)
        grid_layout.addWidget(self.font_weight_combo, 1, 1)
        
        grid_layout.addWidget(BodyLabel("对齐"), 1, 2)
        self.alignment_combo = BodyClickableComboBox()
        self.alignment_combo.addItems([label for label, _ in ALIGNMENT_OPTIONS])
        self.alignment_combo.setMinimumWidth(110)
        grid_layout.addWidget(self.alignment_combo, 1, 3)
        
        # 第三行：首行缩进（仅对正文显示）
        if self.level == 'normal':
            grid_layout.addWidget(BodyLabel("首行缩进"), 2, 0)
            self.text_indent_edit = BodyClickableEditableComboBox()
            self.text_indent_edit.addItems([label for label, _ in TEXT_INDENT_OPTIONS])
            self.text_indent_edit.setMinimumWidth(140)
            grid_layout.addWidget(self.text_indent_edit, 2, 1)
        
        # 设置列拉伸
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(3, 1)
        
        section_layout.addWidget(grid_widget)
        
        return group
    
    def create_rules_section(self):
        """创建匹配规则区域"""
        group = QFrame(self)
        group.setObjectName("ConfigSection")

        section_layout = QVBoxLayout(group)
        section_layout.setContentsMargins(14, 12, 14, 12)
        section_layout.setSpacing(8)
        
        # 添加规则按钮和说明
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        header_layout.addWidget(StrongBodyLabel("识别规则", group))
        
        rule_count = len(self.config.patterns) if self.config else 0
        self.rule_count_label = CaptionLabel(f"已配置 {rule_count} 条规则")
        header_layout.addWidget(self.rule_count_label)
        header_layout.addStretch()
        
        self.add_rule_button = PrimaryPushButton("从模板添加")
        self.add_rule_button.setIcon(FIF.ADD)
        self.add_rule_button.setFixedSize(128, 30)
        self.add_rule_button.clicked.connect(self.add_rule)
        header_layout.addWidget(self.add_rule_button)
        
        section_layout.addWidget(header_container)
        
        # 规则列表容器
        self.rules_container = QWidget()
        self.rules_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rules_layout = QVBoxLayout(self.rules_container)
        self.rules_layout.setContentsMargins(0, 0, 0, 0)
        self.rules_layout.setSpacing(8)
        self.rules_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        section_layout.addWidget(self.rules_container, 1)
        
        return group

    def _template_by_id(self, template_id: str) -> RuleTemplate:
        """按模板ID获取规则模板"""
        for template in self._template_options():
            if template.id == template_id:
                return template
        return ADVANCED_RULE_TEMPLATE

    def _update_rule_count_label(self):
        """更新规则数量提示"""
        if not hasattr(self, 'rule_count_label'):
            return
        count = len([widget for widget in self.rule_widgets if widget.pattern.pattern.strip()])
        self.rule_count_label.setText(f"已配置 {count} 条规则")

    def _literal_from_exact_pattern(self, pattern: str) -> str:
        """从简单精确匹配正则提取文本"""
        if not pattern.startswith("^") or not pattern.endswith("$"):
            return ""
        literal = pattern[1:-1]
        if re.search(r"(?<!\\)[\[\]\(\)\+\*\?\|\{\}]", literal):
            return ""
        return re.sub(r"\\(.)", r"\1", literal)

    def _detect_rule_template(self, pattern: RegexPattern) -> tuple[str, str]:
        """识别已有正则对应的模板"""
        for template in RULE_TEMPLATES.get(self.level, []):
            if template.pattern and pattern.pattern == template.pattern:
                return template.id, ""

        exact_text = self._literal_from_exact_pattern(pattern.pattern)
        if exact_text and any(template.id == "exact_text" for template in RULE_TEMPLATES.get(self.level, [])):
            return "exact_text", exact_text

        return "advanced", pattern.pattern

    def _build_pattern_from_template(self, template_id: str, parameter: str, raw_pattern: str) -> str:
        """由用户可见模板生成底层正则"""
        template = self._template_by_id(template_id)
        if template.id == "advanced":
            return raw_pattern.strip()
        if template.id == "exact_text":
            value = parameter.strip() or template.placeholder
            return f"^{re.escape(value)}$"
        return template.pattern

    def _set_rule_pattern_text(self, widget: QWidget, pattern: str):
        """更新规则正则显示，避免触发递归保存"""
        widget.pattern_edit.blockSignals(True)
        widget.pattern_edit.setText(pattern)
        widget.pattern_edit.blockSignals(False)

    def _update_rule_editor_state(self, widget: QWidget):
        """根据规则类型更新输入状态"""
        template_id = widget.template_ids[widget.type_combo.currentIndex()]
        template = self._template_by_id(template_id)

        widget.parameter_edit.setEnabled(template.parameter_required)
        widget.parameter_edit.setVisible(template.parameter_required)
        widget.parameter_edit.setPlaceholderText(template.placeholder or template.sample)
        widget.pattern_edit.setReadOnly(template.id != "advanced")
        widget.pattern_edit.setVisible(template.id == "advanced")
        widget.pattern_edit.setPlaceholderText(template.placeholder if template.id == "advanced" else "自动生成")

        if template.id != "advanced":
            self._set_rule_pattern_text(
                widget,
                self._build_pattern_from_template(template.id, widget.parameter_edit.text(), widget.pattern.pattern)
            )

    def _sync_rule_widget(self, widget: QWidget):
        """从控件状态同步到 RegexPattern"""
        template_id = widget.template_ids[widget.type_combo.currentIndex()]
        template = self._template_by_id(template_id)
        raw_pattern = widget.pattern_edit.text()
        pattern_text = self._build_pattern_from_template(template.id, widget.parameter_edit.text(), raw_pattern)

        widget.pattern.enabled = widget.enabled_checkbox.isChecked()
        widget.pattern.name = widget.name_edit.text().strip() or template.label
        widget.pattern.pattern = pattern_text
        widget.pattern.description = template.sample

        if widget.pattern_edit.text() != pattern_text:
            self._set_rule_pattern_text(widget, pattern_text)

    def _update_rule_test_result(self, widget: QWidget):
        """更新单条规则测试结果"""
        sample = widget.test_edit.text().strip()
        pattern = widget.pattern_edit.text().strip()

        if not sample or not pattern:
            widget.test_result.setText("")
            return

        try:
            matched = re.match(pattern, sample) is not None
        except re.error as exc:
            widget.test_result.setText(f"规则错误: {exc}")
            widget.test_result.setStyleSheet("color: #e74c3c;")
            return

        if matched:
            widget.test_result.setText("匹配")
            widget.test_result.setStyleSheet("color: #16a34a;")
        else:
            widget.test_result.setText("不匹配")
            widget.test_result.setStyleSheet("color: #888888;")
    
    def create_rule_widget(self, pattern: RegexPattern):
        """创建单个规则组件"""
        rule_widget = QFrame()
        rule_widget.setObjectName("RuleWidget")
        rule_widget.setMinimumHeight(54)
        rule_widget.setMaximumHeight(60)
        
        layout = QHBoxLayout(rule_widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        # 启用复选框
        enabled_checkbox = CheckBox()
        enabled_checkbox.setChecked(pattern.enabled)
        enabled_checkbox.setToolTip("启用规则")
        enabled_checkbox.setFixedWidth(26)
        layout.addWidget(enabled_checkbox)
        
        # 规则名称
        name_edit = LineEdit()
        name_edit.setText(pattern.name)
        name_edit.setPlaceholderText("规则名称")
        name_edit.setFixedWidth(132)
        layout.addWidget(name_edit)

        template_id, parameter = self._detect_rule_template(pattern)
        template_options = self._template_options()
        template_ids = [template.id for template in template_options]

        type_combo = BodyClickableComboBox()
        type_combo.addItems([template.label for template in template_options])
        type_combo.setFixedWidth(140)
        if template_id in template_ids:
            type_combo.setCurrentIndex(template_ids.index(template_id))
        layout.addWidget(type_combo)

        parameter_edit = LineEdit()
        parameter_edit.setText(parameter if template_id == "exact_text" else "")
        parameter_edit.setPlaceholderText("匹配文本")
        parameter_edit.setFixedWidth(150)
        layout.addWidget(parameter_edit)

        pattern_edit = LineEdit()
        pattern_edit.setText(pattern.pattern)
        pattern_edit.setPlaceholderText("生成的正则表达式")
        pattern_edit.setMinimumWidth(200)
        pattern_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(pattern_edit)

        test_edit = LineEdit()
        test_edit.setPlaceholderText("测试文本")
        test_edit.setMinimumWidth(150)
        test_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(test_edit)

        test_result = CaptionLabel("")
        test_result.setFixedWidth(66)
        layout.addWidget(test_result)
        
        # 删除按钮
        remove_button = TransparentPushButton()
        remove_button.setIcon(FIF.DELETE)
        remove_button.setFixedSize(32, 30)
        remove_button.setToolTip("删除规则")
        self.update_remove_button_style(remove_button)
        layout.addWidget(remove_button)
        
        # 为规则组件添加样式
        self.apply_rule_widget_style(rule_widget)
        
        # 保存组件引用和数据
        rule_widget.pattern = pattern
        rule_widget.enabled_checkbox = enabled_checkbox
        rule_widget.name_edit = name_edit
        rule_widget.type_combo = type_combo
        rule_widget.template_ids = template_ids
        rule_widget.parameter_edit = parameter_edit
        rule_widget.pattern_edit = pattern_edit
        rule_widget.test_edit = test_edit
        rule_widget.test_result = test_result
        rule_widget.remove_button = remove_button
        
        # 连接信号
        enabled_checkbox.stateChanged.connect(lambda *_: self.on_rule_changed())
        name_edit.textChanged.connect(lambda *_: self.on_rule_changed())
        type_combo.currentIndexChanged.connect(lambda *_: self.on_rule_changed())
        parameter_edit.textChanged.connect(lambda *_: self.on_rule_changed())
        pattern_edit.textChanged.connect(lambda *_: self.on_rule_changed())
        test_edit.textChanged.connect(lambda *_: self._update_rule_test_result(rule_widget))
        remove_button.clicked.connect(lambda: self.remove_rule(rule_widget))

        self._update_rule_editor_state(rule_widget)
        
        return rule_widget
    
    def update_remove_button_style(self, button):
        """更新删除按钮样式以适应当前主题"""
        # 浅色主题样式 - 更明显的红色按钮
        light_qss = """
            PushButton {
                color: #ffffff;
                background-color: #e74c3c;
                border: 1px solid #c0392b;
                border-radius: 4px;
                font-weight: bold;
            }
            PushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
            PushButton:pressed {
                background-color: #a93226;
                border-color: #922b21;
            }
        """
        
        # 深色主题样式 - 更明显的红色按钮
        dark_qss = """
            PushButton {
                color: #ffffff;
                background-color: #ff6b6b;
                border: 1px solid #ff5252;
                border-radius: 4px;
                font-weight: bold;
            }
            PushButton:hover {
                background-color: #ff5252;
                border-color: #ff3333;
            }
            PushButton:pressed {
                background-color: #ff3333;
                border-color: #ff1111;
            }
        """
        
        # 使用 QFluentWidgets 推荐的方式设置主题自适应样式
        setCustomStyleSheet(button, light_qss, dark_qss)
    
    def apply_rule_widget_style(self, widget):
        """为规则组件应用样式"""
        # 浅色主题样式
        light_qss = """
            QFrame#RuleWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
            }
            QFrame#RuleWidget:hover {
                border-color: #ced4da;
                background-color: #f1f3f4;
            }
        """
        
        # 深色主题样式
        dark_qss = """
            QFrame#RuleWidget {
                background-color: #3c4043;
                border: 1px solid #5f6368;
                border-radius: 6px;
            }
            QFrame#RuleWidget:hover {
                border-color: #8ab4f8;
                background-color: #484a4d;
            }
        """
        
        setCustomStyleSheet(widget, light_qss, dark_qss)
    
    def update_group_box_style(self, group_box):
        """更新群组框样式以适应当前主题"""
        # 浅色主题样式
        light_qss = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid rgba(128, 128, 128, 0.3);
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 6px;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
                color: #333333;
            }
        """
        
        # 深色主题样式
        dark_qss = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid rgba(200, 200, 200, 0.3);
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 6px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
                color: #ffffff;
            }
        """
        
        # 使用 QFluentWidgets 推荐的方式设置主题自适应样式
        setCustomStyleSheet(group_box, light_qss, dark_qss)
    
    def apply_card_style(self):
        """为卡片应用美化样式"""
        light_qss = """
            TitleLevelCard {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                background-color: #ffffff;
            }
            TitleLevelCard QFrame#ConfigSection {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                background-color: #fbfbfc;
            }
        """
        
        dark_qss = """
            TitleLevelCard {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: #2d3748;
            }
            TitleLevelCard QFrame#ConfigSection {
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
                background-color: #263241;
            }
        """
        
        setCustomStyleSheet(self, light_qss, dark_qss)
    
    def apply_title_label_style(self, label):
        """为标题标签应用样式"""
        light_qss = """
            SubtitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px 0px;
            }
        """
        
        dark_qss = """
            SubtitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ecf0f1;
                padding: 5px 0px;
            }
        """
        
        setCustomStyleSheet(label, light_qss, dark_qss)
    
    def load_config(self):
        """加载配置"""
        if not self.config:
            return
        
        # 加载样式配置
        style = self.config.style
        self._set_combo_text(self.font_family_edit, style.font_family)
        self._set_mapped_combo(self.font_size_edit, FONT_SIZE_OPTIONS, style.font_size)
        self._set_mapped_combo(self.font_weight_combo, FONT_WEIGHT_OPTIONS, style.font_weight)
        self._set_mapped_combo(self.alignment_combo, ALIGNMENT_OPTIONS, style.alignment)
        
        # 设置首行缩进（仅正文）
        if self.level == 'normal' and hasattr(self, 'text_indent_edit'):
            self._set_mapped_combo(self.text_indent_edit, TEXT_INDENT_OPTIONS, style.text_indent)
        
    
    def load_rules(self):
        """加载匹配规则"""
        # 清除现有规则
        self.clear_rules()
        
        # 添加配置中的规则
        for pattern in self.config.patterns:
            rule_widget = self.create_rule_widget(pattern)
            self.rule_widgets.append(rule_widget)
            self.rules_layout.addWidget(rule_widget)
        self._update_rule_count_label()
        
    
    def clear_rules(self):
        """清除所有规则组件"""
        for widget in self.rule_widgets:
            widget.deleteLater()
        self.rule_widgets.clear()
    
    def add_rule(self):
        """添加新规则"""
        template = RULE_TEMPLATES.get(self.level, [ADVANCED_RULE_TEMPLATE])[0]
        new_pattern = RegexPattern(
            pattern=template.pattern,
            name=template.label,
            enabled=True,
            description=template.sample
        )
        
        rule_widget = self.create_rule_widget(new_pattern)
        self.rule_widgets.append(rule_widget)
        self.rules_layout.addWidget(rule_widget)
        self.on_rule_changed()
    
    def remove_rule(self, rule_widget):
        """删除规则并保存配置"""
        if rule_widget in self.rule_widgets:
            self.rule_widgets.remove(rule_widget)
            rule_widget.deleteLater()
            
            # 删除规则后立即保存配置
            try:
                self._update_rule_count_label()
                self.save_config_silent()
                print(f"规则已删除并保存，剩余规则数量: {len(self.rule_widgets)}")
            except Exception as e:
                print(f"删除规则后保存配置失败: {e}")
    
    def on_rule_changed(self):
        """规则改变时更新数据并自动保存"""
        for widget in self.rule_widgets:
            self._update_rule_editor_state(widget)
            self._sync_rule_widget(widget)
            self._update_rule_test_result(widget)
        self._update_rule_count_label()
        
        # 实时保存配置变化
        try:
            self.save_config_silent()
        except Exception as e:
            print(f"自动保存配置失败: {e}")
    
    def save_config_silent(self):
        """静默保存配置（不显示提示）"""
        try:
            # 保存样式配置
            style = StyleConfig(
                font_family=self._combo_text(self.font_family_edit),
                font_size=self._mapped_combo_value(self.font_size_edit, FONT_SIZE_OPTIONS),
                font_kerning="1.0000pt",  # 固定值
                font_weight=self._mapped_combo_value(self.font_weight_combo, FONT_WEIGHT_OPTIONS),
                alignment=self._mapped_combo_value(self.alignment_combo, ALIGNMENT_OPTIONS),
                text_indent=(
                    hasattr(self, 'text_indent_edit')
                    and self._mapped_combo_value(self.text_indent_edit, TEXT_INDENT_OPTIONS)
                    or "0.0000pt"
                ),
                description=""
            )
            
            # 识别规则由独立的语义规则页保存；样式页不覆盖旧正则兼容字段。
            user_config_manager.update_level_config(self.level, style, None)
            
            self.config_changed.emit(self.level)
            
        except Exception as e:
            raise e


class RecognitionRulesCard(CardWidget):
    """语义识别规则配置卡片"""

    config_changed = pyqtSignal()

    TARGET_OPTIONS = [
        ("关闭", "disabled"),
        ("一级标题", "h1"),
        ("二级标题", "h2"),
        ("三级标题", "h3"),
        ("特殊格式", "special_format"),
    ]
    TITLE_TARGET_OPTIONS = [
        ("关闭", "disabled"),
        ("一级标题", "h1"),
        ("二级标题", "h2"),
        ("三级标题", "h3"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rule_widgets = []
        self._loading = False
        self.setup_ui()
        self.load_config()
        self.apply_card_style()

    def setup_ui(self):
        """设置识别规则配置界面"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        title_row = QWidget(self)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        icon_widget = IconWidget(FIF.TAG, self)
        icon_widget.setFixedSize(20, 20)
        title_layout.addWidget(icon_widget)

        title_layout.addWidget(SubtitleLabel("识别规则", self))
        title_layout.addStretch()

        self.add_regex_button = PushButton("高级正则", self)
        self.add_regex_button.setIcon(FIF.ADD)
        self.add_regex_button.setFixedSize(112, 30)
        self.add_regex_button.clicked.connect(self.add_advanced_regex_rule)
        title_layout.addWidget(self.add_regex_button)

        layout.addWidget(title_row)

        rules_section = QFrame(self)
        rules_section.setObjectName("ConfigSection")
        rules_layout = QVBoxLayout(rules_section)
        rules_layout.setContentsMargins(12, 10, 12, 10)
        rules_layout.setSpacing(6)
        rules_layout.addWidget(StrongBodyLabel("规则分配", rules_section))

        self.rules_container = QWidget(rules_section)
        self.rules_layout = QVBoxLayout(self.rules_container)
        self.rules_layout.setContentsMargins(0, 0, 0, 0)
        self.rules_layout.setSpacing(6)
        self.rules_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        rules_layout.addWidget(self.rules_container, 1)
        layout.addWidget(rules_section, 1)

        test_section = QFrame(self)
        test_section.setObjectName("ConfigSection")
        test_layout = QVBoxLayout(test_section)
        test_layout.setContentsMargins(12, 10, 12, 10)
        test_layout.setSpacing(6)

        test_header = QWidget(test_section)
        test_header_layout = QHBoxLayout(test_header)
        test_header_layout.setContentsMargins(0, 0, 0, 0)
        test_header_layout.addWidget(StrongBodyLabel("测试文本", test_section))
        test_header_layout.addStretch()
        test_layout.addWidget(test_header)

        self.test_edit = TextEdit(test_section)
        self.test_edit.setPlaceholderText("第一章 总则\n第一节 适用范围\n（一）政策支持")
        self.test_edit.setFixedHeight(70)
        self.test_edit.textChanged.connect(self.refresh_test_results)
        test_layout.addWidget(self.test_edit)

        self.test_result_container = QWidget(test_section)
        self.test_result_layout = QVBoxLayout(self.test_result_container)
        self.test_result_layout.setContentsMargins(0, 0, 0, 0)
        self.test_result_layout.setSpacing(4)
        test_layout.addWidget(self.test_result_container)

        layout.addWidget(test_section)

    def _sample_text(self, rule: RecognitionRule) -> str:
        """获取规则示例文本"""
        sample = rule.params.get("sample", "")
        if sample:
            return str(sample)
        samples = {
            "chapter": "第一章 总则",
            "section": "第一节 基本情况",
            "chinese_list": "一、总体要求",
            "chinese_parentheses": "（一）政策支持",
            "hierarchical_numeric": "1 背景 / 1.1 现状 / 1.1.1 数据来源",
            "arabic_comma": "1、项目背景",
            "arabic_dot": "1. Project background",
            "prefix_symbol": "技术创新能力：正文内容",
            "advanced_regex": str(rule.params.get("pattern", "")) or "自定义正则",
        }
        return samples.get(rule.matcher_type, "")

    def _target_options(self, rule: RecognitionRule) -> list[tuple[str, str]]:
        """按规则类型获取可选目标级别"""
        if rule.matcher_type in {"hierarchical_numeric", "advanced_regex"}:
            return self.TITLE_TARGET_OPTIONS
        return self.TARGET_OPTIONS

    def _target_index(self, target_level: str, options: list[tuple[str, str]] = None) -> int:
        """获取输出级别在下拉框中的位置"""
        target_options = options or self.TARGET_OPTIONS
        for index, (_, value) in enumerate(target_options):
            if value == target_level:
                return index
        return 0

    def _target_value(self, combo: ComboBox) -> str:
        """读取输出级别保存值"""
        target_options = getattr(combo, "target_options", self.TARGET_OPTIONS)
        index = combo.currentIndex()
        if 0 <= index < len(target_options):
            return target_options[index][1]
        return "disabled"

    def _clear_layout(self, layout: QVBoxLayout):
        """清空布局中的组件"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_config(self):
        """加载语义识别规则"""
        self._loading = True
        self._clear_layout(self.rules_layout)
        self.rule_widgets.clear()

        for rule in user_config_manager.get_recognition_rules():
            rule_widget = self.create_rule_widget(rule)
            self.rule_widgets.append(rule_widget)
            self.rules_layout.addWidget(rule_widget)

        self._loading = False
        self.refresh_test_results()

    def create_rule_widget(self, rule: RecognitionRule):
        """创建单条语义规则行"""
        rule_widget = QFrame(self)
        rule_widget.setObjectName("RecognitionRuleRow")
        rule_widget.rule = rule

        outer_layout = QVBoxLayout(rule_widget)
        outer_layout.setContentsMargins(8, 6, 8, 6)
        outer_layout.setSpacing(4)

        row_container = QWidget(rule_widget)
        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        outer_layout.addWidget(row_container)

        info_container = QWidget(rule_widget)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        rule_widget.name_edit = None
        rule_widget.pattern_edit = None

        if rule.matcher_type == "advanced_regex":
            name_edit = LineEdit(rule_widget)
            name_edit.setText(rule.name)
            name_edit.setPlaceholderText("规则名称")
            name_edit.setMinimumWidth(160)
            name_edit.textChanged.connect(lambda *_: self.save_config_silent())
            info_layout.addWidget(name_edit)

            pattern_edit = LineEdit(rule_widget)
            pattern_edit.setText(str(rule.params.get("pattern", "")))
            pattern_edit.setPlaceholderText(r"从行首匹配，例如 ^附录[A-Z]?\s+.+")
            pattern_edit.setMinimumWidth(260)
            pattern_edit.textChanged.connect(lambda *_: self.save_config_silent())
            info_layout.addWidget(pattern_edit)

            rule_widget.name_edit = name_edit
            rule_widget.pattern_edit = pattern_edit
        else:
            info_layout.addWidget(StrongBodyLabel(rule.name, rule_widget))

            sample_label = CaptionLabel(f"示例：{self._sample_text(rule)}", rule_widget)
            sample_label.setStyleSheet("color: #777777;")
            info_layout.addWidget(sample_label)

        row_layout.addWidget(info_container, 1)

        target_label = "起始级别" if rule.matcher_type == "hierarchical_numeric" else "识别为"
        row_layout.addWidget(BodyLabel(target_label, rule_widget))
        target_combo = BodyClickableComboBox(rule_widget)
        target_options = self._target_options(rule)
        target_combo.target_options = target_options
        target_combo.addItems([label for label, _ in target_options])
        target_combo.setFixedWidth(104)
        current_target_level = rule.target_level
        if rule.matcher_type == "hierarchical_numeric":
            current_target_level = str(rule.params.get("start_level") or rule.target_level)
        target_combo.setCurrentIndex(
            self._target_index(current_target_level if rule.enabled else "disabled", target_options)
        )
        target_combo.currentIndexChanged.connect(lambda *_: self.save_config_silent())
        row_layout.addWidget(target_combo)
        rule_widget.target_combo = target_combo

        rule_widget.move_up_button = None
        rule_widget.move_down_button = None
        rule_widget.remove_button = None

        if rule.matcher_type == "advanced_regex":
            move_up_button = TransparentPushButton()
            move_up_button.setIcon(FIF.UP)
            move_up_button.setToolTip("上移")
            move_up_button.setFixedSize(30, 30)
            move_up_button.clicked.connect(lambda: self.move_advanced_regex_rule(rule_widget, -1))
            row_layout.addWidget(move_up_button)

            move_down_button = TransparentPushButton()
            move_down_button.setIcon(FIF.DOWN)
            move_down_button.setToolTip("下移")
            move_down_button.setFixedSize(30, 30)
            move_down_button.clicked.connect(lambda: self.move_advanced_regex_rule(rule_widget, 1))
            row_layout.addWidget(move_down_button)

            remove_button = TransparentPushButton()
            remove_button.setIcon(FIF.DELETE)
            remove_button.setToolTip("删除")
            remove_button.setFixedSize(30, 30)
            remove_button.clicked.connect(lambda: self.remove_advanced_regex_rule(rule_widget))
            row_layout.addWidget(remove_button)

            rule_widget.move_up_button = move_up_button
            rule_widget.move_down_button = move_down_button
            rule_widget.remove_button = remove_button

        rule_widget.delimiter_checks = {}
        rule_widget.custom_delimiter_edit = None

        if rule.matcher_type == "prefix_symbol":
            delimiters_container = QWidget(rule_widget)
            delimiters_layout = QHBoxLayout(delimiters_container)
            delimiters_layout.setContentsMargins(0, 0, 0, 0)
            delimiters_layout.setSpacing(6)
            delimiters_layout.addSpacing(2)

            selected_delimiters = set(rule.params.get("delimiters", []))
            for delimiter in SEGMENT_DELIMITER_OPTIONS:
                checkbox = CheckBox(delimiter, rule_widget)
                checkbox.setChecked(delimiter in selected_delimiters)
                checkbox.stateChanged.connect(lambda *_: self.save_config_silent())
                delimiters_layout.addWidget(checkbox)
                rule_widget.delimiter_checks[delimiter] = checkbox

            custom_edit = LineEdit(rule_widget)
            custom_edit.setPlaceholderText("自定义")
            custom_edit.setText(str(rule.params.get("custom_delimiter", "")))
            custom_edit.setFixedWidth(80)
            custom_edit.textChanged.connect(lambda *_: self.save_config_silent())
            delimiters_layout.addWidget(custom_edit)
            rule_widget.custom_delimiter_edit = custom_edit
            delimiters_layout.addStretch()
            outer_layout.addWidget(delimiters_container)

        return rule_widget

    def add_advanced_regex_rule(self):
        """添加高级正则兜底规则"""
        new_rule = RecognitionRule(
            id=f"advanced_regex_{uuid.uuid4().hex[:8]}",
            name="自定义正则",
            matcher_type="advanced_regex",
            target_level="h3",
            enabled=True,
            priority=len(self.rule_widgets) * 10 + 10,
            params={"pattern": "", "sample": "自定义标题"},
        )
        rule_widget = self.create_rule_widget(new_rule)
        self.rule_widgets.append(rule_widget)
        self.rules_layout.addWidget(rule_widget)
        self.save_config_silent()

    def remove_advanced_regex_rule(self, rule_widget: QWidget):
        """删除高级正则规则"""
        if rule_widget not in self.rule_widgets:
            return
        if rule_widget.rule.matcher_type != "advanced_regex":
            return

        self.rule_widgets.remove(rule_widget)
        rule_widget.deleteLater()
        self.save_config_silent()

    def move_advanced_regex_rule(self, rule_widget: QWidget, direction: int):
        """在高级正则列表内部移动规则"""
        if rule_widget not in self.rule_widgets:
            return
        if rule_widget.rule.matcher_type != "advanced_regex":
            return

        current_index = self.rule_widgets.index(rule_widget)
        candidate_index = current_index + direction
        while 0 <= candidate_index < len(self.rule_widgets):
            candidate = self.rule_widgets[candidate_index]
            if candidate.rule.matcher_type == "advanced_regex":
                self.rule_widgets[current_index], self.rule_widgets[candidate_index] = (
                    self.rule_widgets[candidate_index],
                    self.rule_widgets[current_index],
                )
                self._rebuild_rules_layout()
                self.save_config_silent()
                return
            candidate_index += direction

    def _rebuild_rules_layout(self):
        """按 rule_widgets 顺序重建规则布局"""
        while self.rules_layout.count():
            self.rules_layout.takeAt(0)
        for widget in self.rule_widgets:
            self.rules_layout.addWidget(widget)

    def save_config_silent(self):
        """保存语义识别规则"""
        if self._loading:
            return

        rules = []
        for index, widget in enumerate(self.rule_widgets):
            rule = widget.rule
            target_level = self._target_value(widget.target_combo)
            params = dict(rule.params)
            name = rule.name

            if rule.matcher_type == "prefix_symbol":
                params["delimiters"] = [
                    delimiter for delimiter, checkbox in widget.delimiter_checks.items()
                    if checkbox.isChecked()
                ]
                if widget.custom_delimiter_edit:
                    params["custom_delimiter"] = widget.custom_delimiter_edit.text().strip()
            elif rule.matcher_type == "hierarchical_numeric":
                if target_level in {"h1", "h2", "h3"}:
                    params["start_level"] = target_level
                else:
                    params.setdefault("start_level", "h1")
            elif rule.matcher_type == "advanced_regex":
                if widget.name_edit:
                    name = widget.name_edit.text().strip() or "自定义正则"
                if widget.pattern_edit:
                    params["pattern"] = widget.pattern_edit.text().strip()

            updated_rule = RecognitionRule(
                id=rule.id,
                name=name,
                matcher_type=rule.matcher_type,
                target_level=target_level,
                enabled=target_level != "disabled",
                priority=index * 10 + 10,
                params=params,
            )
            widget.rule = updated_rule
            rules.append(updated_rule)

        user_config_manager.update_recognition_rules(rules)
        self.config_changed.emit()
        self.refresh_test_results()

    def refresh_test_results(self):
        """刷新测试文本的识别结果"""
        if not hasattr(self, 'test_result_layout'):
            return

        self._clear_layout(self.test_result_layout)
        text = self.test_edit.toPlainText().strip() if hasattr(self, 'test_edit') else ""
        if not text:
            empty_label = CaptionLabel("输入测试文本后会显示命中规则", self)
            empty_label.setStyleSheet("color: #888888;")
            self.test_result_layout.addWidget(empty_label)
            return

        enabled_levels = {"h1", "h2", "h3", "special_format"}
        for line_number, line in enumerate([item.strip() for item in text.splitlines() if item.strip()], 1):
            match = user_config_manager.classify_line(line, enabled_levels)
            if match:
                label = RECOGNITION_TARGET_LABELS.get(match.target_level, match.target_level)
                if match.target_level == "special_format" and match.remaining_text:
                    result_text = (
                        f"{line_number}. {label} · {match.rule_name}："
                        f"重点“{match.matched_text}”，正文“{match.remaining_text}”"
                    )
                else:
                    result_text = f"{line_number}. {label} · {match.rule_name}：{line}"
            else:
                result_text = f"{line_number}. 正文 · 未命中规则：{line}"

            result_label = CaptionLabel(result_text, self)
            result_label.setWordWrap(True)
            self.test_result_layout.addWidget(result_label)

    def apply_card_style(self):
        """为识别规则卡片应用样式"""
        light_qss = """
            RecognitionRulesCard {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                background-color: #ffffff;
            }
            RecognitionRulesCard QFrame#ConfigSection {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                background-color: #fbfbfc;
            }
            QFrame#RecognitionRuleRow {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 6px;
                background-color: #ffffff;
            }
        """

        dark_qss = """
            RecognitionRulesCard {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: #2d3748;
            }
            RecognitionRulesCard QFrame#ConfigSection {
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
                background-color: #263241;
            }
            QFrame#RecognitionRuleRow {
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 6px;
                background-color: #1f2937;
            }
        """

        setCustomStyleSheet(self, light_qss, dark_qss)


class StyleOverviewCard(CardWidget):
    """全部文档格式的紧凑样式设置卡片"""

    config_changed = pyqtSignal(str)

    LEVELS = [
        ("h1", "一级标题", FIF.LABEL),
        ("h2", "二级标题", FIF.TAG),
        ("h3", "三级标题", FIF.BOOK_SHELF),
        ("normal", "正文", FIF.DOCUMENT),
        ("special_format", "特殊格式", FIF.PALETTE),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = {}
        self._loading = False
        self.setup_ui()
        self.load_config()
        self.apply_card_style()

    def setup_ui(self):
        """设置样式总表界面"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title_row = QWidget(self)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        icon_widget = IconWidget(FIF.FONT, self)
        icon_widget.setFixedSize(20, 20)
        title_layout.addWidget(icon_widget)
        title_layout.addWidget(SubtitleLabel("格式设置", self))
        title_layout.addStretch()
        layout.addWidget(title_row)

        table_frame = QFrame(self)
        table_frame.setObjectName("StyleTable")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(12, 10, 12, 10)
        table_layout.setSpacing(8)

        for level, title, icon in self.LEVELS:
            style_row = QFrame(table_frame)
            style_row.setObjectName("StyleRow")
            row_layout = QHBoxLayout(style_row)
            row_layout.setContentsMargins(10, 8, 10, 8)
            row_layout.setSpacing(10)

            level_label = self._create_level_label(title, icon, style_row)
            level_label.setFixedWidth(78)
            row_layout.addWidget(level_label)

            controls_widget = QWidget(style_row)
            controls_layout = QGridLayout(controls_widget)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.setHorizontalSpacing(8)
            controls_layout.setVerticalSpacing(6)

            font_family_edit = BodyClickableEditableComboBox(style_row)
            font_family_edit.addItems(FONT_FAMILY_OPTIONS)
            font_family_edit.setMinimumWidth(180)
            font_family_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._add_setting_cell(controls_layout, 0, 0, "字体", font_family_edit, style_row)

            font_size_edit = BodyClickableEditableComboBox(style_row)
            font_size_edit.addItems([label for label, _ in FONT_SIZE_OPTIONS])
            font_size_edit.setMinimumWidth(132)
            self._add_setting_cell(controls_layout, 0, 2, "字号", font_size_edit, style_row)

            font_weight_combo = BodyClickableComboBox(style_row)
            font_weight_combo.addItems([label for label, _ in FONT_WEIGHT_OPTIONS])
            font_weight_combo.setMinimumWidth(84)
            self._add_setting_cell(controls_layout, 1, 0, "粗细", font_weight_combo, style_row)

            alignment_combo = BodyClickableComboBox(style_row)
            alignment_combo.addItems([label for label, _ in ALIGNMENT_OPTIONS])
            alignment_combo.setMinimumWidth(96)
            self._add_setting_cell(controls_layout, 1, 2, "对齐", alignment_combo, style_row)

            text_indent_edit = None
            if level == "normal":
                text_indent_edit = BodyClickableEditableComboBox(style_row)
                text_indent_edit.addItems([label for label, _ in TEXT_INDENT_OPTIONS])
                text_indent_edit.setMinimumWidth(128)
                self._add_setting_cell(controls_layout, 1, 4, "缩进", text_indent_edit, style_row)

            controls_layout.setColumnStretch(1, 2)
            controls_layout.setColumnStretch(3, 1)
            controls_layout.setColumnStretch(5, 1)
            row_layout.addWidget(controls_widget, 1)
            table_layout.addWidget(style_row)

            self.rows[level] = {
                "title": title,
                "font_family": font_family_edit,
                "font_size": font_size_edit,
                "font_weight": font_weight_combo,
                "alignment": alignment_combo,
                "text_indent": text_indent_edit,
            }

            for combo in (
                font_family_edit,
                font_size_edit,
                font_weight_combo,
                alignment_combo,
                text_indent_edit,
            ):
                if combo:
                    combo.currentTextChanged.connect(lambda *_: self.save_config_silent())

        layout.addWidget(table_frame)

    def _add_setting_cell(self, layout: QGridLayout, row: int, column: int, label_text: str, widget, parent):
        """添加一组紧凑的字段标签和控件"""
        label = CaptionLabel(label_text, parent)
        label.setStyleSheet("color: #777777;")
        layout.addWidget(label, row, column)
        layout.addWidget(widget, row, column + 1)

    def _create_level_label(self, title: str, icon, parent):
        """创建格式级别标签"""
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        icon_widget = IconWidget(icon, parent)
        icon_widget.setFixedSize(16, 16)
        layout.addWidget(icon_widget)
        layout.addWidget(BodyLabel(title, parent))
        layout.addStretch()
        return container

    def _set_combo_text(self, combo: ComboBox, value: str):
        """设置下拉框文本"""
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        elif hasattr(combo, 'setText'):
            combo.setText(value)

    def _set_mapped_combo(self, combo: ComboBox, options: list[tuple[str, str]], value: str):
        """按保存值设置映射下拉框"""
        for index, (_, option_value) in enumerate(options):
            if option_value == value:
                combo.setCurrentIndex(index)
                return
        self._set_combo_text(combo, value)

    def _combo_text(self, combo: ComboBox) -> str:
        """读取下拉框当前文本"""
        return combo.currentText().strip()

    def _mapped_combo_value(self, combo: ComboBox, options: list[tuple[str, str]]) -> str:
        """读取映射下拉框保存值"""
        current_text = combo.currentText().strip()
        for label, value in options:
            if current_text == label:
                return value
        return current_text

    def load_config(self):
        """加载全部样式配置"""
        self._loading = True
        for level, widgets in self.rows.items():
            config = user_config_manager.get_config(level)
            style = config.style
            self._set_combo_text(widgets["font_family"], style.font_family)
            self._set_mapped_combo(widgets["font_size"], FONT_SIZE_OPTIONS, style.font_size)
            self._set_mapped_combo(widgets["font_weight"], FONT_WEIGHT_OPTIONS, style.font_weight)
            self._set_mapped_combo(widgets["alignment"], ALIGNMENT_OPTIONS, style.alignment)
            if widgets["text_indent"]:
                self._set_mapped_combo(widgets["text_indent"], TEXT_INDENT_OPTIONS, style.text_indent)
        self._loading = False

    def save_config_silent(self):
        """保存全部样式配置"""
        if self._loading:
            return

        for level, widgets in self.rows.items():
            current_style = user_config_manager.get_config(level).style
            text_indent = current_style.text_indent
            if widgets["text_indent"]:
                text_indent = self._mapped_combo_value(widgets["text_indent"], TEXT_INDENT_OPTIONS)

            style = StyleConfig(
                font_family=self._combo_text(widgets["font_family"]),
                font_size=self._mapped_combo_value(widgets["font_size"], FONT_SIZE_OPTIONS),
                font_kerning=current_style.font_kerning,
                font_weight=self._mapped_combo_value(widgets["font_weight"], FONT_WEIGHT_OPTIONS),
                alignment=self._mapped_combo_value(widgets["alignment"], ALIGNMENT_OPTIONS),
                text_indent=text_indent,
                description=current_style.description,
            )
            user_config_manager.update_level_config(level, style, None)
            self.config_changed.emit(level)

    def apply_card_style(self):
        """为样式总表卡片应用样式"""
        light_qss = """
            StyleOverviewCard {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                background-color: #ffffff;
            }
            StyleOverviewCard QFrame#StyleTable {
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                background-color: #fbfbfc;
            }
            StyleOverviewCard QFrame#StyleRow {
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 6px;
                background-color: #ffffff;
            }
        """

        dark_qss = """
            StyleOverviewCard {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: #2d3748;
            }
            StyleOverviewCard QFrame#StyleTable {
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
                background-color: #263241;
            }
            StyleOverviewCard QFrame#StyleRow {
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 6px;
                background-color: #1f2937;
            }
        """

        setCustomStyleSheet(self, light_qss, dark_qss)


class ConfigInterface(QWidget):
    """配置界面主页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConfigInterface")
        self.setup_ui()
        self.apply_theme_background()
    
    def setup_ui(self):
        """设置主界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)
        
        # 添加页面标题
        page_title = TitleLabel("文档格式配置")
        page_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.apply_page_title_style(page_title)
        layout.addWidget(page_title)

        self.config_panel = CardWidget()
        self.config_panel.setObjectName("ConfigPanel")
        self.config_panel.setBorderRadius(8)
        panel_layout = QVBoxLayout(self.config_panel)
        panel_layout.setContentsMargins(14, 12, 14, 12)
        panel_layout.setSpacing(12)

        body_container = QWidget()
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(12)

        self.nav_buttons = {}
        self.config_stack_keys = []
        self.config_stack = None

        self.rules_card = RecognitionRulesCard()
        self.rules_card.setMinimumWidth(470)
        self.rules_card.config_changed.connect(lambda: self.on_config_changed("recognition_rules"))
        body_layout.addWidget(self.rules_card, 1)

        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        self.style_card = StyleOverviewCard()
        self.style_card.config_changed.connect(self.on_config_changed)
        right_layout.addWidget(self.style_card)

        right_layout.addStretch()
        self.setup_save_button(right_layout)
        body_layout.addWidget(right_column)

        panel_layout.addWidget(body_container, 1)

        self.config_cards = {}
        layout.addWidget(self.config_panel, 1)
        self.apply_panel_style()
        
        self.load_ui_settings()

    def switch_config_section(self, route_key: str):
        """切换配置分类"""
        if route_key not in self.config_stack_keys:
            return

        self.config_stack.setCurrentIndex(self.config_stack_keys.index(route_key))
        for key, button in self.nav_buttons.items():
            button.setProperty("selected", key == route_key)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def apply_panel_style(self):
        """为单面板布局应用样式"""
        light_qss = """
            CardWidget#ConfigPanel {
                background-color: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
            }
            QFrame#TopSettingsBar {
                background-color: #fbfbfc;
                border: 1px solid rgba(0, 0, 0, 0.07);
                border-radius: 8px;
            }
            QFrame#ActionBar {
                background-color: #fbfbfc;
                border: 1px solid rgba(0, 0, 0, 0.07);
                border-radius: 8px;
            }
            QFrame#ThemeBox {
                background-color: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 6px;
            }
        """

        dark_qss = """
            CardWidget#ConfigPanel {
                background-color: #1f2937;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
            }
            QFrame#TopSettingsBar {
                background-color: #263241;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
            }
            QFrame#ActionBar {
                background-color: #263241;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
            }
            QFrame#ThemeBox {
                background-color: #374151;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 6px;
            }
        """

        setCustomStyleSheet(self.config_panel, light_qss, dark_qss)
        
    def apply_page_title_style(self, label):
        """为页面标题应用样式"""
        light_qss = """
            TitleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #1f2937;
                padding: 0px;
                margin: 0px;
            }
        """
        
        dark_qss = """
            TitleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #f9fafb;
                padding: 0px;
                margin: 0px;
            }
        """
        
        setCustomStyleSheet(label, light_qss, dark_qss)
    
    def create_app_settings_section(self):
        """创建应用设置区域"""
        card = QFrame()
        card.setObjectName("TopSettingsBar")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        settings_icon = IconWidget(FIF.SETTING, card)
        settings_icon.setFixedSize(18, 18)
        layout.addWidget(settings_icon)

        layout.addWidget(StrongBodyLabel("界面"))
        layout.addStretch()
        layout.addWidget(BodyLabel("主题"))

        self.theme_combo = BodyClickableComboBox()
        self.theme_combo.addItems(["自动", "浅色", "深色"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.setFixedWidth(92)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        return card
    
    def update_group_box_style(self, group_box):
        """更新群组框样式以适应当前主题"""
        # 浅色主题样式
        light_qss = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid rgba(128, 128, 128, 0.3);
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 6px;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
                color: #333333;
            }
        """
        
        # 深色主题样式
        dark_qss = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid rgba(200, 200, 200, 0.3);
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 6px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
                color: #ffffff;
            }
        """
        
        # 使用 QFluentWidgets 推荐的方式设置主题自适应样式
        setCustomStyleSheet(group_box, light_qss, dark_qss)
    
    def apply_theme_background(self):
        """为配置界面应用主题背景"""
        # 主界面背景样式 - 使用渐变背景
        main_light_qss = """
            ConfigInterface {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                color: #1e293b;
            }
        """
        
        main_dark_qss = """
            ConfigInterface {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                color: #f8fafc;
            }
        """
        
        # 应用主界面样式
        setCustomStyleSheet(self, main_light_qss, main_dark_qss)
    
    
    def apply_title_label_style(self, label):
        """为标题标签应用样式"""
        light_qss = """
            SubtitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px 0px;
            }
        """
        
        dark_qss = """
            SubtitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ecf0f1;
                padding: 5px 0px;
            }
        """
        
        setCustomStyleSheet(label, light_qss, dark_qss)
    
    def apply_scroll_area_style(self):
        """为滚动区域应用特殊样式"""
        if not hasattr(self, 'scroll'):
            return

        # 美化滚动区域样式
        light_qss = """
            QScrollArea {
                background: transparent;
                border: none;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background-color: rgba(0, 0, 0, 0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.3);
            }
        """
        
        dark_qss = """
            QScrollArea {
                background: transparent;
                border: none;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """
        
        setCustomStyleSheet(self.scroll, light_qss, dark_qss)
        # 内容区域保持透明背景
        self.scroll_content.setStyleSheet("QWidget{background: transparent}")
    
    def setup_save_button(self, layout):
        """设置保存按钮"""
        bottom_container = QFrame()
        bottom_container.setObjectName("ActionBar")
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(12, 10, 12, 10)
        bottom_layout.setSpacing(8)

        config_path = user_config_manager.get_config_file_path()
        path_label = CaptionLabel("配置文件")
        path_label.setStyleSheet("color: #888888; font-size: 10px;")
        path_label.setToolTip(config_path)
        path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bottom_layout.addWidget(path_label)

        theme_box = QFrame(bottom_container)
        theme_box.setObjectName("ThemeBox")
        theme_layout = QHBoxLayout(theme_box)
        theme_layout.setContentsMargins(10, 0, 8, 0)
        theme_layout.setSpacing(8)
        theme_box.setFixedHeight(34)
        theme_label = BodyLabel("主题", theme_box)
        theme_layout.addWidget(theme_label)

        self.theme_combo = BodyClickableComboBox(theme_box)
        self.theme_combo.addItems(["自动", "浅色", "深色"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.setFixedWidth(88)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        bottom_layout.addWidget(theme_box)

        export_button = PushButton("导出")
        export_button.setIcon(FIF.UP)
        export_button.setFixedSize(88, 34)
        export_button.clicked.connect(self.export_config)
        bottom_layout.addWidget(export_button)
        
        import_button = PushButton("导入")
        import_button.setIcon(FIF.DOWN)
        import_button.setFixedSize(88, 34)
        import_button.clicked.connect(self.import_config)
        bottom_layout.addWidget(import_button)
        
        save_all_button = PrimaryPushButton("保存")
        save_all_button.setIcon(FIF.SAVE)
        save_all_button.setFixedSize(112, 34)
        save_all_button.clicked.connect(self.save_all_config)
        
        self.apply_save_button_style(save_all_button)
        bottom_layout.addWidget(save_all_button)
        
        layout.addWidget(bottom_container)
    
    def apply_save_button_style(self, button):
        """为保存按钮应用特殊样式"""
        light_qss = """
            PrimaryPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #106ebe);
                border: 1px solid #005a9e;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            PrimaryPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106ebe, stop:1 #005a9e);
            }
            PrimaryPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #004578);
            }
        """
        
        dark_qss = """
            PrimaryPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0066cc, stop:1 #004499);
                border: 1px solid #003366;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            PrimaryPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0080ff, stop:1 #0066cc);
            }
            PrimaryPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004499, stop:1 #003366);
            }
        """
        
        setCustomStyleSheet(button, light_qss, dark_qss)
    
    def on_config_changed(self, level):
        """配置改变时的处理"""
        pass  # 目前不需要特殊处理
    
    def on_theme_changed(self, theme_text):
        """主题改变时的处理"""
        from qfluentwidgets import setTheme, Theme
        
        if theme_text == "浅色":
            setTheme(Theme.LIGHT)
        elif theme_text == "深色":
            setTheme(Theme.DARK)
        else:  # 自动
            setTheme(Theme.AUTO)
            
        InfoBar.success(
            title="主题已切换",
            content=f"已切换到{theme_text}主题",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
    
    def get_title_matching_settings(self):
        """获取标题匹配设置"""
        enabled_targets = user_config_manager.get_enabled_recognition_target_levels()
        if not user_config_manager.get_recognition_rules():
            enabled_targets = {"h1", "h2", "h3", "special_format"}

        return {
            'enable_h1': 'h1' in enabled_targets,
            'enable_h2': 'h2' in enabled_targets,
            'enable_h3': 'h3' in enabled_targets,
            'enable_special': 'special_format' in enabled_targets
        }
    
    def on_title_level_changed(self):
        """标题级别设置改变时的处理"""
        try:
            settings = self.get_title_matching_settings()
            user_config_manager.save_ui_settings(settings)
        except Exception as e:
            print(f"保存标题级别设置失败: {e}")
    
    def load_ui_settings(self):
        """加载界面设置"""
        try:
            settings = user_config_manager.load_ui_settings()
            print(f"界面设置已加载: {settings}")
            
        except Exception as e:
            print(f"加载界面设置失败: {e}")
    
    def save_all_config(self):
        """保存所有配置"""
        try:
            total_rules = 0
            total_levels = 0

            if hasattr(self, 'style_card'):
                self.style_card.save_config_silent()
                total_levels = len(self.style_card.rows)

            if hasattr(self, 'rules_card'):
                self.rules_card.save_config_silent()
                total_rules = len([
                    rule for rule in user_config_manager.get_recognition_rules()
                    if rule.enabled and rule.target_level != "disabled"
                ])

            user_config_manager.save_ui_settings(self.get_title_matching_settings())

            if total_rules > 0:
                content = f"已保存 {total_levels} 个格式样式、{total_rules} 条识别规则"
            else:
                content = f"已保存 {total_levels} 个格式样式"
            
            InfoBar.success(
                title="保存成功",
                content=content,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                title="保存失败",
                content=f"保存配置时出错: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
    
    def create_title_settings_section(self, level: str, title: str, icon):
        """创建标题设置区域（一级标题、二级标题、特殊格式）"""
        card = TitleLevelCard(level, title)
        card.config_changed.connect(self.on_config_changed)
        return card
    
    def create_text_settings_section(self, level: str, title: str, icon):
        """创建文本设置区域（正文）"""
        card = TitleLevelCard(level, title)
        card.config_changed.connect(self.on_config_changed)
        return card
    
    def export_config(self):
        """导出配置到文件"""
        from PyQt6.QtWidgets import QFileDialog
        from ..config import user_config_manager
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出配置文件",
            "textpolish_config.json",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            success = user_config_manager.export_config_to_file(file_path)
            if success:
                InfoBar.success(
                    title="导出成功",
                    content=f"配置已导出到: {file_path}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000,
                    parent=self
                )
            else:
                InfoBar.error(
                    title="导出失败",
                    content="导出配置文件时出错",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000,
                    parent=self
                )
    
    def import_config(self):
        """从文件导入配置"""
        from PyQt6.QtWidgets import QFileDialog
        from ..config import user_config_manager
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入配置文件",
            "",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            # 先确认是否要覆盖当前配置
            reply = MessageBox(
                "确认导入",
                "导入配置将覆盖当前所有设置，是否继续？",
                self
            )
            reply.yesButton.setText("确认导入")
            reply.cancelButton.setText("取消")
            
            if reply.exec():
                success = user_config_manager.import_config_from_file(file_path)
                if success:
                    InfoBar.success(
                        title="导入成功",
                        content="配置已成功导入，请重启应用使配置生效",
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=4000,
                        parent=self
                    )
                    # 刷新配置界面
                    self.refresh_all_configs()
                else:
                    InfoBar.error(
                        title="导入失败",
                        content="导入配置文件时出错，请检查文件格式",
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=3000,
                        parent=self
                    )
    
    def refresh_all_configs(self):
        """刷新所有配置卡片"""
        if hasattr(self, 'style_card'):
            self.style_card.load_config()
        if hasattr(self, 'rules_card'):
            self.rules_card.load_config()
