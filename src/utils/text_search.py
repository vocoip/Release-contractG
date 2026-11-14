#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""文本搜索辅助工具。

统一生成用于模糊搜索的拼音键，避免各 UI 页面各自拼接、逻辑漂移。
"""

from typing import List

from pypinyin import Style, lazy_pinyin


def build_pinyin_keys(text: str) -> List[str]:
    """生成文本的拼音搜索键。

    Args:
        text: 原始文本，允许为 None。

    Returns:
        长度为 3 的列表：[完整拼音, 逐音节首字符, FIRST_LETTER 模式首字母]。
        非中文内容原样参与拼接。
    """
    text = text or ''
    return [
        ''.join(lazy_pinyin(text)),
        ''.join(part[0] for part in lazy_pinyin(text) if part),
        ''.join(lazy_pinyin(text, style=Style.FIRST_LETTER)),
    ]
