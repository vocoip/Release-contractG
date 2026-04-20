#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
合同数据模型
"""

class ContractItem:
    """合同商品项"""
    def __init__(self, name="", model="", unit="", price=0.0, quantity=1, amount=0.0):
        self.name = name
        self.model = model
        self.unit = unit
        self.price = price
        self.quantity = quantity
        self.amount = amount
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'model': self.model,
            'unit': self.unit,
            'price': self.price,
            'quantity': self.quantity,
            'amount': self.amount
        }


class Contract:
    """合同类"""
    def __init__(self, number="", customer=None, company=None, items=None, 
                 sign_date="", delivery_date="", payment_method="", remarks="",
                 total_amount=0.0, service_fee=0.0, grand_total=0.0,
                 quote_valid_days=30, is_draft=False):
        self.number = number
        self.customer = customer
        self.company = company
        self.items = items or []
        self.sign_date = sign_date
        self.delivery_date = delivery_date
        self.payment_method = payment_method
        self.remarks = ""  # 将默认值设为空字符串，保留字段以保持向后兼容性
        self.total_amount = total_amount
        self.service_fee = service_fee
        self.grand_total = grand_total
        self.quote_valid_days = quote_valid_days
        self.is_draft = is_draft
        
        # 添加技术服务费相关属性
        self.service_fee_enabled = True  # 默认启用
        self.service_fee_rate = 0.1  # 默认10%
        self.min_service_fee = 1500  # 默认1500元
    
    def to_dict(self):
        """转换为字典"""
        return {
            'number': self.number,
            'customer': self.customer.to_dict() if self.customer else {},
            'company': self.company,
            'items': [item.to_dict() for item in self.items],
            'sign_date': self.sign_date,
            'delivery_date': self.delivery_date,
            'payment_method': self.payment_method,
            'remarks': self.remarks,
            'total_amount': self.total_amount,
            'service_fee': self.service_fee,
            'grand_total': self.grand_total,
            'quote_valid_days': self.quote_valid_days,
            'is_draft': self.is_draft,
            # 添加技术服务费相关字段
            'service_fee_enabled': self.service_fee_enabled,
            'service_fee_rate': self.service_fee_rate,
            'min_service_fee': self.min_service_fee
        } 