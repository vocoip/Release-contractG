#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel数据管理模块 - 使用openpyxl替代pandas
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.models.customer import Customer
from src.models.product import Product
from src.utils.excel_utils import ExcelUtils

class ExcelManager:
    """Excel数据管理器"""
    
    # 客户数据相关常量
    CUSTOMER_HEADERS = ['name', 'contact', 'phone', 'address', 'bank_name', 'bank_account', 'tax_id']
    CUSTOMER_HEADER_NAMES = ['公司名称', '联系人', '电话', '地址', '开户银行', '银行账号', '税号']
    CUSTOMER_REQUIRED = ['name']  # 只保留公司名称作为必填字段
    
    # 商品数据相关常量
    PRODUCT_HEADERS = ['name', 'model', 'unit', 'price']
    PRODUCT_HEADER_NAMES = ['商品名称', '规格型号', '单位', '单价(元)']
    PRODUCT_REQUIRED = ['name', 'price']
    
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
            # 创建客户数据示例
            customer_examples = [
                {
                    'name': '示例公司1',
                    'contact': '张三',
                    'phone': '13800138000',
                    'address': '北京市朝阳区xxx街道1号',
                    'bank_name': '中国工商银行北京分行',
                    'bank_account': '6222021234567890123',
                    'tax_id': '91110000123456789A'
                },
                {
                    'name': '示例公司2',
                    'contact': '李四',
                    'phone': '13900139000',
                    'address': '上海市浦东新区xxx路2号',
                    'bank_name': '中国建设银行上海分行',
                    'bank_account': '6227002234567890123',
                    'tax_id': '91310000123456789B'
                }
            ]
            
            ExcelUtils.create_template(
                str(self.customers_file),
                self.CUSTOMER_HEADERS,
                self.CUSTOMER_HEADER_NAMES,
                self.CUSTOMER_REQUIRED,
                customer_examples
            )
        
        # 商品数据文件
        if not self.products_file.exists():
            # 创建商品数据示例
            product_examples = [
                {
                    'name': '示例商品1',
                    'model': 'XH-001',
                    'unit': '个',
                    'price': '100.00'
                },
                {
                    'name': '示例商品2',
                    'model': 'XH-002',
                    'unit': '件',
                    'price': '200.00'
                }
            ]
            
            ExcelUtils.create_template(
                str(self.products_file),
                self.PRODUCT_HEADERS,
                self.PRODUCT_HEADER_NAMES,
                self.PRODUCT_REQUIRED,
                product_examples
            )
    
    def load_customers(self) -> List[Customer]:
        """加载客户数据"""
        if not self.customers_file.exists():
            return []
        
        try:
            # 定义行验证函数
            def validate_customer(row_data: Dict[str, Any], row_idx: int) -> Optional[str]:
                # 验证必填字段
                for field in self.CUSTOMER_REQUIRED:
                    if not row_data.get(field):
                        return f"{dict(zip(self.CUSTOMER_HEADERS, self.CUSTOMER_HEADER_NAMES))[field]}不能为空"
                return None
            
            # 定义行处理函数
            def process_customer(row_data: Dict[str, Any]) -> Customer:
                # 清理数据
                cleaned_data = {
                    'name': str(row_data.get('name', '')).strip(),
                    'contact': str(row_data.get('contact', '')).strip(),
                    'phone': str(row_data.get('phone', '')).strip(),
                    'address': str(row_data.get('address', '')).strip(),
                    'bank_name': str(row_data.get('bank_name', '')).strip(),
                    'bank_account': str(row_data.get('bank_account', '')).strip(),
                    'tax_id': str(row_data.get('tax_id', '')).strip().upper()  # 税号转大写
                }
                return Customer(**cleaned_data)
            
            # 导入数据
            customers, errors = ExcelUtils.import_data(
                str(self.customers_file),
                self.CUSTOMER_HEADERS,
                self.CUSTOMER_HEADER_NAMES,
                self.CUSTOMER_REQUIRED,
                validate_customer,
                process_customer
            )
            
            if errors:
                print("警告：\n" + "\n".join(errors))
            
            return customers
            
        except Exception as e:
            raise Exception(f"读取客户数据失败：{str(e)}")
    
    def save_customers(self, customers: List[Customer]) -> bool:
        """保存客户数据"""
        try:
            # 定义行格式化函数
            def format_customer(customer: Customer) -> List[Any]:
                if not isinstance(customer, Customer):
                    raise TypeError(f"期望 Customer 对象，但收到 {type(customer)}")
                customer_dict = customer.to_dict()
                return [customer_dict.get(header, '') for header in self.CUSTOMER_HEADERS]
            
            # 导出数据
            ExcelUtils.export_data(
                str(self.customers_file),
                self.CUSTOMER_HEADERS,
                self.CUSTOMER_HEADER_NAMES,
                customers,
                format_customer
            )
            return True
            
        except Exception as e:
            raise Exception(f"保存客户数据失败：{str(e)}")
    
    def import_customers(self, file_path: str, progress_callback=None) -> Tuple[List[Customer], List[str]]:
        """导入客户数据"""
        try:
            # 定义行验证函数
            def validate_customer(row_data: Dict[str, Any], row_idx: int) -> Optional[str]:
                # 验证必填字段
                for field in self.CUSTOMER_REQUIRED:
                    if not row_data.get(field):
                        return f"{dict(zip(self.CUSTOMER_HEADERS, self.CUSTOMER_HEADER_NAMES))[field]}不能为空"
                
                # 所有其他验证规则已移除
                return None
            
            # 定义行处理函数
            def process_customer(row_data: Dict[str, Any]) -> Customer:
                # 清理数据
                cleaned_data = {
                    'name': str(row_data.get('name', '')).strip(),
                    'contact': str(row_data.get('contact', '')).strip(),
                    'phone': str(row_data.get('phone', '')).strip(),
                    'address': str(row_data.get('address', '')).strip(),
                    'bank_name': str(row_data.get('bank_name', '')).strip(),
                    'bank_account': str(row_data.get('bank_account', '')).strip(),
                    'tax_id': str(row_data.get('tax_id', '')).strip()  # 不再转大写
                }
                return Customer(**cleaned_data)
            
            # 导入数据
            return ExcelUtils.import_data(
                file_path,
                self.CUSTOMER_HEADERS,
                self.CUSTOMER_HEADER_NAMES,
                self.CUSTOMER_REQUIRED,
                validate_customer,
                process_customer,
                progress_callback
            )
            
        except Exception as e:
            raise Exception(f"导入客户数据失败：{str(e)}")
    
    def export_customers(self, customers: List[Customer], file_path: str, progress_callback=None):
        """导出客户数据"""
        try:
            # 定义行格式化函数
            def format_customer(customer: Customer) -> List[Any]:
                if not isinstance(customer, Customer):
                    raise TypeError(f"期望 Customer 对象，但收到 {type(customer)}")
                customer_dict = customer.to_dict()
                return [customer_dict.get(header, '') for header in self.CUSTOMER_HEADERS]
            
            # 导出数据
            ExcelUtils.export_data(
                file_path,
                self.CUSTOMER_HEADERS,
                self.CUSTOMER_HEADER_NAMES,
                customers,
                format_customer,
                progress_callback
            )
            
        except Exception as e:
            raise Exception(f"导出客户数据失败：{str(e)}")
    
    def load_products(self) -> List[Product]:
        """加载商品数据"""
        if not self.products_file.exists():
            return []
        
        try:
            # 定义行验证函数
            def validate_product(row_data: Dict[str, Any], row_idx: int) -> Optional[str]:
                # 验证必填字段
                for field in self.PRODUCT_REQUIRED:
                    if not row_data.get(field):
                        return f"{dict(zip(self.PRODUCT_HEADERS, self.PRODUCT_HEADER_NAMES))[field]}不能为空"
                
                # 验证价格格式
                try:
                    if row_data.get('price'):
                        float(row_data['price'])
                except ValueError:
                    return "单价必须是有效的数字"
                
                return None
            
            # 定义行处理函数
            def process_product(row_data: Dict[str, Any]) -> Product:
                return Product.from_dict(row_data)
            
            # 导入数据
            products, errors = ExcelUtils.import_data(
                str(self.products_file),
                self.PRODUCT_HEADERS,
                self.PRODUCT_HEADER_NAMES,
                self.PRODUCT_REQUIRED,
                validate_product,
                process_product
            )
            
            if errors:
                print("警告：\n" + "\n".join(errors))
            
            return products
            
        except Exception as e:
            raise Exception(f"读取商品数据失败：{str(e)}")
    
    def save_products(self, products: List[Product]) -> bool:
        """保存商品数据"""
        try:
            # 定义行格式化函数
            def format_product(product: Product) -> List[Any]:
                product_dict = product.to_dict()
                return [product_dict.get(header, '') for header in self.PRODUCT_HEADERS]
            
            # 导出数据
            ExcelUtils.export_data(
                str(self.products_file),
                self.PRODUCT_HEADERS,
                self.PRODUCT_HEADER_NAMES,
                products,
                format_product
            )
            return True
            
        except Exception as e:
            raise Exception(f"保存商品数据失败：{str(e)}")
    
    def import_products(self, file_path: str, progress_callback=None) -> Tuple[List[Product], List[str]]:
        """导入商品数据"""
        try:
            # 定义行验证函数
            def validate_product(row_data: Dict[str, Any], row_idx: int) -> Optional[str]:
                # 验证必填字段
                for field in self.PRODUCT_REQUIRED:
                    if not row_data.get(field):
                        return f"{dict(zip(self.PRODUCT_HEADERS, self.PRODUCT_HEADER_NAMES))[field]}不能为空"
                
                # 验证价格格式
                try:
                    if row_data.get('price'):
                        float(row_data['price'])
                except ValueError:
                    return "单价必须是有效的数字"
                
                return None
            
            # 定义行处理函数
            def process_product(row_data: Dict[str, Any]) -> Product:
                return Product.from_dict(row_data)
            
            # 导入数据
            return ExcelUtils.import_data(
                file_path,
                self.PRODUCT_HEADERS,
                self.PRODUCT_HEADER_NAMES,
                self.PRODUCT_REQUIRED,
                validate_product,
                process_product,
                progress_callback
            )
            
        except Exception as e:
            raise Exception(f"导入商品数据失败：{str(e)}")
    
    def export_products(self, products: List[Product], file_path: str, progress_callback=None):
        """导出商品数据"""
        try:
            # 定义行格式化函数
            def format_product(product: Product) -> List[Any]:
                product_dict = product.to_dict()
                return [product_dict.get(header, '') for header in self.PRODUCT_HEADERS]
            
            # 导出数据
            ExcelUtils.export_data(
                file_path,
                self.PRODUCT_HEADERS,
                self.PRODUCT_HEADER_NAMES,
                products,
                format_product,
                progress_callback
            )
            
        except Exception as e:
            raise Exception(f"导出商品数据失败：{str(e)}")
    
    def create_customer_template(self, file_path: str) -> str:
        """创建客户导入模板"""
        example_data = [
            {
                'name': '北京示例科技有限公司',
                'contact': '张三',
                'phone': '13800138000',
                'address': '北京市朝阳区望京街道望京SOHO塔1-A座10层1001室',
                'bank_name': '中国工商银行北京望京支行',
                'bank_account': '6222021234567890123',
                'tax_id': '91110105MA12345678'
            },
            {
                'name': '上海示例贸易有限公司',
                'contact': '李四',
                'phone': '13900139000',
                'address': '上海市浦东新区陆家嘴环路1000号恒生银行大厦25楼',
                'bank_name': '中国建设银行上海陆家嘴支行',
                'bank_account': '6227002234567890123',
                'tax_id': '91310115MA87654321'
            }
        ]
        return ExcelUtils.create_template(
            file_path,
            self.CUSTOMER_HEADERS,
            self.CUSTOMER_HEADER_NAMES,
            self.CUSTOMER_REQUIRED,
            example_data
        )
    
    def create_product_template(self, file_path: str) -> str:
        """创建商品导入模板"""
        example_data = [
            {
                'name': '示例商品',
                'model': 'XYZ-123',
                'unit': '台',
                'price': '1000.00'
            }
        ]
        return ExcelUtils.create_template(
            file_path,
            self.PRODUCT_HEADERS,
            self.PRODUCT_HEADER_NAMES,
            self.PRODUCT_REQUIRED,
            example_data
        ) 