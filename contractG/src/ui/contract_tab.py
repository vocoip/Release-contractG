#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
合同生成标签页模块
"""

import os
import datetime
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, 
    QLabel, QComboBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QTextEdit, QCheckBox, QHeaderView,
    QSplitter, QSizePolicy, QFrame, QDialog, QPlainTextEdit,
    QFileDialog, QButtonGroup, QRadioButton, QGridLayout
)
from PyQt5.QtCore import Qt, QDate, QSize, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor
import subprocess
from pypinyin import lazy_pinyin, Style
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QStyle

# 注意：路径设置已由path_setup模块处理，不需要在这里重复设置

from src.database.excel_manager import ExcelManager
from src.utils.config_manager import ConfigManager
from src.utils.excel_handler import ExcelHandler
from src.models.contract import Contract, ContractItem
from src.models.company import Company
from src.ui.dialogs.customer_dialog import CustomerDialog
from src.utils.text_parser import TextParser
from src.ui.styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, 
    WARNING_COLOR, DANGER_COLOR, LIGHT_COLOR,
    HEADING_STYLE, SUBHEADING_STYLE
)

class ContractTab(QWidget):
    """合同生成标签页"""
    def __init__(self, customer_tab, product_tab):
        super().__init__()
        self.customer_tab = customer_tab
        self.product_tab = product_tab
        self.excel_manager = ExcelManager()
        self.config_manager = ConfigManager()
        self.excel_handler = ExcelHandler()
        
        # 创建QSettings对象，用于保存和恢复用户选择
        self.settings = QSettings("contractG", "ContractGenerator")
        
        # 连接客户和商品更新信号
        self.customer_tab.customer_updated.connect(self.update_customer_combo)
        self.product_tab.product_updated.connect(self.update_product_table)
        
        self.setup_ui()
        self.update_customer_combo()
        self.update_product_table()
        self.update_company_combo()
        
        # 恢复上次的选择状态
        self.restore_settings()
    
    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # 添加标题
        title_label = QLabel("合同生成")
        title_label.setStyleSheet(HEADING_STYLE + "font-size: 14pt;")
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        main_layout.addWidget(title_label)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #BDBDBD;
            }
        """)
        
        # 左侧面板 - 客户和商品选择
        left_panel = QWidget()
        left_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # 允许垂直拉伸
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)
        
        # 客户选择区域
        customer_group = QGroupBox("选择客户")
        customer_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # 固定高度
        customer_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #1976D2;
            }
        """)
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(8)
        
        # 客户搜索和新增区域
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        search_label = QLabel("搜索:")
        search_label.setMinimumWidth(40)
        search_layout.addWidget(search_label)
        
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("输入客户名称进行搜索...")
        self.customer_search.textChanged.connect(self.filter_customers)
        self.customer_search.setMinimumHeight(28)
        search_layout.addWidget(self.customer_search)
        
        # 新增客户按钮
        add_customer_btn = QPushButton("新增客户")
        add_customer_btn.setStyleSheet("""
            QPushButton {
                padding: 3px 10px;
                border: none;
                border-radius: 3px;
                background-color: #28a745;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_customer_btn.clicked.connect(self.add_customer)
        search_layout.addWidget(add_customer_btn)
        
        customer_layout.addLayout(search_layout)
        
        # 客户表格
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(3)
        self.customer_table.setHorizontalHeaderLabels(["公司名称", "联系人", "电话"])
        self.customer_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customer_table.doubleClicked.connect(self.select_customer)
        
        # 调整列宽
        self.customer_table.setColumnWidth(0, 200)
        self.customer_table.setColumnWidth(1, 100)
        self.customer_table.setColumnWidth(2, 120)
        
        # 设置表格样式
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        self.customer_table.horizontalHeader().setMinimumHeight(28)
        self.customer_table.horizontalHeader().setStyleSheet("QHeaderView::section { padding: 4px; }")
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 4px;
                min-height: 20px;
            }
        """)
        
        # 设置表格高度
        self.customer_table.setMinimumHeight(120)
        self.customer_table.setMaximumHeight(180)
        customer_layout.addWidget(self.customer_table)
        
        # 显示选中的客户信息
        self.selected_customer_label = QLabel("未选择客户")
        self.selected_customer_label.setStyleSheet("""
            font-weight: bold; 
            color: #1976D2; 
            padding: 6px; 
            background-color: #E3F2FD; 
            border-radius: 4px;
        """)
        self.selected_customer_label.setMinimumHeight(28)
        customer_layout.addWidget(self.selected_customer_label)
        
        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)
        
        # 商品选择区域
        product_group = QGroupBox("添加商品")
        product_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许垂直拉伸
        product_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #1976D2;
            }
        """)
        product_layout = QVBoxLayout()
        product_layout.setSpacing(8)
        
        # 商品搜索
        product_search_layout = QHBoxLayout()
        product_search_layout.setSpacing(8)
        
        product_search_label = QLabel("搜索:")
        product_search_label.setMinimumWidth(40)
        product_search_layout.addWidget(product_search_label)
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("输入商品名称进行搜索...")
        self.product_search.textChanged.connect(self.filter_products)
        self.product_search.setMinimumHeight(28)
        product_search_layout.addWidget(self.product_search)
        
        product_layout.addLayout(product_search_layout)
        
        # 商品表格
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["商品名称", "规格型号", "单位", "单价(元)"])
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.product_table.doubleClicked.connect(self.add_to_contract)
        
        # 调整列宽
        self.product_table.setColumnWidth(0, 200)
        self.product_table.setColumnWidth(1, 120)
        self.product_table.setColumnWidth(2, 60)
        self.product_table.setColumnWidth(3, 80)
        
        # 设置表格样式
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.horizontalHeader().setMinimumHeight(28)
        self.product_table.horizontalHeader().setStyleSheet("QHeaderView::section { padding: 4px; }")
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 4px;
                min-height: 20px;
            }
        """)
        
        product_layout.addWidget(self.product_table, 1)
        
        # 添加到合同按钮
        add_btn = QPushButton("添加到合同")
        add_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_btn.clicked.connect(self.add_to_contract)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: #2E7D32;
            }}
        """)
        add_btn.setMinimumHeight(32)
        product_layout.addWidget(add_btn)
        
        product_group.setLayout(product_layout)
        left_layout.addWidget(product_group, 1)
        
        # 右侧面板 - 合同信息和预览
        right_panel = QWidget()
        right_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # 允许垂直拉伸
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 合同信息区域
        contract_group = QGroupBox("合同信息")
        contract_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        contract_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #1976D2;
            }
        """)
        contract_layout = QVBoxLayout(contract_group)
        contract_layout.setSpacing(4)
        contract_layout.setContentsMargins(8, 8, 8, 8)
        
        # 生成选项区域 - 移到顶部
        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        options_layout.setContentsMargins(0, 0, 0, 8)
        
        # 文档类型选项
        doc_type_widget = QWidget()
        doc_type_layout = QHBoxLayout(doc_type_widget)
        doc_type_layout.setContentsMargins(0, 0, 0, 0)
        doc_type_layout.setSpacing(10)
        
        doc_type_layout.addWidget(QLabel("<b>文档类型</b>"))
        
        # 创建单选按钮组
        self.doc_type_group = QButtonGroup(self)
        
        # 合同选项
        self.doc_type_contract = QRadioButton("合同")
        self.doc_type_contract.setChecked(True)
        doc_type_layout.addWidget(self.doc_type_contract)
        self.doc_type_group.addButton(self.doc_type_contract, 0)
        
        # 报价单选项
        self.doc_type_quote = QRadioButton("报价单")
        doc_type_layout.addWidget(self.doc_type_quote)
        self.doc_type_group.addButton(self.doc_type_quote, 1)
        
        # 连接文档类型改变信号
        self.doc_type_group.buttonClicked.connect(self.update_generate_button_text)
        
        options_layout.addWidget(doc_type_widget)
        
        # 添加垂直分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("""
            QFrame {
                background-color: #E0E0E0;
                width: 1px;
                margin: 5px 10px;
            }
        """)
        options_layout.addWidget(separator)
        
        # PDF选项
        pdf_widget = QWidget()
        pdf_layout = QHBoxLayout(pdf_widget)
        pdf_layout.setContentsMargins(0, 0, 0, 0)
        pdf_layout.setSpacing(10)
        
        # 转换为PDF选项（包含盖章和转图片式）
        self.convert_to_pdf = QCheckBox("盖章(图片式PDF)")
        self.convert_to_pdf.setChecked(True)
        self.convert_to_pdf.setToolTip("启用后，将自动添加印章并转换为图片式PDF\n- 印章位置：右下角，大小40mm\n- 转换为图片式PDF以提高兼容性")
        pdf_layout.addWidget(self.convert_to_pdf)
        
        # 隐藏的选项（用于保持功能）
        self.add_seal = QCheckBox()
        self.add_seal.setVisible(False)
        self.convert_to_image_pdf = QCheckBox()
        self.convert_to_image_pdf.setVisible(False)
        
        # 当PDF选项改变时，同步更新隐藏的选项
        def on_pdf_option_changed(state):
            self.add_seal.setChecked(state == Qt.Checked)
            self.convert_to_image_pdf.setChecked(state == Qt.Checked)
        
        self.convert_to_pdf.stateChanged.connect(on_pdf_option_changed)
        
        options_layout.addWidget(pdf_widget)
        
        # 添加弹性空间
        options_layout.addStretch()
        
        # 生成按钮
        self.generate_btn = QPushButton("生成文档")
        self.generate_btn.setIcon(QIcon("src/resources/icons/contract.png"))
        self.generate_btn.clicked.connect(self.generate_contract)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 36px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        options_layout.addWidget(self.generate_btn)
        
        # 将生成选项添加到合同布局的顶部
        contract_layout.addLayout(options_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #E0E0E0;")
        contract_layout.addWidget(separator)
        
        # 合同基本信息表单 - 使用网格布局代替表单布局
        info_grid = QGridLayout()
        info_grid.setSpacing(4)  # 减少间距
        info_grid.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        # 第一行：合同编号和签订日期
        info_grid.addWidget(QLabel("合同编号:"), 0, 0, Qt.AlignRight)
        self.contract_number = QLineEdit()
        self.contract_number.setMinimumHeight(24)  # 减少高度
        today = datetime.date.today()
        default_number = f"SC-{today.strftime('%Y%m%d')}-001"
        self.contract_number.setText(default_number)
        info_grid.addWidget(self.contract_number, 0, 1)
        
        info_grid.addWidget(QLabel("签订日期:"), 0, 2, Qt.AlignRight)
        self.sign_date = QDateEdit()
        self.sign_date.setCalendarPopup(True)
        self.sign_date.setDate(QDate.currentDate())
        self.sign_date.setMinimumHeight(24)  # 减少高度
        info_grid.addWidget(self.sign_date, 0, 3)
        
        # 第二行：交货日期和付款方式
        info_grid.addWidget(QLabel("交货日期:"), 1, 0, Qt.AlignRight)
        self.delivery_date = QDateEdit()
        self.delivery_date.setCalendarPopup(True)
        self.delivery_date.setDate(QDate.currentDate().addDays(7))
        self.delivery_date.setMinimumHeight(24)  # 减少高度
        info_grid.addWidget(self.delivery_date, 1, 1)
        
        info_grid.addWidget(QLabel("付款方式:"), 1, 2, Qt.AlignRight)
        self.payment_method = QComboBox()
        self.payment_method.addItems([
            "款到发货",
            "货到付款",
            "预付30%，发货前付70%",
            "预付50%，发货前付50%",
            "月结30天",
            "月结60天",
            "自定义"
        ])
        self.payment_method.setEditable(True)
        self.payment_method.setMinimumHeight(24)  # 减少高度
        info_grid.addWidget(self.payment_method, 1, 3)
        
        # 第三行：报价有效期和乙方公司
        info_grid.addWidget(QLabel("报价有效期:"), 2, 0, Qt.AlignRight)
        self.quote_valid_days = QSpinBox()
        self.quote_valid_days.setRange(1, 90)
        self.quote_valid_days.setValue(30)
        self.quote_valid_days.setSuffix(" 天")
        self.quote_valid_days.setMinimumHeight(24)  # 减少高度
        info_grid.addWidget(self.quote_valid_days, 2, 1)
        
        info_grid.addWidget(QLabel("乙方公司:"), 2, 2, Qt.AlignRight)
        self.company_combo = QComboBox()
        self.company_combo.setMinimumHeight(24)  # 减少高度
        info_grid.addWidget(self.company_combo, 2, 3)
        
        # 第四行：技术服务费设置 - 使用水平布局
        info_grid.addWidget(QLabel("技术服务费:"), 3, 0, Qt.AlignRight)
        
        fee_layout = QHBoxLayout()
        fee_layout.setSpacing(4)
        fee_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加复选框
        self.service_fee_enabled = QCheckBox("启用")
        self.service_fee_enabled.setChecked(True)  # 默认启用
        self.service_fee_enabled.stateChanged.connect(self.on_service_fee_enabled_changed)
        fee_layout.addWidget(self.service_fee_enabled)
        
        fee_layout.addWidget(QLabel("费率:"))
        
        self.service_fee_rate = QDoubleSpinBox()
        self.service_fee_rate.setRange(0, 100)
        self.service_fee_rate.setValue(10)
        self.service_fee_rate.setSuffix(" %")
        self.service_fee_rate.setMinimumHeight(24)  # 减少高度
        self.service_fee_rate.valueChanged.connect(self.calculate_total)
        fee_layout.addWidget(self.service_fee_rate)
        
        fee_layout.addWidget(QLabel("最低:"))
        
        self.min_service_fee = QDoubleSpinBox()
        self.min_service_fee.setRange(0, 100000)
        self.min_service_fee.setValue(1500)
        self.min_service_fee.setSuffix(" 元")
        self.min_service_fee.setMinimumHeight(24)  # 减少高度
        self.min_service_fee.valueChanged.connect(self.calculate_total)
        fee_layout.addWidget(self.min_service_fee)
        
        # 将服务费布局添加到网格的第四行
        fee_widget = QWidget()
        fee_widget.setLayout(fee_layout)
        info_grid.addWidget(fee_widget, 3, 1, 1, 3)  # 跨越3列
        
        # 设置列的拉伸因子
        info_grid.setColumnStretch(1, 2)
        info_grid.setColumnStretch(3, 2)
        
        contract_layout.addLayout(info_grid)
        
        # 合同商品列表
        table_layout = QVBoxLayout()
        table_layout.setSpacing(2)  # 减少间距
        table_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        # 创建一个QWidget作为商品列表的容器
        items_widget = QWidget()
        items_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        items_layout = QVBoxLayout(items_widget)
        items_layout.setContentsMargins(0, 0, 0, 0)
        items_layout.setSpacing(2)  # 减少间距
        
        # 商品数量标签和操作按钮放在同一行
        items_header = QHBoxLayout()
        items_header.setSpacing(4)
        
        # 商品数量标签
        items_count = QLabel("(0件商品)")
        items_count.setStyleSheet("color: #666;")
        self.items_count_label = items_count
        items_header.addWidget(items_count)
        
        items_header.addStretch()
        
        # 商品操作按钮
        edit_item_btn = QPushButton("编辑")
        edit_item_btn.setIcon(QIcon("src/resources/icons/edit.png"))
        edit_item_btn.clicked.connect(self.edit_contract_item)
        edit_item_btn.setMinimumHeight(24)  # 减少高度
        edit_item_btn.setMaximumWidth(70)  # 减少宽度
        items_header.addWidget(edit_item_btn)
        
        remove_item_btn = QPushButton("移除")
        remove_item_btn.setIcon(QIcon("src/resources/icons/delete.png"))
        remove_item_btn.clicked.connect(self.remove_contract_item)
        remove_item_btn.setMinimumHeight(24)  # 减少高度
        remove_item_btn.setMaximumWidth(70)  # 减少宽度
        items_header.addWidget(remove_item_btn)
        
        clear_items_btn = QPushButton("清空")
        clear_items_btn.setIcon(QIcon("src/resources/icons/clear.png"))
        clear_items_btn.clicked.connect(self.clear_contract_items)
        clear_items_btn.setMinimumHeight(24)  # 减少高度
        clear_items_btn.setMaximumWidth(70)  # 减少宽度
        items_header.addWidget(clear_items_btn)
        
        items_layout.addLayout(items_header)
        
        # 商品表格
        self.contract_items_table = QTableWidget()
        self.contract_items_table.setColumnCount(6)
        self.contract_items_table.setHorizontalHeaderLabels(["商品名称", "规格型号", "单位", "单价(元)", "数量", "金额(元)"])
        self.contract_items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contract_items_table.setEditTriggers(QTableWidget.EditKeyPressed)
        self.contract_items_table.doubleClicked.connect(self.on_contract_item_double_clicked)
        self.contract_items_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 调整列宽
        self.contract_items_table.setColumnWidth(0, 180)
        self.contract_items_table.setColumnWidth(1, 120)
        self.contract_items_table.setColumnWidth(2, 60)
        self.contract_items_table.setColumnWidth(3, 80)
        self.contract_items_table.setColumnWidth(4, 60)
        self.contract_items_table.setColumnWidth(5, 80)
        
        # 设置表格样式
        self.contract_items_table.horizontalHeader().setStretchLastSection(True)
        self.contract_items_table.horizontalHeader().setMinimumHeight(24)  # 减少高度
        self.contract_items_table.horizontalHeader().setStyleSheet("QHeaderView::section { padding: 2px; }")  # 减少内边距
        self.contract_items_table.verticalHeader().setVisible(False)
        self.contract_items_table.setAlternatingRowColors(True)
        self.contract_items_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 2px;  /* 减少内边距 */
                min-height: 18px;  /* 减少最小高度 */
            }
        """)
        
        items_layout.addWidget(self.contract_items_table)
        
        # 将商品列表容器添加到主布局，并设置拉伸因子
        contract_layout.addWidget(items_widget, 1)
        
        # 合同金额信息
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(20)  # 增加间距
        amount_layout.setContentsMargins(0, 8, 0, 8)  # 添加上下边距
        
        # 商品总金额
        amount_layout.addWidget(QLabel("商品总金额:"))
        self.total_amount_label = QLabel("0.00 元")
        self.total_amount_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        amount_layout.addWidget(self.total_amount_label)
        
        # 技术服务费
        amount_layout.addWidget(QLabel("技术服务费:"))
        self.service_fee_label = QLabel("0.00 元")
        self.service_fee_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        amount_layout.addWidget(self.service_fee_label)
        
        # 合同总金额
        amount_layout.addWidget(QLabel("合同总金额:"))
        self.contract_amount_label = QLabel("0.00 元")
        self.contract_amount_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #D50000;")
        amount_layout.addWidget(self.contract_amount_label)
        
        # 添加弹性空间
        amount_layout.addStretch()
        
        contract_layout.addLayout(amount_layout)
        
        right_layout.addWidget(contract_group, 1)
        
        # 将左右面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # 设置初始分割比例
        splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])
        
        # 将分割器添加到主布局，并设置拉伸因子
        main_layout.addWidget(splitter, 1)  # 添加拉伸因子1，使分割器占用所有可用空间
        self.setLayout(main_layout)
        
        # 初始化生成按钮文本
        self.update_generate_button_text()
        
        # 恢复用户设置
        self.restore_settings()
    
    def update_customer_combo(self):
        """更新客户列表"""
        self.filter_customers()
    
    def filter_customers(self):
        """过滤客户"""
        search_text = self.customer_search.text().lower()
        self.customer_table.setRowCount(0)
        customers = self.customer_tab.get_customers()
        
        row = 0
        for customer in customers:
            # 获取客户信息的拼音和首字母
            name_pinyin = ''.join(lazy_pinyin(customer.name or ''))
            name_initials = ''.join([p[0] for p in lazy_pinyin(customer.name or '')])
            contact_pinyin = ''.join(lazy_pinyin(customer.contact or ''))
            contact_initials = ''.join([p[0] for p in lazy_pinyin(customer.contact or '')])
            
            # 将所有可搜索字段组合成一个字符串（包含原文、拼音和首字母）
            searchable_text = f"{customer.name or ''} {customer.contact or ''} {customer.phone or ''} {customer.address or ''} {name_pinyin} {name_initials} {contact_pinyin} {contact_initials}".lower()
            
            # 将搜索关键词按空格分割，支持多个关键词
            search_keywords = [keyword.strip() for keyword in search_text.split() if keyword.strip()]
            
            # 检查是否所有关键词都匹配
            if not search_text or all(keyword in searchable_text for keyword in search_keywords):
                self.customer_table.insertRow(row)
                name_item = QTableWidgetItem(customer.name)
                name_item.setData(Qt.UserRole, customer)
                self.customer_table.setItem(row, 0, name_item)
                self.customer_table.setItem(row, 1, QTableWidgetItem(customer.contact))
                self.customer_table.setItem(row, 2, QTableWidgetItem(customer.phone))
                row += 1
    
    def select_customer(self):
        """选择客户"""
        selected_rows = self.customer_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        customer_item = self.customer_table.item(row, 0)
        customer = customer_item.data(Qt.UserRole)
        
        if customer:
            self.selected_customer = customer
            self.selected_customer_label.setText(f"已选择: {customer.name} ({customer.contact})")
    
    def update_product_table(self):
        """更新商品表格"""
        self.product_table.setRowCount(0)
        products = self.product_tab.get_products()
        
        for i, product in enumerate(products):
            self.product_table.insertRow(i)
            self.product_table.setItem(i, 0, QTableWidgetItem(product.name))
            self.product_table.setItem(i, 1, QTableWidgetItem(product.model))
            self.product_table.setItem(i, 2, QTableWidgetItem(product.unit))
            self.product_table.setItem(i, 3, QTableWidgetItem(product.price))
    
    def filter_products(self):
        """过滤商品"""
        search_text = self.product_search.text().lower()
        self.product_table.setRowCount(0)
        products = self.product_tab.get_products()
        
        row = 0
        for product in products:
            # 获取商品信息的拼音和首字母
            name_pinyin = ''.join(lazy_pinyin(product.name))
            name_initials = ''.join([p[0] for p in lazy_pinyin(product.name)])
            model_pinyin = ''.join(lazy_pinyin(product.model))
            model_initials = ''.join([p[0] for p in lazy_pinyin(product.model)])
            
            # 将所有可搜索字段组合成一个字符串（包含原文、拼音和首字母）
            searchable_text = f"{product.name} {product.model} {product.unit} {name_pinyin} {name_initials} {model_pinyin} {model_initials}".lower()
            
            # 将搜索关键词按空格分割，支持多个关键词
            search_keywords = [keyword.strip() for keyword in search_text.split() if keyword.strip()]
            
            # 检查是否所有关键词都匹配
            if not search_text or all(keyword in searchable_text for keyword in search_keywords):
                self.product_table.insertRow(row)
                self.product_table.setItem(row, 0, QTableWidgetItem(product.name))
                self.product_table.setItem(row, 1, QTableWidgetItem(product.model))
                self.product_table.setItem(row, 2, QTableWidgetItem(product.unit))
                self.product_table.setItem(row, 3, QTableWidgetItem(product.price))
                row += 1
    
    def add_to_contract(self):
        """添加商品到合同"""
        selected_rows = self.product_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个商品！")
            return
        
        row = selected_rows[0].row()
        
        # 获取选中的商品信息
        name = self.product_table.item(row, 0).text()
        model = self.product_table.item(row, 1).text()
        unit = self.product_table.item(row, 2).text()
        price = self.product_table.item(row, 3).text()
        
        # 检查价格是否为空
        if not price:
            QMessageBox.warning(self, "警告", "商品价格不能为空！请先设置商品价格。")
            return
        
        # 添加到合同表格
        row = self.contract_items_table.rowCount()
        self.contract_items_table.insertRow(row)
        
        # 设置只读的单元格
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.contract_items_table.setItem(row, 0, name_item)
        
        model_item = QTableWidgetItem(model)
        model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
        self.contract_items_table.setItem(row, 1, model_item)
        
        unit_item = QTableWidgetItem(unit)
        unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)
        self.contract_items_table.setItem(row, 2, unit_item)
        
        # 设置可编辑的单价单元格
        price_item = QTableWidgetItem(price)
        self.contract_items_table.setItem(row, 3, price_item)
        
        # 添加数量单元格（可编辑）
        quantity_item = QTableWidgetItem("1")
        self.contract_items_table.setItem(row, 4, quantity_item)
        
        # 计算金额
        try:
            amount = float(price) * 1
            amount_item = QTableWidgetItem(f"{amount:.2f}")
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # 金额不可编辑
        except ValueError:
            QMessageBox.warning(self, "警告", f"商品价格格式不正确：'{price}'，请输入有效的数字。")
            self.contract_items_table.removeRow(row)
            return
        
        self.contract_items_table.setItem(row, 5, amount_item)
        
        # 连接数量和单价变化信号
        self.contract_items_table.itemChanged.connect(self.update_item_amount)
        
        # 计算总金额
        self.calculate_total()
    
    def update_item_amount(self, item):
        """更新商品金额"""
        if item.column() in [3, 4]:  # 单价列或数量列
            row = item.row()
            try:
                # 检查行是否有效
                if row < 0 or row >= self.contract_items_table.rowCount():
                    return
                
                # 获取单价和数量
                price_item = self.contract_items_table.item(row, 3)
                quantity_item = self.contract_items_table.item(row, 4)
                
                if not price_item or not quantity_item:
                    return
                
                price = float(price_item.text())
                if price <= 0:
                    raise ValueError("单价必须大于0")
                
                quantity = int(quantity_item.text())
                if quantity <= 0:
                    raise ValueError("数量必须大于0")
                
                # 计算新的金额
                amount = price * quantity
                
                # 更新金额单元格
                amount_item = self.contract_items_table.item(row, 5)
                if amount_item is None:
                    amount_item = QTableWidgetItem(f"{amount:.2f}")
                    self.contract_items_table.setItem(row, 5, amount_item)
                else:
                    amount_item.setText(f"{amount:.2f}")
                
                self.calculate_total()
            except ValueError as e:
                error_msg = str(e) if "必须大于0" in str(e) else "请输入有效的数值！"
                QMessageBox.warning(self, "警告", error_msg)
                if item.column() == 3:  # 单价列
                    # 恢复原始单价
                    original_price = self.product_table.item(self.product_table.currentRow(), 3).text()
                    item.setText(original_price)
                else:  # 数量列
                    item.setText("1")
            except Exception as e:
                QMessageBox.warning(self, "警告", f"更新金额时出错: {str(e)}")
                if item.column() == 3:
                    original_price = self.product_table.item(self.product_table.currentRow(), 3).text()
                    item.setText(original_price)
                else:
                    item.setText("1")
    
    def remove_contract_item(self):
        """从合同中移除商品"""
        selected_rows = self.contract_items_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个商品！")
            return
        
        # 断开信号连接，防止删除过程中触发itemChanged
        self.contract_items_table.itemChanged.disconnect(self.update_item_amount)
        
        row = selected_rows[0].row()
        self.contract_items_table.removeRow(row)
        
        # 重新连接信号
        self.contract_items_table.itemChanged.connect(self.update_item_amount)
        
        # 重新计算总金额
        self.calculate_total()
    
    def edit_contract_item(self):
        """编辑合同中的商品"""
        selected_rows = self.contract_items_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个商品！")
            return
        
        row = selected_rows[0].row()
        
        # 获取当前商品信息
        name = self.contract_items_table.item(row, 0).text()
        model = self.contract_items_table.item(row, 1).text()
        unit = self.contract_items_table.item(row, 2).text()
        price = float(self.contract_items_table.item(row, 3).text())
        quantity = int(self.contract_items_table.item(row, 4).text())
        
        # 创建编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑商品")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # 商品信息（只读）
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        model_label = QLabel(model)
        unit_label = QLabel(unit)
        
        form_layout.addRow("商品名称:", name_label)
        form_layout.addRow("规格型号:", model_label)
        form_layout.addRow("单位:", unit_label)
        
        # 单价（可编辑）
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0.01, 9999999.99)
        price_spin.setDecimals(2)
        price_spin.setValue(price)
        price_spin.setMinimumHeight(30)
        form_layout.addRow("单价(元):", price_spin)
        
        # 数量（可编辑）
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 9999)
        quantity_spin.setValue(quantity)
        quantity_spin.setMinimumHeight(30)
        form_layout.addRow("数量:", quantity_spin)
        
        # 金额（自动计算）
        amount_label = QLabel(f"{price * quantity:.2f}")
        amount_label.setStyleSheet("font-weight: bold; color: #1976D2;")
        form_layout.addRow("金额(元):", amount_label)
        
        # 更新金额显示
        def update_amount():
            amount = price_spin.value() * quantity_spin.value()
            amount_label.setText(f"{amount:.2f}")
        
        price_spin.valueChanged.connect(update_amount)
        quantity_spin.valueChanged.connect(update_amount)
        
        layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                background-color: #28a745;
                color: white;
                min-height: 30px;
            }
        """)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                background-color: #6c757d;
                color: white;
                min-height: 30px;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # 连接按钮信号
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 断开信号连接，防止更新过程中触发itemChanged
            self.contract_items_table.itemChanged.disconnect(self.update_item_amount)
            
            # 更新单价和数量
            new_price = price_spin.value()
            new_quantity = quantity_spin.value()
            new_amount = new_price * new_quantity
            
            self.contract_items_table.item(row, 3).setText(f"{new_price:.2f}")
            self.contract_items_table.item(row, 4).setText(str(new_quantity))
            self.contract_items_table.item(row, 5).setText(f"{new_amount:.2f}")
            
            # 重新连接信号
            self.contract_items_table.itemChanged.connect(self.update_item_amount)
            
            # 重新计算总金额
            self.calculate_total()
    
    def clear_contract_items(self):
        """清空合同商品列表"""
        # 检查信号是否已连接，如果已连接则断开
        try:
            self.contract_items_table.itemChanged.disconnect(self.update_item_amount)
        except TypeError:
            pass  # 信号未连接，忽略错误
        
        self.contract_items_table.setRowCount(0)
        
        # 重新连接信号
        self.contract_items_table.itemChanged.connect(self.update_item_amount)
        
        # 重新计算总金额
        self.calculate_total()
    
    def calculate_total(self):
        """计算合同总金额"""
        total = 0.0
        
        # 计算商品总数量
        item_count = self.contract_items_table.rowCount()
        self.items_count_label.setText(f"({item_count}件商品)")
        
        # 计算商品总金额
        for row in range(self.contract_items_table.rowCount()):
            try:
                amount_item = self.contract_items_table.item(row, 5)
                if amount_item is None:
                    # 如果金额单元格不存在，尝试从价格和数量计算
                    price_item = self.contract_items_table.item(row, 3)
                    quantity_item = self.contract_items_table.item(row, 4)
                    
                    if price_item is not None and quantity_item is not None:
                        try:
                            price = float(price_item.text())
                            quantity = int(quantity_item.text())
                            amount = price * quantity
                            
                            # 创建金额单元格
                            amount_item = QTableWidgetItem(f"{amount:.2f}")
                            self.contract_items_table.setItem(row, 5, amount_item)
                            total += amount
                        except (ValueError, TypeError):
                            continue
                else:
                    try:
                        amount = float(amount_item.text())
                        total += amount
                    except (ValueError, TypeError):
                        continue
            except Exception as e:
                print(f"计算总金额时出错: {str(e)}")
                continue
        
        # 更新商品总金额显示
        self.total_amount_label.setText(f"{total:.2f} 元")
        
        try:
            # 计算技术服务费
            service_fee = 0.0
            if self.service_fee_enabled.isChecked():
                service_fee_rate = self.service_fee_rate.value() / 100
                min_service_fee = self.min_service_fee.value()
                service_fee = max(total * service_fee_rate, min_service_fee)
            
            # 更新技术服务费显示
            self.service_fee_label.setText(f"{service_fee:.2f} 元")
            
            # 计算合同总金额
            grand_total = total + service_fee
            self.contract_amount_label.setText(f"{grand_total:.2f} 元")
            
            # 根据金额大小调整颜色
            if grand_total > 50000:
                self.contract_amount_label.setStyleSheet("font-weight: bold; font-size: 14pt; color: #D50000;")
            elif grand_total > 10000:
                self.contract_amount_label.setStyleSheet("font-weight: bold; font-size: 14pt; color: #FF6D00;")
            else:
                self.contract_amount_label.setStyleSheet("font-weight: bold; font-size: 14pt; color: #2E7D32;")
        except Exception as e:
            # 如果服务费计算出错，仅显示商品总额
            self.contract_amount_label.setText(f"{total:.2f} 元")
            print(f"计算服务费时出错: {str(e)}")
    
    def update_company_combo(self):
        """更新乙方公司下拉框"""
        self.company_combo.clear()
        companies = self.config_manager.get_companies()
        for company in companies:
            self.company_combo.addItem(company.name, company)
            if company.is_default:
                self.company_combo.setCurrentIndex(self.company_combo.count() - 1)
    
    def clear_contract(self):
        """清空合同所有内容"""
        # 清空合同商品列表
        self.clear_contract_items()
        
        # 清空选中的客户
        if hasattr(self, 'selected_customer'):
            delattr(self, 'selected_customer')
        self.selected_customer_label.setText("未选择客户")
        
        # 重置日期为当前日期
        self.sign_date.setDate(QDate.currentDate())
        self.delivery_date.setDate(QDate.currentDate().addDays(7))
        
        # 重置付款方式为默认值
        self.payment_method.setCurrentIndex(0)
        
        # 重置技术服务费为默认值
        self.service_fee_enabled.setChecked(True)
        self.service_fee_rate.setValue(10)
        self.min_service_fee.setValue(1500)
        
        # 重新计算总金额
        self.calculate_total()
    
    def generate_contract(self):
        """生成合同"""
        # 检查是否选择了客户
        if not hasattr(self, 'selected_customer'):
            QMessageBox.warning(self, "警告", "请先选择客户！")
            return
        
        # 检查是否添加了商品
        if self.contract_items_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "请先添加商品到合同！")
            return
        
        # 获取客户信息
        customer = self.selected_customer
        
        # 获取乙方公司信息
        company = self.company_combo.currentData()
        if not company:
            QMessageBox.warning(self, "警告", "请选择乙方公司！")
            return
        
        # 获取合同信息
        contract_number = self.contract_number.text()
        sign_date = self.sign_date.date().toString("yyyy年MM月dd日")
        delivery_date = self.delivery_date.date().toString("yyyy年MM月dd日")
        payment_method = self.payment_method.currentText()
        remarks = ""  # 使用空字符串替代
        quote_valid_days = self.quote_valid_days.value()
        
        # 获取商品列表
        items = []
        for row in range(self.contract_items_table.rowCount()):
            item = ContractItem(
                name=self.contract_items_table.item(row, 0).text(),
                model=self.contract_items_table.item(row, 1).text(),
                unit=self.contract_items_table.item(row, 2).text(),
                price=float(self.contract_items_table.item(row, 3).text()),
                quantity=int(self.contract_items_table.item(row, 4).text()),
                amount=float(self.contract_items_table.item(row, 5).text())
            )
            items.append(item)
        
        # 创建合同对象
        contract = Contract(
            number=contract_number,
            customer=customer,
            company=company.to_dict(),
            items=items,
            sign_date=sign_date,
            delivery_date=delivery_date,
            payment_method=payment_method,
            remarks=remarks,
            total_amount=float(self.total_amount_label.text().split()[0]),
            service_fee=float(self.service_fee_label.text().split()[0]),
            grand_total=float(self.contract_amount_label.text().split()[0]),
            quote_valid_days=quote_valid_days,
            is_draft=False
        )
        
        # 添加技术服务费参数
        contract.service_fee_enabled = self.service_fee_enabled.isChecked()
        contract.service_fee_rate = self.service_fee_rate.value() / 100  # 转换为小数
        contract.min_service_fee = self.min_service_fee.value()
        
        # 添加印章设置
        contract.add_seal = self.add_seal.isChecked()
        # 根据文档类型设置印章位置
        if self.doc_type_group.checkedId() == 1:  # 报价单
            contract.seal_position = "right-bottom"
            contract.seal_text = "报价方签章处"  # 添加签章文字
        else:  # 合同
            contract.seal_position = "right-bottom"
            contract.seal_text = None  # 合同不添加签章文字
        
        # 添加PDF转换选项
        contract.convert_to_pdf = self.convert_to_pdf.isChecked()
        contract.convert_to_image_pdf = self.convert_to_image_pdf.isChecked()
        
        # 添加随机后缀
        import random
        contract.random_suffix = f"{random.randint(100, 999)}"
        
        # 获取文档类型选择
        doc_type_id = self.doc_type_group.checkedId()
        
        # 保存当前选择的状态
        self.save_settings()
        
        try:
            if doc_type_id == 0:  # 合同
                self.excel_handler.generate_contract_only(contract)
            else:  # 报价单
                self.excel_handler.generate_quote_only(contract)
            
            # 更新合同编号（自增）
            self.increment_contract_number()
            
            # 清空合同所有内容
            self.clear_contract()
            
            # 自动打开输出文件夹
            self.open_contracts_folder()
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"生成文档时出错：{str(e)}")
    
    def open_contracts_folder(self):
        """打开合同文件夹"""
        try:
            folder_path = self.excel_handler.get_contracts_folder()
            
            # 根据操作系统打开文件夹
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS 和 Linux
                if os.path.exists('/usr/bin/open'):  # macOS
                    subprocess.run(['open', folder_path])
                else:  # Linux
                    subprocess.run(['xdg-open', folder_path])
            else:
                QMessageBox.warning(self, "警告", "无法自动打开文件夹，请手动打开。")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"打开文件夹时出错：{str(e)}")
    
    def increment_contract_number(self):
        """自增合同编号"""
        current_number = self.contract_number.text()
        
        # 假设合同编号格式为 SC-YYYYMMDD-XXX
        parts = current_number.split('-')
        if len(parts) == 3:
            try:
                seq_num = int(parts[2])
                parts[2] = f"{seq_num + 1:03d}"
                new_number = '-'.join(parts)
                self.contract_number.setText(new_number)
            except ValueError:
                # 如果解析失败，保持原编号不变
                pass
    
    def add_customer(self):
        """添加新客户"""
        dialog = CustomerDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            customer = dialog.get_customer_data()
            # 添加到客户列表
            self.customer_tab.customers.append(customer)
            # 保存更改
            self.customer_tab.excel_manager.save_customers(self.customer_tab.customers)
            # 更新客户列表
            self.update_customer_combo()
            # 选中新添加的客户
            self.select_customer_by_name(customer.name)
            QMessageBox.information(self, "成功", "客户添加成功")

    def select_customer_by_name(self, name):
        """根据名称选择客户"""
        for row in range(self.customer_table.rowCount()):
            item = self.customer_table.item(row, 0)
            if item and item.text() == name:
                self.customer_table.selectRow(row)
                self.select_customer()
                break

    def on_service_fee_enabled_changed(self, state):
        """技术服务费启用状态改变"""
        enabled = state == Qt.Checked
        self.service_fee_rate.setEnabled(enabled)
        self.min_service_fee.setEnabled(enabled)
        self.calculate_total()

    def update_generate_button_text(self, button=None):
        """根据选择的文档类型更新生成按钮的文本"""
        doc_type = self.doc_type_group.checkedId()
        if doc_type == 0:
            self.generate_btn.setText("生成合同")
        elif doc_type == 1:
            self.generate_btn.setText("生成报价单")
        else:
            self.generate_btn.setText("生成文档")

    def save_settings(self):
        """保存用户选择的状态"""
        # 保存文档类型选择
        self.settings.setValue("doc_type", self.doc_type_group.checkedId())
        
        # 保存PDF转换选项
        self.settings.setValue("convert_to_pdf", self.convert_to_pdf.isChecked())
        
        # 保存印章选项
        self.settings.setValue("add_seal", self.add_seal.isChecked())
        
        # 保存PDF转图片式选项
        self.settings.setValue("convert_to_image_pdf", self.convert_to_image_pdf.isChecked())
    
    def restore_settings(self):
        """恢复用户上次选择的状态"""
        # 恢复文档类型选择
        doc_type = self.settings.value("doc_type", 0, type=int)
        if doc_type == 0:
            self.doc_type_contract.setChecked(True)
        elif doc_type == 1:
            self.doc_type_quote.setChecked(True)
        
        # 恢复PDF转换选项
        convert_to_pdf = self.settings.value("convert_to_pdf", True, type=bool)
        self.convert_to_pdf.setChecked(convert_to_pdf)
        
        # 恢复印章选项和图片式PDF选项（自动跟随PDF选项）
        if convert_to_pdf:
            self.add_seal.setChecked(True)
            self.convert_to_image_pdf.setChecked(True)
        else:
            self.add_seal.setChecked(False)
            self.convert_to_image_pdf.setChecked(False)
        
        # 更新生成按钮文本
        self.update_generate_button_text() 

    def on_contract_item_double_clicked(self, index):
        """处理已选商品双击事件，弹出编辑对话框"""
        row = index.row()
        
        # 获取当前商品信息
        name = self.contract_items_table.item(row, 0).text()
        model = self.contract_items_table.item(row, 1).text()
        unit = self.contract_items_table.item(row, 2).text()
        price = float(self.contract_items_table.item(row, 3).text())
        quantity = int(self.contract_items_table.item(row, 4).text())
        
        # 创建编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑商品")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # 商品信息（只读）
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        model_label = QLabel(model)
        unit_label = QLabel(unit)
        
        form_layout.addRow("商品名称:", name_label)
        form_layout.addRow("规格型号:", model_label)
        form_layout.addRow("单位:", unit_label)
        
        # 单价（可编辑）
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0.01, 9999999.99)
        price_spin.setDecimals(2)
        price_spin.setValue(price)
        price_spin.setMinimumHeight(30)
        form_layout.addRow("单价(元):", price_spin)
        
        # 数量（可编辑）
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 9999)
        quantity_spin.setValue(quantity)
        quantity_spin.setMinimumHeight(30)
        form_layout.addRow("数量:", quantity_spin)
        
        # 金额（自动计算）
        amount_label = QLabel(f"{price * quantity:.2f}")
        amount_label.setStyleSheet("font-weight: bold; color: #1976D2;")
        form_layout.addRow("金额(元):", amount_label)
        
        # 更新金额显示
        def update_amount():
            amount = price_spin.value() * quantity_spin.value()
            amount_label.setText(f"{amount:.2f}")
        
        price_spin.valueChanged.connect(update_amount)
        quantity_spin.valueChanged.connect(update_amount)
        
        layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                background-color: #28a745;
                color: white;
                min-height: 30px;
            }
        """)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                background-color: #6c757d;
                color: white;
                min-height: 30px;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # 连接按钮信号
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 断开信号连接，防止更新过程中触发itemChanged
            self.contract_items_table.itemChanged.disconnect(self.update_item_amount)
            
            # 更新单价和数量
            new_price = price_spin.value()
            new_quantity = quantity_spin.value()
            new_amount = new_price * new_quantity
            
            self.contract_items_table.item(row, 3).setText(f"{new_price:.2f}")
            self.contract_items_table.item(row, 4).setText(str(new_quantity))
            self.contract_items_table.item(row, 5).setText(f"{new_amount:.2f}")
            
            # 重新连接信号
            self.contract_items_table.itemChanged.connect(self.update_item_amount)
            
            # 重新计算总金额
            self.calculate_total() 