#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
乙方公司模型模块
"""

class Company:
    """乙方公司模型类"""
    def __init__(self, name, contact="", phone="", address="", bank_name="", bank_account="", tax_id="", is_default=False, seal_image=""):
        """
        初始化公司信息
        
        Args:
            name (str): 公司名称
            contact (str, optional): 联系人
            phone (str, optional): 联系电话
            address (str, optional): 公司地址
            bank_name (str, optional): 开户银行
            bank_account (str, optional): 银行账号
            tax_id (str, optional): 税号
            is_default (bool, optional): 是否为默认公司
            seal_image (str, optional): 印章图片文件名
        """
        self.name = name
        self.contact = contact
        self.phone = phone
        self.address = address
        self.bank_name = bank_name
        self.bank_account = bank_account
        self.tax_id = tax_id
        self.is_default = is_default
        self.seal_image = seal_image
    
    def to_dict(self):
        """
        将公司信息转换为字典格式
        
        Returns:
            dict: 包含公司信息的字典
        """
        return {
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'address': self.address,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'tax_id': self.tax_id,
            'is_default': self.is_default,
            'seal_image': self.seal_image
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        从字典创建公司对象
        
        Args:
            data (dict): 包含公司信息的字典
            
        Returns:
            Company: 新创建的公司对象
        """
        # 确保所有必需的字段都存在
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                data[field] = ""
        
        # 设置可选字段的默认值
        optional_fields = ['contact', 'phone', 'address', 'bank_name', 'bank_account', 'tax_id', 'is_default', 'seal_image']
        for field in optional_fields:
            if field not in data:
                if field == 'is_default':
                    data[field] = False
                else:
                    data[field] = ""
        
        return cls(**data) 