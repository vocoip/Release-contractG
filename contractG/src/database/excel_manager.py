#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel数据管理模块 - 使用openpyxl替代pandas
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.models.customer import Customer
from src.models.product import Product

class ExcelManager:
    """Excel数据管理器"""
    
    def __init__(self):
        """初始化Excel管理器"""
        self.data_dir = Path(project_root) / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.customers_file = self.data_dir / "customers.xlsx"
        self.products_file = self.data_dir / "products.xlsx"
        
        # 确保数据文件存在
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """确保数据文件存在"""
        # 客户数据文件
        if not self.customers_file.exists():
            # 创建空的客户数据文件
            wb = Workbook()
            ws = wb.active
            headers = ['name', 'contact', 'phone', 'address', 'bank_name', 'bank_account', 'tax_id']
            ws.append(headers)
            wb.save(str(self.customers_file))
        
        # 商品数据文件
        if not self.products_file.exists():
            # 创建空的商品数据文件
            wb = Workbook()
            ws = wb.active
            headers = ['name', 'model', 'unit', 'price']
            ws.append(headers)
            wb.save(str(self.products_file))
    
    def load_customers(self) -> List[Customer]:
        """加载客户数据"""
        if not self.customers_file.exists():
            return []
        
        try:
            wb = load_workbook(str(self.customers_file))
            ws = wb.active
            customers = []
            
            # 获取表头
            headers = [cell.value for cell in ws[1]]
            
            # 从第二行开始读取数据
            for row in ws.iter_rows(min_row=2, values_only=True):
                # 创建行数据字典
                row_data = dict(zip(headers, row))
                
                customer = Customer(
                    name=str(row_data.get('name', '')),
                    contact=str(row_data.get('contact', '')),
                    phone=str(row_data.get('phone', '')),
                    address=str(row_data.get('address', '')),
                    bank_name=str(row_data.get('bank_name', '')),
                    bank_account=str(row_data.get('bank_account', '')),
                    tax_id=str(row_data.get('tax_id', ''))
                )
                customers.append(customer)
            
            return customers
        except Exception as e:
            raise Exception(f"读取客户数据失败：{str(e)}")
    
    def save_customers(self, customers: List[Customer]) -> bool:
        """保存客户数据"""
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            
            # 添加表头
            headers = ['name', 'contact', 'phone', 'address', 'bank_name', 'bank_account', 'tax_id']
            ws.append(headers)
            
            # 添加数据
            for customer in customers:
                row = [
                    customer.name,
                    customer.contact,
                    customer.phone,
                    customer.address,
                    customer.bank_name,
                    customer.bank_account,
                    customer.tax_id
                ]
                ws.append(row)
            
            # 保存到Excel文件
            wb.save(str(self.customers_file))
            return True
        except Exception as e:
            raise Exception(f"保存客户数据失败：{str(e)}")
    
    def import_customers(self, file_path: str) -> List[Customer]:
        """导入客户数据"""
        try:
            # 读取Excel文件
            wb = load_workbook(file_path)
            ws = wb.active
            
            # 获取表头
            headers = [cell.value for cell in ws[1]]
            
            # 验证必要的列是否存在
            required_columns = ['name', 'contact', 'phone']
            missing_columns = [col for col in required_columns if col not in headers]
            
            if missing_columns:
                # 创建模板文件
                template_path = os.path.join(os.path.dirname(file_path), "客户导入模板.xlsx")
                template_wb = Workbook()
                template_ws = template_wb.active
                template_headers = ['name', 'contact', 'phone', 'address', 'bank_name', 'bank_account', 'tax_id']
                template_ws.append(template_headers)
                template_wb.save(template_path)
                
                raise Exception(
                    f"导入文件缺少必要的列：{', '.join(missing_columns)}\n"
                    f"已在同目录下创建模板文件：{os.path.basename(template_path)}\n"
                    "请使用正确的模板文件重新导入！"
                )
            
            # 创建列名到索引的映射
            header_map = {header: idx for idx, header in enumerate(headers)}
            
            # 导入客户数据
            new_customers = []
            validation_errors = []
            
            # 从第二行开始读取数据
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
                try:
                    # 验证必填字段
                    name = str(row[header_map['name']]).strip() if row[header_map['name']] else ""
                    contact = str(row[header_map['contact']]).strip() if row[header_map['contact']] else ""
                    phone = str(row[header_map['phone']]).strip() if row[header_map['phone']] else ""
                    
                    if not name:
                        validation_errors.append(f"第 {row_idx} 行：公司名称不能为空")
                        continue
                    
                    if not contact:
                        validation_errors.append(f"第 {row_idx} 行：联系人不能为空")
                        continue
                    
                    if not phone:
                        validation_errors.append(f"第 {row_idx} 行：电话不能为空")
                        continue
                    
                    # 创建客户对象
                    customer = Customer(
                        name=name,
                        contact=contact,
                        phone=phone,
                        address=str(row[header_map.get('address', -1)] or '').strip(),
                        bank_name=str(row[header_map.get('bank_name', -1)] or '').strip(),
                        bank_account=str(row[header_map.get('bank_account', -1)] or '').strip(),
                        tax_id=str(row[header_map.get('tax_id', -1)] or '').strip()
                    )
                    new_customers.append(customer)
                
                except Exception as e:
                    validation_errors.append(f"第 {row_idx} 行：数据格式错误 - {str(e)}")
            
            # 如果有验证错误
            if validation_errors:
                if not new_customers:
                    raise Exception("导入失败：\n" + "\n".join(validation_errors))
                else:
                    # 记录警告信息，但仍然返回有效的客户数据
                    print("警告：\n" + "\n".join(validation_errors))
            
            return new_customers
        
        except Exception as e:
            raise Exception(f"导入客户数据失败：{str(e)}")
    
    def export_customers(self, customers: List[Customer], file_path: str):
        """导出客户数据"""
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = '客户数据'
            
            # 添加表头
            headers = ['公司名称', '联系人', '电话', '地址', '开户银行', '银行账号', '税号']
            ws.append(headers)
            
            # 设置表头样式
            header_font = Font(bold=True)
            for cell in ws[1]:
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
            
            # 添加数据
            for customer in customers:
                row = [
                    customer.name,
                    customer.contact,
                    customer.phone,
                    customer.address,
                    customer.bank_name,
                    customer.bank_account,
                    customer.tax_id
                ]
                ws.append(row)
            
            # 调整列宽
            for idx, col in enumerate(headers, 1):
                # 计算列的最大宽度
                max_length = len(col)
                column_letter = get_column_letter(idx)
                
                for row_idx in range(2, ws.max_row + 1):
                    cell_value = ws.cell(row=row_idx, column=idx).value
                    if cell_value:
                        max_length = max(max_length, len(str(cell_value)))
                
                ws.column_dimensions[column_letter].width = max_length + 4
            
            # 保存文件
            wb.save(file_path)
        
        except Exception as e:
            raise Exception(f"导出客户数据失败：{str(e)}")
    
    def load_products(self):
        """加载商品数据"""
        try:
            if not self.products_file.exists():
                return []
            
            wb = load_workbook(str(self.products_file))
            ws = wb.active
            products = []
            
            # 获取表头
            headers = [cell.value for cell in ws[1]]
            
            # 从第二行开始读取数据
            for row in ws.iter_rows(min_row=2, values_only=True):
                # 创建行数据字典
                row_data = dict(zip(headers, row))
                
                product = Product.from_dict(row_data)
                products.append(product)
            
            return products
        except Exception as e:
            print(f"加载商品数据出错: {e}")
            return []
    
    def save_products(self, products):
        """保存产品数据到Excel"""
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            
            # 添加表头
            headers = ['name', 'model', 'unit', 'price']
            ws.append(headers)
            
            # 添加数据
            for product in products:
                product_dict = product.to_dict()
                row = [product_dict.get(header, '') for header in headers]
                ws.append(row)
            
            # 保存到Excel文件
            wb.save(str(self.products_file))
            return True
        except Exception as e:
            print(f"保存商品数据出错: {e}")
            return False 