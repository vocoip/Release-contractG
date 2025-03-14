#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序样式模块
"""

# 主题颜色
PRIMARY_COLOR = "#1976D2"  # 主色调：蓝色
SECONDARY_COLOR = "#03A9F4"  # 次要色调：浅蓝色
SUCCESS_COLOR = "#4CAF50"  # 成功色：绿色
WARNING_COLOR = "#FFC107"  # 警告色：黄色
DANGER_COLOR = "#F44336"  # 危险色：红色
INFO_COLOR = "#2196F3"  # 信息色：蓝色
LIGHT_COLOR = "#F5F5F5"  # 浅色：近白色
DARK_COLOR = "#212121"  # 深色：近黑色
BORDER_COLOR = "#E0E0E0"  # 边框色：浅灰色

# 字体设置
FONT_FAMILY = "Microsoft YaHei, Arial, sans-serif"
FONT_SIZE_SMALL = "9pt"
FONT_SIZE_NORMAL = "10pt"
FONT_SIZE_LARGE = "12pt"
FONT_SIZE_XLARGE = "14pt"

# 全局样式表
GLOBAL_STYLE = f"""
QWidget {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_NORMAL};
}}

QMainWindow {{
    background-color: white;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    background-color: white;
}}

QTabBar::tab {{
    background-color: {LIGHT_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: white;
    border-bottom: 2px solid {PRIMARY_COLOR};
}}

QTabBar::tab:hover {{
    background-color: #E3F2FD;
}}

QPushButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}}

QPushButton:hover {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton:pressed {{
    background-color: #0D47A1;
}}

QPushButton:disabled {{
    background-color: #BDBDBD;
    color: #757575;
}}

QPushButton[flat="true"] {{
    background-color: transparent;
    color: {PRIMARY_COLOR};
}}

QPushButton[flat="true"]:hover {{
    background-color: #E3F2FD;
}}

QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {PRIMARY_COLOR};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QTableWidget {{
    border: 1px solid {BORDER_COLOR};
    gridline-color: {BORDER_COLOR};
    selection-background-color: #E3F2FD;
    selection-color: {DARK_COLOR};
}}

QTableWidget::item {{
    padding: 4px;
}}

QTableWidget::item:selected {{
    background-color: #E3F2FD;
    color: {DARK_COLOR};
}}

QHeaderView::section {{
    background-color: {LIGHT_COLOR};
    padding: 6px;
    border: 1px solid {BORDER_COLOR};
    font-weight: bold;
}}

QGroupBox {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    margin-top: 16px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: {PRIMARY_COLOR};
}}

QLabel[heading="true"] {{
    font-size: {FONT_SIZE_LARGE};
    font-weight: bold;
    color: {PRIMARY_COLOR};
}}

QLabel[subheading="true"] {{
    font-size: {FONT_SIZE_NORMAL};
    font-weight: bold;
    color: {DARK_COLOR};
}}

QStatusBar {{
    background-color: {LIGHT_COLOR};
    color: {DARK_COLOR};
}}

QToolBar {{
    background-color: {LIGHT_COLOR};
    border-bottom: 1px solid {BORDER_COLOR};
    spacing: 6px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 6px;
    border-radius: 4px;
}}

QToolButton:hover {{
    background-color: #E3F2FD;
}}

QToolButton:pressed {{
    background-color: #BBDEFB;
}}

QMenu {{
    background-color: white;
    border: 1px solid {BORDER_COLOR};
}}

QMenu::item {{
    padding: 6px 24px 6px 24px;
}}

QMenu::item:selected {{
    background-color: #E3F2FD;
    color: {DARK_COLOR};
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
}}

QCheckBox::indicator:unchecked {{
    border: 1px solid {BORDER_COLOR};
    background-color: white;
}}

QCheckBox::indicator:checked {{
    border: 1px solid {PRIMARY_COLOR};
    background-color: {PRIMARY_COLOR};
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
}}

QRadioButton::indicator:unchecked {{
    border: 1px solid {BORDER_COLOR};
    background-color: white;
    border-radius: 8px;
}}

QRadioButton::indicator:checked {{
    border: 1px solid {PRIMARY_COLOR};
    background-color: {PRIMARY_COLOR};
    border-radius: 8px;
}}

QScrollBar:vertical {{
    border: none;
    background-color: {LIGHT_COLOR};
    width: 12px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: #BDBDBD;
    min-height: 20px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #9E9E9E;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background-color: {LIGHT_COLOR};
    height: 12px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: #BDBDBD;
    min-width: 20px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #9E9E9E;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""

# 按钮样式
PRIMARY_BUTTON_STYLE = f"""
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
"""

SECONDARY_BUTTON_STYLE = f"""
    background-color: white;
    color: {PRIMARY_COLOR};
    border: 1px solid {PRIMARY_COLOR};
    padding: 8px 16px;
    border-radius: 4px;
"""

SUCCESS_BUTTON_STYLE = f"""
    background-color: {SUCCESS_COLOR};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
"""

WARNING_BUTTON_STYLE = f"""
    background-color: {WARNING_COLOR};
    color: {DARK_COLOR};
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
"""

DANGER_BUTTON_STYLE = f"""
    background-color: {DANGER_COLOR};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
"""

# 标签样式
HEADING_STYLE = f"""
    font-size: {FONT_SIZE_LARGE};
    font-weight: bold;
    color: {PRIMARY_COLOR};
"""

SUBHEADING_STYLE = f"""
    font-size: {FONT_SIZE_NORMAL};
    font-weight: bold;
    color: {DARK_COLOR};
"""

INFO_LABEL_STYLE = f"""
    color: {INFO_COLOR};
    font-size: {FONT_SIZE_NORMAL};
"""

SUCCESS_LABEL_STYLE = f"""
    color: {SUCCESS_COLOR};
    font-size: {FONT_SIZE_NORMAL};
"""

WARNING_LABEL_STYLE = f"""
    color: {WARNING_COLOR};
    font-size: {FONT_SIZE_NORMAL};
"""

DANGER_LABEL_STYLE = f"""
    color: {DANGER_COLOR};
    font-size: {FONT_SIZE_NORMAL};
"""

# 表格样式
TABLE_STYLE = f"""
    border: 1px solid {BORDER_COLOR};
    gridline-color: {BORDER_COLOR};
    selection-background-color: #E3F2FD;
    selection-color: {DARK_COLOR};
"""

# 分组框样式
GROUP_BOX_STYLE = f"""
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    margin-top: 16px;
    font-weight: bold;
"""

# 输入框样式
INPUT_STYLE = f"""
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 6px;
    background-color: white;
"""

# 卡片样式
CARD_STYLE = """
    QGroupBox {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin-top: 16px;
        padding: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 5px;
        color: #1976D2;
        background-color: white;
    }
""" 