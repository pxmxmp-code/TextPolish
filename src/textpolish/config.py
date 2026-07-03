#!/usr/bin/env python3
"""
配置文件 - 包含应用程序的所有配置常量
"""

# 应用程序信息
APP_NAME = "TextPolish"
APP_VERSION = "3.3.2"
APP_TITLE = "Gemini文本格式修复工具"
APP_ORGANIZATION = "TextPolish"

# 窗口配置
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
PRIMARY_BUTTON_HEIGHT = 45

# 分割器配置
SPLITTER_SIZES = [400, 200, 400]  # 左侧40%，中间20%，右侧40%
SPLITTER_HANDLE_WIDTH = 1

# 字体配置
FONTS = {
    "preview": {
        "family": "Microsoft YaHei",
        "size": 14
    },
    "ui_label": {
        "size": 10
    },
    "level_label": {
        "size": 9
    }
}

# 旧的静态配置已移除，现在使用用户可配置系统 user_config_manager

# 标点符号替换映射
PUNCTUATION_MAP = {
    ',': '，',
    ';': '；',
    ':': '：', 
    '!': '！',
    '?': '？',
    '(': '（',
    ')': '）',
    '[': '【',
    ']': '】',
}

# 主题颜色配置
THEME_COLORS = {
    "dark": {
        "body": "#ffffff",
        "h1": "#74b9ff",
        "h2": "#a29bfe", 
        "h3": "#fd79a8",
        "special": "#ff7675",
        "normal": "#ddd"
    },
    "light": {
        "body": "#333333",
        "h1": "#2c3e50",
        "h2": "#34495e",
        "h3": "#2980b9", 
        "special": "#e74c3c",
        "normal": "#333"
    }
}

# 消息配置
MESSAGES = {
    "success": {
        "process_complete": "处理完成",
        "copy_success": "复制成功",
        "theme_switched": "主题已切换"
    },
    "warning": {
        "no_input": "请先输入要处理的文本！",
        "no_content": "没有可复制的内容"
    },
    "error": {
        "process_failed": "处理失败",
        "copy_failed": "复制失败",
        "formatted_copy_failed": "格式化复制失败",
        "icon_load_failed": "设置窗口图标失败",
        "app_icon_failed": "设置应用程序图标失败",
        "startup_failed": "程序启动失败"
    },
    "info": {
        "cleared": "已清空",
        "processing": "正在处理...",
        "ready": "就绪"
    }
}

# 图标文件路径配置
ICON_PATHS = {
    "ico": "icon.ico"
}

# HTML模板配置
HTML_NAMESPACE = 'xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40"'


# =============================================
# 新的用户可配置系统
# =============================================

import json
import os
import re
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QSettings


@dataclass
class StyleConfig:
    """标题样式配置"""
    font_family: str = "方正仿宋_GBK"
    font_size: str = "16.0000pt"
    font_kerning: str = "1.0000pt"
    font_weight: str = "normal"
    alignment: str = "left"
    text_indent: str = "0.0000pt"
    description: str = ""


@dataclass
class RegexPattern:
    """正则表达式模式"""
    pattern: str
    name: str
    enabled: bool = True
    description: str = ""


@dataclass
class RecognitionRule:
    """面向用户的语义识别规则"""

    id: str
    name: str
    matcher_type: str
    target_level: str = "disabled"
    enabled: bool = True
    priority: int = 0
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecognitionMatch:
    """单行文本的识别结果"""

    rule_id: str
    rule_name: str
    target_level: str
    matched_text: str
    remaining_text: str = ""


@dataclass
class TitleConfig:
    """标题级别配置"""
    style: StyleConfig
    patterns: List[RegexPattern]


RECOGNITION_TARGET_LABELS = {
    "disabled": "关闭",
    "h1": "一级标题",
    "h2": "二级标题",
    "h3": "三级标题",
    "special_format": "特殊格式",
}

