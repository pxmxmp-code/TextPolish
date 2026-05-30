#!/usr/bin/env python3
"""
文本处理模块 - 负责清理和预处理输入文本
"""

import re
from typing import Optional

from ..config import PUNCTUATION_MAP


class TextProcessor:
    """文本处理器 - 负责清理和标准化文本格式"""
    
    def __init__(self):
        """初始化文本处理器"""
        self.punctuation_map = PUNCTUATION_MAP
    
    def clean_text(self, text: str) -> str:
        """
        清理文本格式问题
        
        Args:
            text: 原始输入文本
            
        Returns:
            清理后的文本
        """
        if not text.strip():
            return text
        
        # 删除特殊符号
        text = self._remove_special_symbols(text)
        
        # 替换英文标点为中文标点
        text = self._replace_punctuation(text)
        
        # 处理引号
        text = self._process_quotes(text)
        
        # 清理空白字符
        text = self._clean_whitespace(text)
        
        # 清理段落格式
        text = self._clean_paragraphs(text)
        
        return text.strip()
    
    def _remove_special_symbols(self, text: str) -> str:
        """删除各种特殊符号和项目符号"""
        # 删除项目符号·
        text = re.sub(r'·\s*', '', text)
        
        # 删除其他常见的特殊符号
        text = re.sub(r'[•▪▫◦‣⁃]\s*', '', text)  # 各种项目符号
        text = re.sub(r'[▲▼◆◇■□●○]\s*', '', text)  # 几何符号
        
        return text
    
    def _replace_punctuation(self, text: str) -> str:
        """智能替换英文标点为中文标点"""
        for en_punct, cn_punct in self.punctuation_map.items():
            # 检查标点前后是否有中文字符
            pattern = r'([\u4e00-\u9fff])\s*' + re.escape(en_punct) + r'\s*([\u4e00-\u9fff])'
            text = re.sub(pattern, r'\1' + cn_punct + r'\2', text)
            
            # 处理行首和行尾的标点
            pattern_start = r'^' + re.escape(en_punct) + r'\s*([\u4e00-\u9fff])'
            text = re.sub(pattern_start, cn_punct + r'\1', text, flags=re.MULTILINE)
            
            pattern_end = r'([\u4e00-\u9fff])\s*' + re.escape(en_punct) + r'$'
            text = re.sub(pattern_end, r'\1' + cn_punct, text, flags=re.MULTILINE)
        
        return text
    
    def _process_quotes(self, text: str) -> str:
        """处理引号：将英文直引号替换为中文引号"""
        processed_lines = []

        for line in text.split('\n'):
            double_quote_open = True
            single_quote_open = True
            chars = []

            for index, char in enumerate(line):
                if char == '"':
                    chars.append('“' if double_quote_open else '”')
                    double_quote_open = not double_quote_open
                    continue

                if char == "'":
                    prev_char = line[index - 1] if index > 0 else ''
                    next_char = line[index + 1] if index + 1 < len(line) else ''

                    if prev_char.isascii() and prev_char.isalpha() and next_char.isascii() and next_char.isalpha():
                        chars.append(char)
                    else:
                        chars.append('‘' if single_quote_open else '’')
                        single_quote_open = not single_quote_open
                    continue

                chars.append(char)

            processed_lines.append(''.join(chars))

        return '\n'.join(processed_lines)
    
    def _clean_whitespace(self, text: str) -> str:
        """清理空白字符"""
        # 暴力删除所有空格（针对中文文本优化）
        text = re.sub(r' +', '', text)  # 删除所有空格
        text = re.sub(r'\t+', '', text)  # 删除所有制表符
        
        # 清理行首行尾空白
        text = re.sub(r'[ \t]+\n', '\n', text)  # 行尾空格
        text = re.sub(r'\n[ \t]+', '\n', text)  # 行首空格
        
        return text
    
    def _clean_paragraphs(self, text: str) -> str:
        """清理段落格式"""
        # 删除段落之间的多余换行
        # 将多个连续换行替换为单个换行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # 多个连续换行替换为两个
        # 进一步优化：将双换行替换为单换行（如果需要更紧凑的格式）
        text = re.sub(r'\n\n+', '\n', text)  # 所有多个换行都替换为单个换行
        
        return text
    
    def get_lines(self, text: str) -> list[str]:
        """
        将文本分割成行，并过滤空行
        
        Args:
            text: 输入文本
            
        Returns:
            非空行的列表
        """
        lines = text.split('\n')
        return [line.strip() for line in lines if line.strip()]
