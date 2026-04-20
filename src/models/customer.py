#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
客户数据模型
"""

class Customer:
    """客户类"""
    def __init__(self, name="", contact="", phone="", address="", bank_name="", bank_account="", tax_id=""):
        self.name = name
        self.contact = contact
        self.phone = phone
        self.address = address
        self.bank_name = bank_name
        self.bank_account = bank_account
        self.tax_id = tax_id
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'address': self.address,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'tax_id': self.tax_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建客户对象"""
        return cls(
            name=str(data.get('name', '')),
            contact=str(data.get('contact', '')),
            phone=str(data.get('phone', '')),
            address=str(data.get('address', '')),
            bank_name=str(data.get('bank_name', '')),
            bank_account=str(data.get('bank_account', '')),
            tax_id=str(data.get('tax_id', ''))
        ) 