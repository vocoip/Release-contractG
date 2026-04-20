#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
商品数据模型
"""

class Product:
    """商品类"""
    def __init__(self, name="", model="", unit="", price="0.00"):
        self.name = name
        self.model = model
        self.unit = unit
        # 确保价格保留两位小数
        try:
            price = float(str(price))
            self.price = f"{price:.2f}"
        except (ValueError, TypeError):
            self.price = "0.00"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'model': self.model,
            'unit': self.unit,
            'price': self.price
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建商品对象"""
        return cls(
            name=str(data.get('name', '')),
            model=str(data.get('model', '')),
            unit=str(data.get('unit', '')),
            price=str(data.get('price', '0.00'))
        ) 