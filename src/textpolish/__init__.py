#!/usr/bin/env python3
"""
TextPolish - Gemini文本格式修复工具
用于处理Gemini AI回答文本复制到Word后的格式混乱问题
"""

__version__ = "3.3.2"
__author__ = "TextPolish Team"
__description__ = "Gemini文本格式修复工具"

# 导出主要类
from .core.text_processor import TextProcessor
from .core.html_generator import HTMLGenerator
from .ui.main_window import TextPolishWindow
from .ui.main_interface import TextPolishInterface

__all__ = [
    'TextProcessor',
    'HTMLGenerator', 
    'TextPolishWindow',
    'TextPolishInterface'
]
