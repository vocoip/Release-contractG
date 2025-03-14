#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel数据管理模块
"""

import os
import sys
from pathlib import Path
from typing import List
import pandas as pd
import json

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
            df = pd.DataFrame(columns=[
                'name', 'contact', 'phone', 'address', 
                'bank_name', 'bank_account', 'tax_id'
            ])
            df.to_excel(self.customers_file, index=False)
        
        # 商品数据文件
        if not self.products_file.exists():
            # 创建空的商品数据文件
            df = pd.DataFrame(columns=['name', 'model', 'unit', 'price'])
            df.to_excel(self.products_file, index=False)
    
    def load_customers(self) -> List[Customer]:
        """加载客户数据"""
        if not self.customers_file.exists():
            return []
        
        try:
            df = pd.read_excel(str(self.customers_file))
            customers = []
            
            for _, row in df.iterrows():
                customer = Customer(
                    name=str(row.get('name', '')),
                    contact=str(row.get('contact', '')),
                    phone=str(row.get('phone', '')),
                    address=str(row.get('address', '')),
                    bank_name=str(row.get('bank_name', '')),
                    bank_account=str(row.get('bank_account', '')),
                    tax_id=str(row.get('tax_id', ''))
                )
                customers.append(customer)
            
            return customers
        except Exception as e:
            raise Exception(f"读取客户数据失败：{str(e)}")
    
    def save_customers(self, customers: List[Customer]) -> bool:
        """保存客户数据"""
        try:
            # 转换为DataFrame
            data = []
            for customer in customers:
                data.append({
                    'name': customer.name,
                    'contact': customer.contact,
                    'phone': customer.phone,
                    'address': customer.address,
                    'bank_name': customer.bank_name,
                    'bank_account': customer.bank_account,
                    'tax_id': customer.tax_id
                })
            
            df = pd.DataFrame(data)
            
            # 保存到Excel文件
            df.to_excel(str(self.customers_file), index=False)
            return True
        except Exception as e:
            raise Exception(f"保存客户数据失败：{str(e)}")
    
    def import_customers(self, file_path: str) -> List[Customer]:
        """导入客户数据"""
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 验证必要的列是否存在
            required_columns = ['name', 'contact', 'phone']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # 创建模板文件
                template_path = os.path.join(os.path.dirname(file_path), "客户导入模板.xlsx")
                template_df = pd.DataFrame(columns=['name', 'contact', 'phone', 'address', 'bank_name', 'bank_account', 'tax_id'])
                template_df.to_excel(template_path, index=False)
                
                raise Exception(
                    f"导入文件缺少必要的列：{', '.join(missing_columns)}\n"
                    f"已在同目录下创建模板文件：{os.path.basename(template_path)}\n"
                    "请使用正确的模板文件重新导入！"
                )
            
            # 导入客户数据
            new_customers = []
            validation_errors = []
            
            for index, row in df.iterrows():
                try:
                    # 验证必填字段
                    name = str(row['name']).strip()
                    contact = str(row['contact']).strip()
                    phone = str(row['phone']).strip()
                    
                    if not name:
                        validation_errors.append(f"第 {index + 2} 行：公司名称不能为空")
                        continue
                    
                    if not contact:
                        validation_errors.append(f"第 {index + 2} 行：联系人不能为空")
                        continue
                    
                    if not phone:
                        validation_errors.append(f"第 {index + 2} 行：电话不能为空")
                        continue
                    
                    # 创建客户对象
                    customer = Customer(
                        name=name,
                        contact=contact,
                        phone=phone,
                        address=str(row.get('address', '')).strip(),
                        bank_name=str(row.get('bank_name', '')).strip(),
                        bank_account=str(row.get('bank_account', '')).strip(),
                        tax_id=str(row.get('tax_id', '')).strip()
                    )
                    new_customers.append(customer)
                
                except Exception as e:
                    validation_errors.append(f"第 {index + 2} 行：数据格式错误 - {str(e)}")
            
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
            # 转换为DataFrame
            data = []
            for customer in customers:
                data.append({
                    '公司名称': customer.name,
                    '联系人': customer.contact,
                    '电话': customer.phone,
                    '地址': customer.address,
                    '开户银行': customer.bank_name,
                    '银行账号': customer.bank_account,
                    '税号': customer.tax_id
                })
            
            df = pd.DataFrame(data)
            
            # 设置Excel写入器
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            
            # 写入数据
            df.to_excel(writer, index=False, sheet_name='客户数据')
            
            # 获取工作表
            worksheet = writer.sheets['客户数据']
            
            # 调整列宽
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),  # 最长数据长度
                    len(col)  # 列名长度
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 4
            
            # 保存文件
            writer.close()
        
        except Exception as e:
            raise Exception(f"导出客户数据失败：{str(e)}")
    
    def load_products(self):
        """加载商品数据"""
        try:
            if not self.products_file.exists():
                return []
            
            df = pd.read_excel(str(self.products_file))
            products = []
            
            for _, row in df.iterrows():
                product = Product.from_dict(row.to_dict())
                products.append(product)
            
            return products
        except Exception as e:
            print(f"加载商品数据出错: {e}")
            return []
    
    def save_products(self, products):
        """保存产品数据到Excel"""
        try:
            data = [product.to_dict() for product in products]
            df = pd.DataFrame(data)
            df.to_excel(str(self.products_file), index=False)
            return True
        except Exception as e:
            print(f"保存商品数据出错: {e}")
            return False 