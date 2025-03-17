#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
客户管理页面模块
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import time

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
                            QMessageBox, QFileDialog, QHeaderView, QCheckBox,
                            QStyle, QApplication, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPalette

# 注意：路径设置已由path_setup模块处理，不需要在这里重复设置

from src.models.customer import Customer
from src.database.excel_manager import ExcelManager
from src.ui.dialogs.customer_dialog import CustomerDialog
from src.utils.text_parser import TextParser
from pypinyin import lazy_pinyin, Style

class CustomerTableItem(QTableWidgetItem):
    """自定义表格项，支持排序"""
    def __init__(self, text: str, sort_key: str = None):
        super().__init__(text)
        self.sort_key = sort_key or text.lower()
    
    def __lt__(self, other):
        return self.sort_key < other.sort_key

class CustomerTab(QWidget):
    """客户管理页面"""
    
    # 定义信号
    customer_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        """初始化页面"""
        super().__init__(parent)
        self.excel_manager = ExcelManager()
        self.customers: List[Customer] = []
        self.filtered_customers: List[Customer] = []
        self.search_timer: Optional[QTimer] = None
        self.setup_ui()
        self.load_customers()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 添加统计信息区域
        self.setup_stats_area(layout)
        
        # 搜索和操作按钮区域
        self.setup_toolbar(layout)
        
        # 批量操作区域
        self.setup_batch_operations(layout)
        
        # 客户列表表格
        self.setup_table(layout)
        
        self.setLayout(layout)
    
    def setup_stats_area(self, layout):
        """设置统计信息区域"""
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #495057;
                font-size: 12px;
            }
        """)
        
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("总客户数: 0")
        self.filtered_label = QLabel("筛选结果: 0")
        self.selected_label = QLabel("已选择: 0")
        
        for label in [self.total_label, self.filtered_label, self.selected_label]:
            stats_layout.addWidget(label)
            stats_layout.addSpacing(20)
        
        stats_layout.addStretch()
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
    
    def setup_toolbar(self, layout):
        """设置工具栏"""
        toolbar_layout = QHBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_icon = QLabel()
        search_icon.setPixmap(QApplication.style().standardPixmap(QStyle.SP_FileDialogContentsView))
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键字进行搜索（公司名称、联系人、电话等）")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border: 2px solid #80bdff;
                outline: 0;
            }
        """)
        search_layout.addWidget(self.search_input)
        toolbar_layout.addLayout(search_layout)
        
        # 添加按钮样式
        button_style = """
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                min-height: 30px;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QPushButton:pressed {
                opacity: 1;
            }
        """
        
        # 添加客户按钮
        add_button = QPushButton("添加客户")
        add_button.setStyleSheet(button_style + "background-color: #28a745;")
        add_button.clicked.connect(self.add_customer)
        toolbar_layout.addWidget(add_button)
        
        # 导入导出按钮
        import_button = QPushButton("导入")
        import_button.setStyleSheet(button_style + "background-color: #17a2b8;")
        import_button.clicked.connect(self.import_customers)
        
        export_button = QPushButton("导出")
        export_button.setStyleSheet(button_style + "background-color: #6c757d;")
        export_button.clicked.connect(self.export_customers)
        
        toolbar_layout.addWidget(import_button)
        toolbar_layout.addWidget(export_button)
        
        layout.addLayout(toolbar_layout)
    
    def setup_batch_operations(self, layout):
        """设置批量操作区域"""
        batch_layout = QHBoxLayout()
        
        # 全选复选框
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        batch_layout.addWidget(self.select_all_checkbox)
        
        # 批量删除按钮
        self.batch_delete_button = QPushButton("批量删除")
        self.batch_delete_button.setEnabled(False)
        self.batch_delete_button.clicked.connect(self.batch_delete_customers)
        self.batch_delete_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
                min-height: 30px;
                background-color: #dc3545;
                color: white;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                opacity: 0.65;
            }
        """)
        batch_layout.addWidget(self.batch_delete_button)
        
        batch_layout.addStretch()
        layout.addLayout(batch_layout)
    
    def setup_table(self, layout):
        """设置表格"""
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # 增加一列用于复选框
        self.table.setHorizontalHeaderLabels([
            "选择", "公司名称", "联系人", "电话", "地址",
            "开户银行", "银行账号", "税号", "操作"
        ])
        
        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                selection-background-color: #e8f0fe;
                selection-color: #000;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 公司名称列自适应
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # 地址列自适应
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 50)   # 选择
        self.table.setColumnWidth(2, 100)  # 联系人
        self.table.setColumnWidth(3, 120)  # 电话
        self.table.setColumnWidth(5, 150)  # 开户银行
        self.table.setColumnWidth(6, 180)  # 银行账号
        self.table.setColumnWidth(7, 180)  # 税号
        self.table.setColumnWidth(8, 120)  # 操作按钮
        
        # 启用排序
        self.table.setSortingEnabled(True)
        
        # 连接信号
        self.table.itemSelectionChanged.connect(self.update_stats)
        
        layout.addWidget(self.table)
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.customers)
        filtered = len(self.filtered_customers)
        selected = len(self.get_selected_rows())
        
        self.total_label.setText(f"总客户数: {total}")
        self.filtered_label.setText(f"筛选结果: {filtered}")
        self.selected_label.setText(f"已选择: {selected}")
        
        # 更新批量删除按钮状态
        self.batch_delete_button.setEnabled(selected > 0)
    
    def get_selected_rows(self) -> List[int]:
        """获取选中的行"""
        selected_rows = []
        for row in range(self.table.rowCount()):
            checkbox_item = self.table.cellWidget(row, 0)
            if checkbox_item and checkbox_item.isChecked():
                selected_rows.append(row)
        return selected_rows
    
    def on_select_all_changed(self, state):
        """全选复选框状态改变"""
        for row in range(self.table.rowCount()):
            checkbox_item = self.table.cellWidget(row, 0)
            if checkbox_item:
                checkbox_item.setChecked(state == Qt.Checked)
    
    def batch_delete_customers(self):
        """批量删除客户"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(selected_rows)} 个客户吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 从后往前删除，避免索引变化
                for row in sorted(selected_rows, reverse=True):
                    customer = self.filtered_customers[row]
                    self.customers.remove(customer)
                    self.filtered_customers.remove(customer)
                
                # 保存更改
                self.excel_manager.save_customers(self.customers)
                
                # 更新表格显示
                self.update_table()
                
                QMessageBox.information(self, "成功", f"成功删除 {len(selected_rows)} 个客户")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除客户时发生错误：{str(e)}")
    
    def update_table(self):
        """更新表格显示"""
        # 保存当前的排序状态
        sort_column = self.table.horizontalHeader().sortIndicatorSection()
        sort_order = self.table.horizontalHeader().sortIndicatorOrder()
        
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_customers))
        
        for row, customer in enumerate(self.filtered_customers):
            # 添加选择复选框
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.update_stats)
            self.table.setCellWidget(row, 0, checkbox)
            
            # 设置单元格内容
            self.table.setItem(row, 1, CustomerTableItem(customer.name))
            self.table.setItem(row, 2, CustomerTableItem(customer.contact))
            self.table.setItem(row, 3, CustomerTableItem(customer.phone))
            self.table.setItem(row, 4, CustomerTableItem(customer.address))
            self.table.setItem(row, 5, CustomerTableItem(customer.bank_name))
            self.table.setItem(row, 6, CustomerTableItem(customer.bank_account))
            self.table.setItem(row, 7, CustomerTableItem(customer.tax_id))
            
            # 创建操作按钮容器
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(5)
            
            # 编辑按钮
            edit_button = QPushButton("编辑")
            edit_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 10px;
                    border: none;
                    border-radius: 3px;
                    background-color: #007bff;
                    color: white;
                }
            """)
            edit_button.clicked.connect(lambda checked, r=row: self.edit_customer(r))
            button_layout.addWidget(edit_button)
            
            # 删除按钮
            delete_button = QPushButton("删除")
            delete_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 10px;
                    border: none;
                    border-radius: 3px;
                    background-color: #dc3545;
                    color: white;
                }
            """)
            delete_button.clicked.connect(lambda checked, r=row: self.delete_customer(r))
            button_layout.addWidget(delete_button)
            
            button_widget.setLayout(button_layout)
            self.table.setCellWidget(row, 8, button_widget)
        
        # 恢复排序
        self.table.setSortingEnabled(True)
        self.table.sortItems(sort_column, sort_order)
        
        # 更新统计信息
        self.update_stats()
    
    def load_customers(self):
        """加载客户数据"""
        try:
            self.customers = self.excel_manager.load_customers()
            self.filtered_customers = self.customers.copy()
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载客户数据时发生错误：{str(e)}")
    
    def on_search_text_changed(self):
        """搜索文本变化时的处理"""
        # 重置定时器
        if self.search_timer is not None:
            self.search_timer.stop()
        else:
            self.search_timer = QTimer()
            self.search_timer.setSingleShot(True)
            self.search_timer.timeout.connect(self._do_search)
        
        # 延迟300毫秒执行搜索
        self.search_timer.start(300)
    
    def _do_search(self):
        """执行搜索"""
        search_text = self.search_input.text().strip().lower()
        
        if not search_text:
            self.filtered_customers = self.customers.copy()
        else:
            # 支持多关键字搜索
            keywords = search_text.split()
            self.filtered_customers = []
            
            for customer in self.customers:
                # 获取拼音和首字母
                name_pinyin = ''.join(lazy_pinyin(customer.name or ''))  # 完整拼音
                name_initials = ''.join([p[0] for p in lazy_pinyin(customer.name or '')])  # 拼音首字母
                name_pinyin_initials = ''.join(lazy_pinyin(customer.name or '', style=Style.FIRST_LETTER))  # 专门的首字母模式
                
                contact_pinyin = ''.join(lazy_pinyin(customer.contact or ''))
                contact_initials = ''.join([p[0] for p in lazy_pinyin(customer.contact or '')])
                contact_pinyin_initials = ''.join(lazy_pinyin(customer.contact or '', style=Style.FIRST_LETTER))
                
                # 检查所有搜索字段
                searchable_fields = [
                    customer.name or '',
                    customer.contact or '',
                    customer.phone or '',
                    customer.address or '',
                    customer.bank_name or '',
                    customer.bank_account or '',
                    customer.tax_id or '',
                    name_pinyin,
                    name_initials,
                    name_pinyin_initials,
                    contact_pinyin,
                    contact_initials,
                    contact_pinyin_initials
                ]
                
                # 所有关键字都必须匹配
                if all(any(keyword in field.lower() for field in searchable_fields) for keyword in keywords):
                    self.filtered_customers.append(customer)
        
        self.update_table()
    
    def add_customer(self):
        """添加客户"""
        dialog = CustomerDialog(parent=self)
        dialog.customer_saved.connect(self._on_customer_saved)
        dialog.exec_()
    
    def edit_customer(self, row):
        """编辑客户"""
        customer = self.filtered_customers[row]
        dialog = CustomerDialog(customer, parent=self)
        dialog.customer_saved.connect(lambda new_customer: self._on_customer_edited(row, new_customer))
        dialog.exec_()
    
    def delete_customer(self, row):
        """删除客户"""
        customer = self.filtered_customers[row]
        reply = QMessageBox.question(
            self,
            "确认删除",
            f'确定要删除客户"{customer.name}"吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 从数据列表中删除
                self.customers.remove(customer)
                self.filtered_customers.remove(customer)
                
                # 保存更改
                self.excel_manager.save_customers(self.customers)
                
                # 更新表格显示
                self.update_table()
                
                QMessageBox.information(self, "成功", "客户删除成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除客户时发生错误：{str(e)}")
    
    def _on_customer_saved(self, customer):
        """新客户保存时的处理"""
        try:
            # 添加到数据列表
            self.customers.append(customer)
            
            # 保存更改
            self.excel_manager.save_customers(self.customers)
            
            # 更新搜索结果
            self._do_search()
            
            QMessageBox.information(self, "成功", "客户添加成功")
            
            # 发送更新信号
            self.customer_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存客户时发生错误：{str(e)}")
    
    def _on_customer_edited(self, row, new_customer):
        """客户编辑完成时的处理"""
        try:
            # 更新数据列表
            old_customer = self.filtered_customers[row]
            index = self.customers.index(old_customer)
            self.customers[index] = new_customer
            self.filtered_customers[row] = new_customer
            
            # 保存更改
            self.excel_manager.save_customers(self.customers)
            
            # 更新表格显示
            self.update_table()
            
            QMessageBox.information(self, "成功", "客户信息更新成功")
            
            # 发送更新信号
            self.customer_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新客户信息时发生错误：{str(e)}")
    
    def import_customers(self):
        """导入客户数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择导入文件",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 导入数据
            new_customers, validation_errors = self.excel_manager.import_customers(file_path)
            
            # 显示验证错误
            if validation_errors:
                error_message = "\n".join(validation_errors[:10])
                if len(validation_errors) > 10:
                    error_message += f"\n... 以及其他 {len(validation_errors) - 10} 个错误"
                QMessageBox.warning(self, "导入警告", f"导入过程中发现以下问题：\n{error_message}")
            
            # 更新数据列表
            self.customers.extend(new_customers)
            
            # 保存更改
            self.excel_manager.save_customers(self.customers)
            
            # 更新显示
            self._do_search()
            
            QMessageBox.information(self, "成功", f"成功导入 {len(new_customers)} 条客户数据")
            
            # 发送更新信号
            self.customer_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入客户数据时发生错误：{str(e)}")
    
    def export_customers(self):
        """导出客户数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择导出位置",
            "",
            "Excel Files (*.xlsx);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 确保文件扩展名为.xlsx
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # 导出数据
            self.excel_manager.export_customers(self.filtered_customers, file_path)
            
            QMessageBox.information(self, "成功", "客户数据导出成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出客户数据时发生错误：{str(e)}")
    
    def get_customers(self):
        """获取所有客户"""
        return self.customers 