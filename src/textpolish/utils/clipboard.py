#!/usr/bin/env python3
"""
剪贴板管理模块 - 负责处理剪贴板操作
"""

import html as html_lib

import pyperclip
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QMimeData
from bs4 import BeautifulSoup


class ClipboardManager:
    """剪贴板管理器 - 负责处理各种剪贴板操作"""

    CHINESE_PUNCTUATION_CHARS = "“”‘’—…、。，；：！？（）【】《》"
    CHINESE_PUNCTUATION_STYLE = (
        "font-family:方正仿宋_GBK;"
        "mso-fareast-font-family:方正仿宋_GBK;"
        "mso-ascii-font-family:方正仿宋_GBK;"
        "mso-hansi-font-family:方正仿宋_GBK;"
        "mso-bidi-font-family:方正仿宋_GBK;"
        "mso-ansi-language:ZH-CN;"
    )

    @classmethod
    def _format_plain_text_line(cls, line: str) -> str:
        fragments = []
        plain_buffer = []
        punctuation_buffer = []

        def flush_plain():
            if plain_buffer:
                fragments.append(html_lib.escape("".join(plain_buffer)))
                plain_buffer.clear()

        def flush_punctuation():
            if punctuation_buffer:
                escaped_text = html_lib.escape("".join(punctuation_buffer))
                fragments.append(
                    f'<span lang="ZH-CN" style="{cls.CHINESE_PUNCTUATION_STYLE}">'
                    f"{escaped_text}</span>"
                )
                punctuation_buffer.clear()

        for char in line:
            if char in cls.CHINESE_PUNCTUATION_CHARS:
                flush_plain()
                punctuation_buffer.append(char)
            else:
                flush_punctuation()
                plain_buffer.append(char)

        flush_plain()
        flush_punctuation()
        return "".join(fragments)

    @classmethod
    def _plain_text_to_html(cls, text: str) -> str:
        """生成极简 HTML，让 Word/WPS 粘贴时保留中文引号字体"""
        normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = []

        for line in normalized_text.split("\n"):
            content = cls._format_plain_text_line(line) if line else "&nbsp;"
            paragraphs.append(f'<p class="MsoNormal">{content}</p>')

        body_content = "\n".join(paragraphs)
        return f"""<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style>
p.MsoNormal {{
    margin: 0pt;
    margin-bottom: .0001pt;
    text-align: left;
}}
</style>
</head>
<body>
<!--StartFragment-->
{body_content}
<!--EndFragment-->
</body>
</html>"""
    
    @staticmethod
    def copy_plain_text(text: str) -> None:
        """
        复制纯文本到剪贴板
        
        Args:
            text: 要复制的文本
        """
        app = QApplication.instance()
        if not app:
            pyperclip.copy(text)
            return

        mime_data = QMimeData()
        mime_data.setText(text)
        mime_data.setHtml(ClipboardManager._plain_text_to_html(text))
        app.clipboard().setMimeData(mime_data)
    
    @staticmethod
    def copy_rich_text(html_content: str) -> None:
        """
        复制富文本（HTML）到剪贴板
        
        Args:
            html_content: HTML内容
        """
        app = QApplication.instance()
        if not app:
            raise RuntimeError("QApplication instance not found")
        
        clipboard = app.clipboard()
        
        # 从HTML中提取纯文本，作为备用格式
        plain_text = BeautifulSoup(html_content, 'html.parser').get_text(
            separator='\n', strip=True
        )
        
        mime_data = QMimeData()
        # 关键：同时设置HTML格式和纯文本格式
        mime_data.setHtml(html_content)
        mime_data.setText(plain_text)
        
        clipboard.setMimeData(mime_data)
    
    @staticmethod
    def get_plain_text() -> str:
        """
        从剪贴板获取纯文本
        
        Returns:
            剪贴板中的纯文本
        """
        return pyperclip.paste()
    
    @staticmethod
    def get_html_text() -> str:
        """
        从剪贴板获取HTML文本
        
        Returns:
            剪贴板中的HTML文本
        """
        app = QApplication.instance()
        if not app:
            return ""
        
        clipboard = app.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasHtml():
            return mime_data.html()
        
        return ""