TITLE_LEVEL_SEQUENCE = ("h1", "h2", "h3")
DEFAULT_SEGMENT_DELIMITERS = ["。", "："]
SEGMENT_DELIMITER_OPTIONS = ["。", "：", "；", "，"]


class UserConfigManager:
    """用户配置管理器"""

    CONFIG_LEVELS = {"h1", "h2", "h3", "normal", "special_format"}
    
    def __init__(self):
        # 设置QSettings的组织名称和应用名称，确保配置文件有合适的路径
        self.settings = QSettings(APP_ORGANIZATION, APP_NAME)
        self._config: Dict[str, TitleConfig] = {}
        self._recognition_rules: List[RecognitionRule] = []
        self._load_default_config()
        self.load_config()

    def _default_recognition_rules(self) -> List[RecognitionRule]:
        """默认语义识别规则，用户只需要分配输出级别"""
        return [
            RecognitionRule(
                id="chapter",
                name="第一章 / 第十二章",
                matcher_type="chapter",
                target_level="h1",
                priority=10,
                params={"sample": "第一章 总则"},
            ),
            RecognitionRule(
                id="section",
                name="第一节 / 第三节",
                matcher_type="section",
                target_level="h2",
                priority=20,
                params={"sample": "第一节 基本情况"},
            ),
            RecognitionRule(
                id="chinese_list",
                name="一、二、三、",
                matcher_type="chinese_list",
                target_level="h2",
                priority=30,
                params={"sample": "一、总体要求"},
            ),
            RecognitionRule(
                id="chinese_parentheses",
                name="（一）（二）",
                matcher_type="chinese_parentheses",
                target_level="h3",
                priority=40,
                params={"sample": "（一）政策支持"},
            ),
            RecognitionRule(
                id="hierarchical_numeric",
                name="层级数字编号",
                matcher_type="hierarchical_numeric",
                target_level="h1",
                priority=45,
                params={
                    "sample": "1 背景 / 1.1 现状 / 1.1.1 数据来源",
                    "start_level": "h1",
                },
            ),
            RecognitionRule(
                id="arabic_comma",
                name="1、2、3、",
                matcher_type="arabic_comma",
                target_level="h3",
                priority=50,
                params={"sample": "1、项目背景"},
            ),
            RecognitionRule(
                id="arabic_dot",
                name="1. 2. 3.",
                matcher_type="arabic_dot",
                target_level="h3",
                priority=60,
                params={"sample": "1. Project background"},
            ),
            RecognitionRule(
                id="prefix_symbol",
                name="段首到符号",
                matcher_type="prefix_symbol",
                target_level="special_format",
                priority=70,
                params={
                    "sample": "技术创新能力：正文内容",
                    "delimiters": DEFAULT_SEGMENT_DELIMITERS.copy(),
                    "custom_delimiter": "",
                },
            ),
        ]

    def _coerce_recognition_rule(self, data: Dict[str, Any], fallback: RecognitionRule = None) -> RecognitionRule:
        """把配置字典转换为 RecognitionRule，并兼容缺失字段"""
        base = asdict(fallback) if fallback else {}
        base.update(data)
        params = base.get("params") or {}
        if not isinstance(params, dict):
            params = {}
        return RecognitionRule(
            id=str(base.get("id", "")),
            name=str(base.get("name", "")),
            matcher_type=str(base.get("matcher_type", "")),
            target_level=str(base.get("target_level", "disabled")),
            enabled=bool(base.get("enabled", True)),
            priority=int(base.get("priority", 0)),
            params=params,
        )

    def _recognition_rule_sort_key(self, rule: RecognitionRule) -> tuple[int, int]:
        """内置规则始终先于高级正则，高级正则内部按 priority 排序"""
        is_advanced_regex = rule.matcher_type == "advanced_regex"
        return (1 if is_advanced_regex else 0, rule.priority)

    def _load_recognition_rules_data(self, data: List[Dict[str, Any]]) -> List[RecognitionRule]:
        """加载语义规则，保留默认规则并合并用户选择"""
        defaults = {rule.id: rule for rule in self._default_recognition_rules()}
        loaded: Dict[str, RecognitionRule] = {}

        for raw_rule in data or []:
            if not isinstance(raw_rule, dict):
                continue
            rule_id = str(raw_rule.get("id", ""))
            fallback = defaults.get(rule_id)
            rule = self._coerce_recognition_rule(raw_rule, fallback)
            if rule.id:
                loaded[rule.id] = rule

        for rule_id, default_rule in defaults.items():
            loaded.setdefault(rule_id, default_rule)

        return sorted(loaded.values(), key=self._recognition_rule_sort_key)

    def _migrate_legacy_patterns_to_rules(self) -> List[RecognitionRule]:
        """将旧正则配置尽量映射到新的语义规则"""
        rules = {rule.id: rule for rule in self._default_recognition_rules()}
        pattern_map = {
            r"^第[一二三四五六七八九十\d]+章": "chapter",
            r"^第[一二三四五六七八九十\d]+节": "section",
            r"^[一二三四五六七八九十]+、": "chinese_list",
            r"^（[一二三四五六七八九十\d]+）": "chinese_parentheses",
            r"^（([一二三四五六七八九十\d]+)）([^。]+。)(.*)": "prefix_symbol",
            r"^([^：]*：)(.*)": "prefix_symbol",
        }

        for level, title_config in self._config.items():
            for pattern in title_config.patterns:
                rule_id = pattern_map.get(pattern.pattern)
                if not rule_id or rule_id not in rules:
                    continue
                rule = rules[rule_id]
                rule.target_level = level
                rule.enabled = pattern.enabled

        return sorted(rules.values(), key=self._recognition_rule_sort_key)

    def _serialize_config(self) -> Dict[str, Any]:
        """序列化完整配置，包含旧正则字段和新语义规则字段"""
        config_dict: Dict[str, Any] = {}
        for level, title_config in self._config.items():
            config_dict[level] = {
                'style': asdict(title_config.style),
                'patterns': [asdict(pattern) for pattern in title_config.patterns]
            }
        config_dict['_recognition_rules'] = [asdict(rule) for rule in self._recognition_rules]
        return config_dict
    
    def _load_default_config(self):
        """加载默认配置"""
        # 尝试从应用配置文件加载
        app_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'app_config.json')
        app_config_path = os.path.abspath(app_config_path)
        
        if self.load_from_app_config(app_config_path):
            print("成功从应用配置文件加载默认设置")
            return
        
        # 如果应用配置文件不存在或加载失败，使用代码中的默认配置
        print("使用代码中的默认配置")
        self._config = {
            "h1": TitleConfig(
                style=StyleConfig(
                    font_family="方正小标宋_GBK",
                    font_size="18.0000pt",
                    font_kerning="22.0000pt",
                    font_weight="normal",
                    alignment="center",
                    text_indent="0.0000pt",
                    description="一级标题：第一章第二章到换行符为止，字体：方正小标宋_GBK；字号：小二；格式：居中"
                ),
                patterns=[
                    RegexPattern(
                        pattern=r'^第[一二三四五六七八九十\d]+章',
                        name="章节标题",
                        enabled=True,
                        description="第一章、第二章等"
                    ),
                    RegexPattern(
                        pattern=r'^前言$',
                        name="前言标题",
                        enabled=True,
                        description="前言"
                    )
                ]
            ),
            "h2": TitleConfig(
                style=StyleConfig(
                    font_family="方正黑体_GBK",
                    font_size="16.0000pt",
                    font_kerning="1.0000pt",
                    font_weight="normal",
                    alignment="center",
                    text_indent="0.0000pt",
                    description="二级标题：第一节第二节到换行符为止或者一、二、到换行符为止，字体：方正黑体_GBK；字号：三号；格式：居中"
                ),
                patterns=[
                    RegexPattern(
                        pattern=r'^第[一二三四五六七八九十\d]+节',
                        name="节次标题",
                        enabled=True,
                        description="第一节、第二节等"
                    ),
                    RegexPattern(
                        pattern=r'^[一二三四五六七八九十]+、',
                        name="序号标题",
                        enabled=True,
                        description="一、二、等"
                    )
                ]
            ),
            "h3": TitleConfig(
                style=StyleConfig(
                    font_family="方正楷体_GBK",
                    font_size="16.0000pt",
                    font_kerning="1.0000pt",
                    font_weight="bold",
                    alignment="justify",
                    text_indent="0.0000pt",
                    description="三级标题：段落的开始第一句到句号为止，字体：方正楷体_GBK；字号：三号加粗；格式：两端对齐"
                ),
                patterns=[
                    RegexPattern(
                        pattern=r'^（[一二三四五六七八九十\d]+）',
                        name="带括号序号",
                        enabled=True,
                        description="（一）、（二）等"
                    )
                ]
            ),
            "normal": TitleConfig(
                style=StyleConfig(
                    font_family="方正仿宋_GBK",
                    font_size="16.0000pt",
                    font_kerning="1.0000pt",
                    text_indent="36.0000pt",
                    description="正文：字体：方正仿宋_GBK；字号：三号；格式：首行缩进2字符"
                ),
                patterns=[]
            ),
            "special_format": TitleConfig(
                style=StyleConfig(
                    font_family="方正楷体_GBK",
                    font_size="16.0000pt",
                    font_kerning="1.0000pt",
                    font_weight="bold",
                    alignment="justify",
                    text_indent="0.0000pt",
                    description="特殊格式：特殊句式识别"
                ),
                patterns=[
                    RegexPattern(
                        pattern=r'^（([一二三四五六七八九十\d]+)）([^。]+。)(.*)',
                        name="括号序号标题",
                        enabled=True,
                        description="（一）、（二）等格式到句号"
                    ),
                    RegexPattern(
                        pattern=r'^([一二三四五六七八九十\d]+[是的][^。]*。)(.*)',
                        name="特殊句式到句号",
                        enabled=True,
                        description="第一句到句号"
                    ),
                    RegexPattern(
                        pattern=r'^([^：]*：)(.*)',
                        name="标题到冒号",
                        enabled=True,
                        description="段落开头到冒号"
                    )
                ]
            )
        }
        self._recognition_rules = self._migrate_legacy_patterns_to_rules()
    
    def get_config(self, level: str) -> Optional[TitleConfig]:
        """获取指定级别的配置"""
        return self._config.get(level)
    
    def get_all_configs(self) -> Dict[str, TitleConfig]:
        """获取所有配置"""
        return self._config.copy()
    
    def update_style(self, level: str, style: StyleConfig):
        """更新样式配置"""
        if level in self._config:
            self._config[level].style = style
            self.save_config()
    
    def update_patterns(self, level: str, patterns: List[RegexPattern]):
        """更新正则表达式配置"""
        if level in self._config:
            self._config[level].patterns = patterns
            self.save_config()
    
    def update_level_config(self, level: str, style: StyleConfig = None, patterns: List[RegexPattern] = None):
        """批量更新指定级别的配置（避免重复保存）"""
        if level in self._config:
            if style:
                self._config[level].style = style
            if patterns is not None:
                self._config[level].patterns = patterns
            self.save_config()
    
    def add_pattern(self, level: str, pattern: RegexPattern):
        """添加新的正则表达式"""
        if level in self._config:
            self._config[level].patterns.append(pattern)
            self.save_config()
    
    def remove_pattern(self, level: str, pattern_index: int):
        """移除正则表达式"""
        if level in self._config and 0 <= pattern_index < len(self._config[level].patterns):
            del self._config[level].patterns[pattern_index]
            self.save_config()
    
    def toggle_pattern(self, level: str, pattern_index: int):
        """切换正则表达式启用状态"""
        if level in self._config and 0 <= pattern_index < len(self._config[level].patterns):
            pattern = self._config[level].patterns[pattern_index]
            pattern.enabled = not pattern.enabled
            self.save_config()
    
    def save_config(self):
        """保存配置到QSettings"""
        try:
            # 确保配置目录存在
            import os
            config_file_path = self.settings.fileName()
            config_dir = os.path.dirname(config_file_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                print(f"创建配置目录: {config_dir}")
            
            config_dict = self._serialize_config()
            
            self.settings.setValue("user_config", json.dumps(config_dict, ensure_ascii=False))
            # 强制同步到文件
            self.settings.sync()
            print(f"配置已保存到: {config_file_path}")
            
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        """从QSettings加载配置，如果没有用户配置则使用默认配置"""
        try:
            config_data = self.settings.value("user_config", "")
            if config_data:
                print("加载用户配置...")
                config_dict = json.loads(config_data)
                
                for level, data in config_dict.items():
                    if level in self._config:
                        # 加载样式配置
                        style_data = data.get('style', {})
                        style = StyleConfig(**style_data)
                        
                        # 加载正则表达式配置
                        patterns_data = data.get('patterns', [])
                        patterns = [RegexPattern(**pattern_data) for pattern_data in patterns_data]
                        
                        self._config[level] = TitleConfig(style=style, patterns=patterns)

                rules_data = config_dict.get('_recognition_rules')
                if isinstance(rules_data, list):
                    self._recognition_rules = self._load_recognition_rules_data(rules_data)
                else:
                    self._recognition_rules = self._migrate_legacy_patterns_to_rules()
                
                print(f"用户配置加载成功，共 {len(config_dict)} 个级别")
            else:
                print("未找到用户配置，使用默认配置")
                # 第一次运行时保存默认配置
                if not self._recognition_rules:
                    self._recognition_rules = self._migrate_legacy_patterns_to_rules()
                self.save_config()
                        
        except Exception as e:
            print(f"加载配置失败，使用默认配置: {e}")
            # 发生错误时重新加载默认配置
            self._load_default_config()
    
    def reset_to_default(self):
        """重置为默认配置"""
        self._load_default_config()
        self.save_config()
    
    def get_enabled_patterns(self, level: str) -> List[str]:
        """获取指定级别的启用正则表达式"""
        if level not in self._config:
            return []
        
        return [pattern.pattern for pattern in self._config[level].patterns if pattern.enabled]

    def get_recognition_rules(self) -> List[RecognitionRule]:
        """获取语义识别规则副本"""
        return [
            RecognitionRule(**asdict(rule))
            for rule in sorted(self._recognition_rules, key=self._recognition_rule_sort_key)
        ]

    def update_recognition_rules(self, rules: List[RecognitionRule]):
        """更新语义识别规则"""
        self._recognition_rules = sorted(rules, key=self._recognition_rule_sort_key)
        self.save_config()

    def get_enabled_recognition_target_levels(self) -> set[str]:
        """获取当前启用规则可能输出的标题级别"""
        enabled_targets: set[str] = set()
        for rule in self._recognition_rules:
            if not rule.enabled or rule.target_level == "disabled":
                continue

            if rule.matcher_type == "hierarchical_numeric":
                start_level = self._hierarchical_numeric_start_level(rule)
                start_index = TITLE_LEVEL_SEQUENCE.index(start_level)
                enabled_targets.update(TITLE_LEVEL_SEQUENCE[start_index:])
                continue

            enabled_targets.add(rule.target_level)

        return enabled_targets

    def _hierarchical_numeric_start_level(self, rule: RecognitionRule) -> str:
        """读取层级数字编号的起始标题级别"""
        start_level = str(rule.params.get("start_level") or rule.target_level or "h1")
        if start_level not in TITLE_LEVEL_SEQUENCE:
            return "h1"
        return start_level

    def _hierarchical_numeric_target_level(self, number_text: str, start_level: str) -> str:
        """按编号深度和起始级别计算输出标题级别"""
        start_index = TITLE_LEVEL_SEQUENCE.index(start_level)
        depth = len(number_text.split("."))
        target_index = min(start_index + depth - 1, len(TITLE_LEVEL_SEQUENCE) - 1)
        return TITLE_LEVEL_SEQUENCE[target_index]

    def _match_hierarchical_numeric(self, rule: RecognitionRule, text: str) -> Optional[tuple[str, str, str]]:
        """匹配 1 / 1.1 / 1.1.1 这类已有层级数字编号"""
        number_match = re.match(r"^(?P<number>[1-9]\d{0,2}(?:\.[1-9]\d{0,2})*)(?P<rest>.*)$", text)
        if not number_match:
            return None

        number_text = number_match.group("number")
        rest = number_match.group("rest")
        if not rest:
            return None

        if rest[0].isspace():
            title_text = rest.strip()
        elif rest[0] in {".", "、"}:
            title_text = rest[1:].strip()
        else:
            return None

        if not title_text:
            return None

        start_level = self._hierarchical_numeric_start_level(rule)
        target_level = self._hierarchical_numeric_target_level(number_text, start_level)
        return text, "", target_level

    def _match_recognition_rule(self, rule: RecognitionRule, line: str) -> Optional[tuple[str, str, str]]:
        """执行单条语义规则匹配，返回匹配段和剩余文本"""
        text = line.strip()
        matcher_patterns = {
            "chapter": r"^第[一二三四五六七八九十百千万\d]+章",
            "section": r"^第[一二三四五六七八九十百千万\d]+节",
            "chinese_list": r"^[一二三四五六七八九十百千万]+、",
            "chinese_parentheses": r"^（[一二三四五六七八九十百千万\d]+）",
            "arabic_comma": r"^\d+、",
            "arabic_dot": r"^\d+\.",
        }

        if rule.matcher_type in matcher_patterns:
            return (text, "", rule.target_level) if re.match(matcher_patterns[rule.matcher_type], text) else None

        if rule.matcher_type == "hierarchical_numeric":
            return self._match_hierarchical_numeric(rule, text)

        if rule.matcher_type == "advanced_regex":
            pattern = str(rule.params.get("pattern", "")).strip()
            if not pattern:
                return None
            try:
                return (text, "", rule.target_level) if re.match(pattern, text) else None
            except re.error:
                return None

        if rule.matcher_type == "prefix_symbol":
            delimiters = [
                delimiter for delimiter in rule.params.get("delimiters", [])
                if isinstance(delimiter, str) and delimiter
            ]
            custom_delimiter = str(rule.params.get("custom_delimiter", "")).strip()
            if custom_delimiter and custom_delimiter not in delimiters:
                delimiters.append(custom_delimiter)

            candidates = []
            for delimiter in delimiters:
                index = text.find(delimiter)
                if index > 0:
                    candidates.append((index, delimiter))

            if not candidates:
                return None

            index, delimiter = min(candidates, key=lambda item: item[0])
            end_index = index + len(delimiter)
            return text[:end_index], text[end_index:].strip(), rule.target_level

        return None

    def classify_line(self, line: str, enabled_levels: Optional[set[str]] = None) -> Optional[RecognitionMatch]:
        """按语义规则识别单行文本"""
        for rule in sorted(self._recognition_rules, key=self._recognition_rule_sort_key):
            if not rule.enabled or rule.target_level == "disabled":
                continue
            if (
                enabled_levels is not None
                and rule.matcher_type != "hierarchical_numeric"
                and rule.target_level not in enabled_levels
            ):
                continue

            match = self._match_recognition_rule(rule, line)
            if not match:
                continue

            matched_text, remaining_text, target_level = match
            if enabled_levels is not None and target_level not in enabled_levels:
                continue

            if target_level != "special_format":
                matched_text = line.strip()
                remaining_text = ""

            return RecognitionMatch(
                rule_id=rule.id,
                rule_name=rule.name,
                target_level=target_level,
                matched_text=matched_text,
                remaining_text=remaining_text,
            )

        return None
    
    def get_style_dict(self, level: str) -> Dict:
        """获取指定级别的样式字典（兼容原有格式）"""
        if level not in self._config:
            return {}
        
        style = self._config[level].style
        return asdict(style)
    
    def save_ui_settings(self, settings: Dict):
        """保存界面设置"""
        try:
            self.settings.setValue("ui_settings", json.dumps(settings, ensure_ascii=False))
            self.settings.sync()
            print(f"界面设置已保存: {settings}")
        except Exception as e:
            print(f"保存界面设置失败: {e}")
    
    def load_ui_settings(self) -> Dict:
        """加载界面设置"""
        try:
            settings_data = self.settings.value("ui_settings", "")
            if settings_data:
                return json.loads(settings_data)
            else:
                # 返回默认设置
                return {
                    'enable_h1': True,
                    'enable_h2': True, 
                    'enable_h3': True,
                    'enable_special': True
                }
        except Exception as e:
            print(f"加载界面设置失败: {e}")
            # 返回默认设置
            return {
                'enable_h1': True,
                'enable_h2': True,
                'enable_h3': True, 
                'enable_special': True
            }
    
    def get_config_file_path(self) -> str:
        """获取配置文件的完整路径"""
        return self.settings.fileName()
    
    def export_config_to_file(self, file_path: str):
        """导出配置到指定文件"""
        try:
            config_dict = self._serialize_config()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config_from_file(self, file_path: str):
        """从指定文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            for level, data in config_dict.items():
                if level in self._config:
                    # 加载样式配置
                    style_data = data.get('style', {})
                    style = StyleConfig(**style_data)
                    
                    # 加载正则表达式配置
                    patterns_data = data.get('patterns', [])
                    patterns = [RegexPattern(**pattern_data) for pattern_data in patterns_data]
                    
                    self._config[level] = TitleConfig(style=style, patterns=patterns)

            rules_data = config_dict.get('_recognition_rules')
            if isinstance(rules_data, list):
                self._recognition_rules = self._load_recognition_rules_data(rules_data)
            else:
                self._recognition_rules = self._migrate_legacy_patterns_to_rules()
            
            # 保存到QSettings
            self.save_config()
            return True
            
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def initialize_from_project_config(self, project_config_path: str):
        """从项目配置文件初始化用户配置（仅在首次运行时）"""
        try:
            # 检查是否已有用户配置
            if self.settings.value("user_config", ""):
                return False  # 已有用户配置，不需要初始化
            
            # 从项目配置文件导入
            if os.path.exists(project_config_path):
                print(f"首次运行，从项目配置初始化: {project_config_path}")
                return self.import_config_from_file(project_config_path)
            
            return False
            
        except Exception as e:
            print(f"从项目配置初始化失败: {e}")
            return False
    
    def load_from_app_config(self, app_config_path: str):
        """从合并的应用配置文件加载默认配置"""
        try:
            if os.path.exists(app_config_path):
                with open(app_config_path, 'r', encoding='utf-8') as f:
                    app_config = json.load(f)
                
                # 加载默认用户配置
                default_user_config = app_config.get('default_user_config', {})
                if default_user_config:
                    print(f"从应用配置加载默认设置: {app_config_path}")
                    
                    for level, data in default_user_config.items():
                        if level in self.CONFIG_LEVELS:
                            # 加载样式配置
                            style_data = data.get('style', {})
                            style = StyleConfig(**style_data)
                            
                            # 加载正则表达式配置
                            patterns_data = data.get('patterns', [])
                            patterns = [RegexPattern(**pattern_data) for pattern_data in patterns_data]
                            
                            self._config[level] = TitleConfig(style=style, patterns=patterns)

                    rules_data = app_config.get('default_recognition_rules')
                    if isinstance(rules_data, list):
                        self._recognition_rules = self._load_recognition_rules_data(rules_data)
                    else:
                        self._recognition_rules = self._migrate_legacy_patterns_to_rules()
                    
                    return True
                
        except Exception as e:
            print(f"从应用配置加载失败: {e}")
        
        return False


# 全局配置管理器实例
user_config_manager = UserConfigManager()
