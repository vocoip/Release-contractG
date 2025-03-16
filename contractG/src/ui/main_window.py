#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QMessageBox, 
    QFileDialog, QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFormLayout, QWidget,
    QTextEdit, QGroupBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QToolBar, QStatusBar, QDockWidget, QFrame, QSplitter, QApplication, QComboBox, QHeaderView
)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
import datetime

# 导入路径设置模块（如果需要）
# 注意：由于path_setup模块在导入时已经自动设置了路径，这里不需要再次导入

# 使用绝对导入
from src.ui.customer_tab import CustomerTab
from src.ui.product_tab import ProductTab
from src.ui.contract_tab import ContractTab
from src.ui.option_tab import OptionTab
from src.utils.config_manager import ConfigManager
from src.models.company import Company
from src.ui.styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, 
    WARNING_COLOR, DANGER_COLOR, LIGHT_COLOR,
    HEADING_STYLE, SUBHEADING_STYLE, CARD_STYLE
)

class CompanyInfoDialog(QDialog):
    """公司信息配置对话框"""
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("配置乙方公司")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        # 先创建所有UI元素
        self.setup_ui()
        
        # 然后加载数据和更新UI
        self.update_seal_combo()
        self.load_companies()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 增加间距
        
        # 添加标题
        title_label = QLabel("乙方公司信息管理")
        title_label.setStyleSheet(HEADING_STYLE)
        layout.addWidget(title_label)
        
        # 添加说明文字
        desc_label = QLabel("在此管理乙方公司信息，可以添加、编辑、删除公司，并设置默认公司。双击表格可以直接编辑公司信息。")
        desc_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(desc_label)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)  # 增加分割条宽度
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #BDBDBD;
            }
        """)
        
        # 左侧面板 - 公司列表
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(15)  # 增加间距
        
        # 公司列表
        list_group = QGroupBox("乙方公司列表（最多2个）")
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)  # 增加间距
        
        self.company_table = QTableWidget()
        self.company_table.setColumnCount(4)
        self.company_table.setHorizontalHeaderLabels(["公司名称", "联系人", "电话", "默认"])
        self.company_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.company_table.setSelectionMode(QTableWidget.SingleSelection)
        self.company_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止直接编辑
        self.company_table.setAlternatingRowColors(True)  # 交替行颜色
        self.company_table.horizontalHeader().setStretchLastSection(True)
        self.company_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.company_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.company_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.company_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.company_table.setColumnWidth(1, 100)  # 联系人列宽
        self.company_table.setColumnWidth(2, 120)  # 电话列宽
        self.company_table.setColumnWidth(3, 60)   # 默认列宽
        
        # 设置表格样式
        self.company_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F5F5F5;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        # 连接双击信号
        self.company_table.itemDoubleClicked.connect(self.edit_company)
        
        list_layout.addWidget(self.company_table)
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # 增加按钮间距
        
        self.add_button = QPushButton("添加公司")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("编辑公司")
        self.edit_button.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_button.clicked.connect(self.edit_company)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("删除公司")
        self.delete_button.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_button.clicked.connect(self.delete_company)
        button_layout.addWidget(self.delete_button)
        
        self.default_button = QPushButton("设为默认")
        self.default_button.setIcon(QIcon("resources/icons/star.png"))
        self.default_button.clicked.connect(self.set_default_company)
        button_layout.addWidget(self.default_button)
        
        list_layout.addLayout(button_layout)
        list_group.setLayout(list_layout)
        left_layout.addWidget(list_group)
        
        # 文本解析导入
        import_group = QGroupBox("从文本解析添加新公司")
        import_layout = QVBoxLayout()
        import_layout.setSpacing(10)  # 增加间距
        
        # 添加帮助提示
        help_text = ('提示：粘贴包含公司信息的文本，如开票信息、名片等。系统支持多种格式，包括：\n'
                    '1. 带有明确标签的文本，如"公司名称：XXX公司"\n'
                    '2. 包含税号、银行账号、电话号码等特征信息的文本\n'
                    '3. 带有地址特征（省/市/区/路）的文本\n\n'
                    '注意：最多只能添加2个公司。')
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 9pt;")
        import_layout.addWidget(help_label)
        
        self.text_import = QTextEdit()
        self.text_import.setPlaceholderText("粘贴包含公司信息的文本，系统将自动解析...")
        self.text_import.setMinimumHeight(120)
        import_layout.addWidget(self.text_import)
        
        parse_btn = QPushButton("解析并添加")
        parse_btn.clicked.connect(self.parse_text)
        parse_btn.setStyleSheet(f"background-color: {SECONDARY_COLOR};")
        parse_btn.setMinimumHeight(36)
        import_layout.addWidget(parse_btn)
        
        import_group.setLayout(import_layout)
        left_layout.addWidget(import_group)
        
        # 右侧面板 - 公司信息编辑
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(15)  # 增加间距
        
        # 公司信息表单
        form_group = QGroupBox("公司信息编辑")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)  # 增加间距
        
        # 添加提示标签
        hint_label = QLabel('在此编辑公司信息，点击"保存当前公司"按钮保存更改。\n注意：最多只能添加2个公司。')
        hint_label.setStyleSheet("color: #666; font-size: 9pt; padding: 5px; background-color: #F5F5F5; border-radius: 4px;")
        form_layout.addWidget(hint_label)
        
        # 表单字段
        fields_layout = QFormLayout()
        fields_layout.setSpacing(10)  # 增加表单项间距
        fields_layout.setLabelAlignment(Qt.AlignRight)  # 标签右对齐
        
        self.company_name = QLineEdit()
        self.company_name.setMinimumHeight(30)  # 增加输入框高度
        self.company_name.setPlaceholderText("请输入公司名称（必填）")
        
        self.contact_person = QLineEdit()
        self.contact_person.setMinimumHeight(30)
        self.contact_person.setPlaceholderText("请输入联系人姓名")
        
        self.phone = QLineEdit()
        self.phone.setMinimumHeight(30)
        self.phone.setPlaceholderText("请输入联系电话")
        
        self.address = QLineEdit()
        self.address.setMinimumHeight(30)
        self.address.setPlaceholderText("请输入公司地址")
        
        self.bank_name = QLineEdit()
        self.bank_name.setMinimumHeight(30)
        self.bank_name.setPlaceholderText("请输入开户银行名称")
        
        self.bank_account = QLineEdit()
        self.bank_account.setMinimumHeight(30)
        self.bank_account.setPlaceholderText("请输入银行账号")
        
        self.tax_id = QLineEdit()
        self.tax_id.setMinimumHeight(30)
        self.tax_id.setPlaceholderText("请输入税号")
        
        # 添加印章选择和上传功能
        self.seal_layout = QHBoxLayout()
        
        self.seal_combo = QComboBox()
        self.seal_combo.setMinimumHeight(30)
        self.seal_combo.setMinimumWidth(200)
        
        self.seal_preview = QLabel()
        self.seal_preview.setFixedSize(60, 60)
        self.seal_preview.setStyleSheet("border: 1px solid #ddd; background-color: #f9f9f9;")
        self.seal_preview.setAlignment(Qt.AlignCenter)
        
        self.seal_upload_btn = QPushButton("上传印章")
        self.seal_upload_btn.setMinimumHeight(30)
        self.seal_upload_btn.clicked.connect(self.upload_seal)
        
        self.seal_layout.addWidget(self.seal_combo)
        self.seal_layout.addWidget(self.seal_preview)
        self.seal_layout.addWidget(self.seal_upload_btn)
        
        fields_layout.addRow("公司名称:", self.company_name)
        fields_layout.addRow("联系人:", self.contact_person)
        fields_layout.addRow("电话:", self.phone)
        fields_layout.addRow("地址:", self.address)
        fields_layout.addRow("开户银行:", self.bank_name)
        fields_layout.addRow("银行账号:", self.bank_account)
        fields_layout.addRow("税号:", self.tax_id)
        fields_layout.addRow("印章:", self.seal_layout)
        
        form_layout.addLayout(fields_layout)
        
        # 保存当前公司按钮
        save_current_btn = QPushButton("保存当前公司")
        save_current_btn.clicked.connect(self.save_company)
        save_current_btn.setStyleSheet(f"background-color: {SUCCESS_COLOR};")
        save_current_btn.setMinimumHeight(40)
        form_layout.addWidget(save_current_btn)
        
        # 清空表单按钮
        clear_btn = QPushButton("清空表单")
        clear_btn.clicked.connect(self.clear_form)
        clear_btn.setMinimumHeight(36)
        form_layout.addWidget(clear_btn)
        
        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)
        
        # 添加左右面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([450, 450])  # 设置初始大小比例
        
        layout.addWidget(splitter, 1)  # 添加拉伸因子
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)  # 增加按钮间距
        
        # 保存所有更改按钮
        save_all_btn = QPushButton("确定")
        save_all_btn.clicked.connect(self.accept)
        save_all_btn.setStyleSheet(f"""
            background-color: {SUCCESS_COLOR};
            font-size: 12pt;
            font-weight: bold;
            padding: 8px 16px;
        """)
        save_all_btn.setMinimumHeight(44)
        save_all_btn.setMinimumWidth(120)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setMinimumWidth(120)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(save_all_btn)
        
        layout.addLayout(bottom_layout)
        self.setLayout(layout)
    
    def save_company(self):
        """保存当前编辑的公司信息"""
        if not self.company_name.text():
            QMessageBox.warning(self, "警告", "公司名称不能为空！")
            return
        
        company_data = {
            'name': self.company_name.text(),
            'contact': self.contact_person.text(),
            'phone': self.phone.text(),
            'address': self.address.text(),
            'bank_name': self.bank_name.text(),
            'bank_account': self.bank_account.text(),
            'tax_id': self.tax_id.text(),
            'is_default': False,
            'seal_image': self.seal_combo.currentData() or ""
        }
        
        companies = self.config_manager.get_companies()
        
        if hasattr(self, 'current_company') and self.current_company:
            # 更新现有公司
            for company in companies:
                if company.name == self.current_company.name:
                    company.__dict__.update(company_data)
                    company.is_default = self.current_company.is_default
                    break
        else:
            # 检查是否达到最大数量限制
            if len(companies) >= 2:
                QMessageBox.warning(self, "警告", "已达到最大公司数量限制（2个）！")
                return
            # 添加新公司
            new_company = Company(**company_data)
            companies.append(new_company)
        
        if self.config_manager.save_companies(companies):
            self.load_companies()
            self.clear_form()
            QMessageBox.information(self, "成功", "公司信息保存成功！")
        else:
            QMessageBox.warning(self, "错误", "保存公司信息失败！")
    
    def clear_form(self):
        """清空表单"""
        self.company_name.clear()
        self.contact_person.clear()
        self.phone.clear()
        self.address.clear()
        self.bank_name.clear()
        self.bank_account.clear()
        self.tax_id.clear()
        self.text_import.clear()
        self.seal_combo.setCurrentIndex(0)
        self.current_company = None
        self.update_seal_preview()
    
    def edit_company(self):
        """编辑选中的公司"""
        selected_rows = self.company_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个公司！")
            return
        
        row = selected_rows[0].row()
        company_item = self.company_table.item(row, 0)
        self.current_company = company_item.data(Qt.UserRole)
        
        if self.current_company:
            self.company_name.setText(self.current_company.name)
            self.contact_person.setText(self.current_company.contact)
            self.phone.setText(self.current_company.phone)
            self.address.setText(self.current_company.address)
            self.bank_name.setText(self.current_company.bank_name)
            self.bank_account.setText(self.current_company.bank_account)
            self.tax_id.setText(self.current_company.tax_id)
            
            # 设置印章
            if hasattr(self.current_company, 'seal_image') and self.current_company.seal_image:
                index = self.seal_combo.findData(self.current_company.seal_image)
                if index >= 0:
                    self.seal_combo.setCurrentIndex(index)
                else:
                    self.seal_combo.setCurrentIndex(0)
            else:
                self.seal_combo.setCurrentIndex(0)
    
    def delete_company(self):
        """删除选中的公司"""
        selected_rows = self.company_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个公司！")
            return
        
        row = selected_rows[0].row()
        company_item = self.company_table.item(row, 0)
        company = company_item.data(Qt.UserRole)
        
        if company:
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除公司 '{company.name}' 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                companies = self.config_manager.get_companies()
                # 只删除选中的公司
                companies = [c for c in companies if c.name != company.name]
                
                # 如果删除的是默认公司，且还有其他公司，将第一个公司设为默认
                if company.is_default and companies:
                    companies[0].is_default = True
                
                if self.config_manager.save_companies(companies):
                    self.load_companies()
                    self.clear_form()
                    QMessageBox.information(self, "成功", "公司已删除！")
                else:
                    QMessageBox.warning(self, "错误", "删除公司失败！")
    
    def set_default_company(self):
        """设置默认公司"""
        selected_rows = self.company_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个公司！")
            return
        
        row = selected_rows[0].row()
        company_item = self.company_table.item(row, 0)
        company = company_item.data(Qt.UserRole)
        
        if company:
            companies = self.config_manager.get_companies()
            for c in companies:
                c.is_default = (c.name == company.name)
            if self.config_manager.save_companies(companies):
                self.load_companies()
                QMessageBox.information(self, "成功", f"已将 '{company.name}' 设置为默认公司！")
            else:
                QMessageBox.warning(self, "错误", "设置默认公司失败！")
    
    def parse_text(self):
        """解析文本导入"""
        text = self.text_import.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入要解析的文本！")
            return
        
        # 检查是否达到最大数量限制
        companies = self.config_manager.get_companies()
        if len(companies) >= 2:
            QMessageBox.warning(self, "警告", "已达到最大公司数量限制（2个）！")
            return
        
        # 解析公司信息
        company_data = self.config_manager.parse_company_info(text)
        if company_data:
            # 检查公司名称是否已存在
            if any(c.name == company_data['name'] for c in companies):
                reply = QMessageBox.question(
                    self,
                    "公司已存在",
                    f"公司 '{company_data['name']}' 已存在，是否更新？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # 创建新公司对象
            new_company = Company(**company_data)
            
            # 如果是第一个公司，设置为默认
            if not companies:
                new_company.is_default = True
            
            # 添加到公司列表
            companies.append(new_company)
            
            # 保存到配置文件
            if self.config_manager.save_companies(companies):
                # 更新界面显示
                self.load_companies()
                # 清空文本输入框
                self.text_import.clear()
                QMessageBox.information(self, "成功", "公司信息已成功添加！")
            else:
                QMessageBox.warning(self, "错误", "保存公司信息失败！")
        else:
            QMessageBox.warning(self, "警告", "无法从文本中解析出公司信息！")
    
    def load_companies(self):
        """加载公司列表"""
        companies = self.config_manager.get_companies()
        
        # 清空表格
        self.company_table.setRowCount(0)
        
        # 填充表格
        for i, company in enumerate(companies):
            self.company_table.insertRow(i)
            
            # 公司名称
            name_item = QTableWidgetItem(company.name)
            name_item.setData(Qt.UserRole, company)  # 存储公司对象
            self.company_table.setItem(i, 0, name_item)
            
            # 联系人
            contact_item = QTableWidgetItem(company.contact)
            self.company_table.setItem(i, 1, contact_item)
            
            # 电话
            phone_item = QTableWidgetItem(company.phone)
            self.company_table.setItem(i, 2, phone_item)
            
            # 默认状态
            default_item = QTableWidgetItem("✓" if company.is_default else "")
            default_item.setTextAlignment(Qt.AlignCenter)
            if company.is_default:
                default_item.setForeground(QColor(SUCCESS_COLOR))
                default_item.setFont(QFont(default_item.font().family(), default_item.font().pointSize(), QFont.Bold))
            self.company_table.setItem(i, 3, default_item)
            
        # 清空表单
        self.clear_form()
    
    def update_seal_combo(self):
        """更新印章下拉框"""
        # 断开之前的信号连接，避免重复连接
        try:
            self.seal_combo.currentIndexChanged.disconnect()
        except:
            pass
            
        self.seal_combo.clear()
        self.seal_combo.addItem("无印章", "")
        
        # 获取印章目录中的所有图片
        seal_dir = os.path.join("resources", "seals")
        if os.path.exists(seal_dir):
            for file in os.listdir(seal_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.seal_combo.addItem(file, file)
        
        # 重新连接信号
        self.seal_combo.currentIndexChanged.connect(self.update_seal_preview)
        self.update_seal_preview()
    
    def update_seal_preview(self):
        """更新印章预览"""
        seal_file = self.seal_combo.currentData()
        if seal_file:
            seal_path = os.path.join("resources", "seals", seal_file)
            if os.path.exists(seal_path):
                pixmap = QPixmap(seal_path)
                self.seal_preview.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        
        # 如果没有印章或印章文件不存在，显示默认图标
        self.seal_preview.setText("无印章")
    
    def upload_seal(self):
        """上传印章图片"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择印章图片", "", 
            "图片文件 (*.png *.jpg *.jpeg)", 
            options=options
        )
        
        if file_path:
            # 确保印章目录存在
            seal_dir = os.path.join("resources", "seals")
            os.makedirs(seal_dir, exist_ok=True)
            
            # 使用税号作为文件名（如果有），否则使用时间戳
            tax_id = self.tax_id.text().strip()
            if tax_id:
                # 使用税号作为文件名
                file_ext = os.path.splitext(file_path)[1]
                target_filename = f"{tax_id}{file_ext}"
            else:
                # 如果没有税号，使用时间戳
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                file_ext = os.path.splitext(file_path)[1]
                target_filename = f"seal_{timestamp}{file_ext}"
            
            target_path = os.path.join(seal_dir, target_filename)
            
            try:
                # 复制文件
                import shutil
                shutil.copy2(file_path, target_path)
                
                # 更新下拉框并选择新上传的印章
                self.update_seal_combo()
                index = self.seal_combo.findData(target_filename)
                if index >= 0:
                    self.seal_combo.setCurrentIndex(index)
                
                QMessageBox.information(self, "成功", "印章上传成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"印章上传失败: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.check_first_run()
    
    def setup_ui(self):
        """设置UI"""
        # 设置窗口基本属性
        self.setWindowTitle("contractG")
        self.setMinimumSize(1200, 800)
        
        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow, QTabWidget, QWidget {
                background-color: #f5f5f5;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                font-size: 9pt;
                color: #333333;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 4px 12px;
                margin-right: 2px;
                color: #666666;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #333333;
                font-weight: bold;
            }
            
            QToolBar {
                background-color: #f0f0f0;
                border: none;
                spacing: 4px;
                padding: 0px;
                margin: 0px;
            }
            
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 2px;
                margin: 0px;
                color: #333333;
            }
            
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            
            QToolButton:pressed {
                background-color: #d0d0d0;
            }

            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
            }
            
            QPushButton:hover {
                background-color: #555555;
            }
            
            QPushButton:pressed {
                background-color: #444444;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }

            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                color: #333333;
                font-size: 9pt;
            }
            
            QComboBox:hover {
                border-color: #999999;
            }
            
            QComboBox:focus {
                border-color: #666666;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }

            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                color: #333333;
                font-size: 9pt;
            }
            
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                border-color: #666666;
            }

            QDialog {
                background-color: white;
                color: #333333;
            }
            
            QDialog QLabel {
                color: #333333;
                font-size: 9pt;
            }
            
            QDialog QPushButton {
                min-width: 80px;
            }

            QMessageBox {
                background-color: white;
            }
            
            QMessageBox QLabel {
                color: #333333;
                font-size: 9pt;
            }
            
            QMenuBar {
                background-color: #f5f5f5;
                color: #333333;
                border-bottom: 1px solid #e0e0e0;
            }
            
            QMenuBar::item {
                padding: 4px 8px;
                background-color: transparent;
            }
            
            QMenuBar::item:selected {
                background-color: #e0e0e0;
                color: #333333;
            }
            
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
            }
            
            QMenu::item {
                padding: 4px 20px;
                color: #333333;
            }
            
            QMenu::item:selected {
                background-color: #e0e0e0;
                color: #333333;
            }

            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 12px;
                color: #333333;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }

            QStatusBar {
                color: #666666;
            }
        """)
        
        # 创建工具栏
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setIconSize(QSize(24, 24))  # 减小图标尺寸
        self.toolbar.setMovable(False)
        self.toolbar.setContentsMargins(0, 0, 0, 0)  # 移除工具栏边距
        self.addToolBar(self.toolbar)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("欢迎使用contractG")
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setTabShape(QTabWidget.Rounded)
        self.tab_widget.setDocumentMode(True)
        
        # 创建各个标签页
        self.customer_tab = CustomerTab()
        self.product_tab = ProductTab()
        self.contract_tab = ContractTab(self.customer_tab, self.product_tab)
        self.option_tab = OptionTab()  # 新增选项页
        
        # 添加标签页到标签页控件
        self.tab_widget.addTab(self.contract_tab, "合同生成")
        self.tab_widget.addTab(self.customer_tab, "客户管理")
        self.tab_widget.addTab(self.product_tab, "商品管理")
        self.tab_widget.addTab(self.option_tab, "Excel 转 PDF")  # 新增选项页
        
        # 设置标签页图标
        self.tab_widget.setTabIcon(0, QIcon("src/resources/icons/contract.png"))
        self.tab_widget.setTabIcon(1, QIcon("src/resources/icons/customer.png"))
        self.tab_widget.setTabIcon(2, QIcon("src/resources/icons/product.png"))
        self.tab_widget.setTabIcon(3, QIcon("src/resources/icons/option.png"))
        
        # 创建中央部件
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除所有边距
        main_layout.setSpacing(0)  # 移除间距
        main_layout.addWidget(self.tab_widget)
        
        self.setCentralWidget(central_widget)
        
        # 创建菜单
        self.create_menus()
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def create_menus(self):
        """创建菜单"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        new_contract_action = QAction("新建合同", self)
        new_contract_action.setShortcut("Ctrl+N")
        new_contract_action.triggered.connect(self.new_contract)
        file_menu.addAction(new_contract_action)
        
        open_data_action = QAction("打开数据文件夹", self)
        open_data_action.triggered.connect(self.open_data_directory)
        file_menu.addAction(open_data_action)
        
        open_output_action = QAction("打开合同文件夹", self)
        open_output_action.triggered.connect(self.open_output_directory)
        file_menu.addAction(open_output_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("设置")
        
        company_config_action = QAction("公司设置", self)
        company_config_action.triggered.connect(self.show_company_config)
        edit_menu.addAction(company_config_action)
        
        # 视图菜单
        view_menu = self.menuBar().addMenu("视图")
        
        contract_tab_action = QAction("合同生成", self)
        contract_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(contract_tab_action)
        
        customer_tab_action = QAction("客户管理", self)
        customer_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(customer_tab_action)
        
        product_tab_action = QAction("商品管理", self)
        product_tab_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(product_tab_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        help_action = QAction("使用帮助", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def check_first_run(self):
        """检查是否首次运行"""
        settings = QSettings("contractG", "ContractGenerator")
        first_run = settings.value("first_run", True, type=bool)
        
        if first_run:
            # 显示欢迎信息
            QMessageBox.information(
                self,
                "欢迎使用",
                "欢迎使用contractG！\n\n"
                "首次使用请先配置您的公司信息。"
            )
            
            # 打开公司配置对话框
            self.show_company_config()
            
            # 标记为非首次运行
            settings.setValue("first_run", False)
    
    def show_company_config(self):
        """显示公司配置对话框"""
        dialog = CompanyInfoDialog(self.config_manager, self)
        dialog.exec_()
        # 更新合同标签页中的公司下拉框
        self.contract_tab.update_company_combo()
    
    def open_data_directory(self):
        """打开数据文件夹"""
        data_dir = os.path.abspath("data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.open_directory(data_dir)
    
    def open_output_directory(self):
        """打开输出文件夹"""
        output_dir = self.contract_tab.excel_handler.get_contracts_folder()
        self.open_directory(output_dir)
    
    def open_directory(self, directory):
        """打开指定目录"""
        if sys.platform == 'win32':
            os.startfile(directory)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.Popen(['open', directory])
        else:  # Linux
            import subprocess
            subprocess.Popen(['xdg-open', directory])
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "<h3>contractG</h3>"
            "<p>版本: 1.1.0</p>"
            "<p>一个简单易用的合同&报价单生成工具。</p>"
            "<p>© 2024 版权所有</p>"
        )
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        <h3>使用帮助</h3>
        <p><b>合同生成</b>: 选择客户和商品，填写合同信息后生成合同。</p>
        <p><b>客户管理</b>: 添加、编辑和删除客户信息。</p>
        <p><b>商品管理</b>: 添加、编辑和删除商品信息。</p>
        <p><b>公司设置</b>: 配置您的公司信息，用于合同乙方信息。</p>
        """
        
        QMessageBox.information(self, "使用帮助", help_text)
    
    def new_contract(self):
        """新建合同"""
        self.tab_widget.setCurrentIndex(0)  # 切换到合同标签页
        self.contract_tab.clear_contract()  # 清空当前合同
        self.statusBar.showMessage("已创建新合同")
    
    def new_customer(self):
        """新建客户"""
        self.tab_widget.setCurrentIndex(1)  # 切换到客户标签页
        self.customer_tab.add_customer()  # 打开添加客户对话框
    
    def new_product(self):
        """新建商品"""
        self.tab_widget.setCurrentIndex(2)  # 切换到商品标签页
        self.product_tab.add_product()  # 打开添加商品对话框
    
    def on_tab_changed(self, index):
        """标签页切换事件"""
        tab_names = ["合同生成", "客户管理", "商品管理", "Excel 转 PDF"]
        if index < len(tab_names):
            self.statusBar.showMessage(f"当前: {tab_names[index]}") 