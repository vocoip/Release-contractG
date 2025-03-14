#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
客户信息对话框模块
"""

import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QMessageBox, QPlainTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.models.customer import Customer
from src.utils.text_parser import TextParser

class CustomerDialog(QDialog):
    """客户信息对话框"""
    
    # 定义信号
    customer_saved = pyqtSignal(Customer)
    
    def __init__(self, customer=None, parent=None):
        """初始化对话框"""
        super().__init__(parent)
        self.customer = customer
        self.setup_ui()
        if customer:
            self.load_customer_data()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("客户信息")
        self.setMinimumWidth(400)
        
        # 创建主布局
        layout = QVBoxLayout()
        
        # 创建文本解析区域
        parse_layout = QVBoxLayout()
        parse_label = QLabel("粘贴文本进行解析:")
        self.parse_text = QPlainTextEdit()
        self.parse_text.setPlaceholderText("在此粘贴包含客户信息的文本，系统将自动解析相关字段")
        self.parse_text.setMaximumHeight(100)
        parse_button = QPushButton("解析文本")
        parse_button.setStyleSheet("""
            QPushButton {
                padding: 3px 10px;
                border: none;
                border-radius: 3px;
                background-color: #17a2b8;
                color: white;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        parse_button.clicked.connect(self.parse_text_content)
        parse_layout.addWidget(parse_label)
        parse_layout.addWidget(self.parse_text)
        parse_layout.addWidget(parse_button)
        layout.addLayout(parse_layout)
        
        # 创建输入字段
        self.create_input_fields(layout)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                background-color: #28a745;
                color: white;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                background-color: #6c757d;
                color: white;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接验证信号
        self.name_input.textChanged.connect(self.validate_input)
        self.tax_id_input.textChanged.connect(self.validate_input)
        
        # 初始验证
        self.validate_input()
    
    def create_input_fields(self, layout):
        """创建输入字段"""
        # 公司名称（必填）
        name_layout = QHBoxLayout()
        name_label = QLabel("公司名称: *")
        name_label.setStyleSheet("color: #d32f2f;")  # 红色星号表示必填
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        self.name_input.setPlaceholderText("必填")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 联系人（选填）
        contact_layout = QHBoxLayout()
        contact_label = QLabel("联系人:")
        self.contact_input = QLineEdit()
        self.contact_input.setMaxLength(50)
        contact_layout.addWidget(contact_label)
        contact_layout.addWidget(self.contact_input)
        layout.addLayout(contact_layout)
        
        # 电话（选填）
        phone_layout = QHBoxLayout()
        phone_label = QLabel("电话:")
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(20)
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # 地址（选填）
        address_layout = QHBoxLayout()
        address_label = QLabel("地址:")
        self.address_input = QLineEdit()
        self.address_input.setMaxLength(200)
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)
        
        # 开户银行（选填）
        bank_name_layout = QHBoxLayout()
        bank_name_label = QLabel("开户银行:")
        self.bank_name_input = QLineEdit()
        self.bank_name_input.setMaxLength(100)
        bank_name_layout.addWidget(bank_name_label)
        bank_name_layout.addWidget(self.bank_name_input)
        layout.addLayout(bank_name_layout)
        
        # 银行账号（选填）
        bank_account_layout = QHBoxLayout()
        bank_account_label = QLabel("银行账号:")
        self.bank_account_input = QLineEdit()
        self.bank_account_input.setMaxLength(30)
        bank_account_layout.addWidget(bank_account_label)
        bank_account_layout.addWidget(self.bank_account_input)
        layout.addLayout(bank_account_layout)
        
        # 税号（必填）
        tax_id_layout = QHBoxLayout()
        tax_id_label = QLabel("税号: *")
        tax_id_label.setStyleSheet("color: #d32f2f;")  # 红色星号表示必填
        self.tax_id_input = QLineEdit()
        self.tax_id_input.setMaxLength(20)
        self.tax_id_input.setPlaceholderText("必填")
        tax_id_layout.addWidget(tax_id_label)
        tax_id_layout.addWidget(self.tax_id_input)
        layout.addLayout(tax_id_layout)
    
    def load_customer_data(self):
        """加载客户数据到表单"""
        if not self.customer:
            return
        
        self.name_input.setText(self.customer.name)
        self.contact_input.setText(self.customer.contact)
        self.phone_input.setText(self.customer.phone)
        self.address_input.setText(self.customer.address)
        self.bank_name_input.setText(self.customer.bank_name)
        self.bank_account_input.setText(self.customer.bank_account)
        self.tax_id_input.setText(self.customer.tax_id)
    
    def get_customer_data(self):
        """获取表单中的客户数据"""
        return Customer(
            name=self.name_input.text().strip(),
            contact=self.contact_input.text().strip(),
            phone=self.phone_input.text().strip(),
            address=self.address_input.text().strip(),
            bank_name=self.bank_name_input.text().strip(),
            bank_account=self.bank_account_input.text().strip(),
            tax_id=self.tax_id_input.text().strip()
        )
    
    def validate_input(self):
        """验证输入"""
        name = self.name_input.text().strip()
        tax_id = self.tax_id_input.text().strip()
        
        # 检查必填字段
        is_valid = bool(name and tax_id)  # 只检查公司名称和税号
        
        # 设置保存按钮状态
        self.save_button.setEnabled(is_valid)
        
        return is_valid
    
    def accept(self):
        """确认对话框"""
        if not self.validate_input():
            QMessageBox.warning(self, "警告", "请填写必填字段：公司名称、税号")
            return
        
        try:
            customer = self.get_customer_data()
            self.customer_saved.emit(customer)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存客户信息时发生错误：{str(e)}")

    def parse_text_content(self):
        """解析文本内容"""
        text = self.parse_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请先粘贴需要解析的文本内容")
            return
        
        # 使用文本解析工具解析内容
        result = TextParser.parse_customer_info(text)
        if not result:
            QMessageBox.warning(self, "警告", "未能从文本中解析出有效的客户信息")
            return
        
        # 填充解析结果到表单
        if result.get('name'):
            self.name_input.setText(result['name'])
        if result.get('contact'):
            self.contact_input.setText(result['contact'])
        if result.get('phone'):
            self.phone_input.setText(result['phone'])
        if result.get('address'):
            self.address_input.setText(result['address'])
        if result.get('bank_name'):
            self.bank_name_input.setText(result['bank_name'])
        if result.get('bank_account'):
            self.bank_account_input.setText(result['bank_account'])
        if result.get('tax_id'):
            self.tax_id_input.setText(result['tax_id'])
        
        # 验证输入
        self.validate_input()
        
        # 清空文本框
        self.parse_text.clear()
        
        QMessageBox.information(self, "成功", "文本解析完成，请检查解析结果并补充完善") 