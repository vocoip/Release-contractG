#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本解析工具模块
"""

import re

class TextParser:
    """文本解析工具类"""
    
    @staticmethod
    def parse_customer_info(text):
        """解析客户信息"""
        if not text:
            return None
        
        # 预处理：移除空行，整理格式
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 定义关键词映射
        keyword_mappings = {
            'name': ['名称', '公司名称', '单位名称', '企业名称', '公司', '单位'],
            'contact': ['联系人', '负责人', '经办人', '联系'],
            'phone': ['电话', '手机', '联系方式', '联系电话', '手机号码', '电话号码', '联系号码', '号码'],
            'address': ['地址', '单位地址', '公司地址', '详细地址', '住所', '所在地'],
            'bank_name': ['开户银行', '开户行', '银行名称', '银行'],
            'bank_account': ['账号', '银行账号', '账户', '银行账户', '账户号码'],
            'tax_id': ['税号', '纳税人识别号', '税务登记号', '纳税识别号', '统一社会信用代码']
        }
        
        # 存储提取的信息
        extracted_info = {
            'name': '',
            'contact': '',
            'phone': '',
            'address': '',
            'bank_name': '',
            'bank_account': '',
            'tax_id': ''
        }
        
        # 第一轮：寻找明确的"关键词:值"格式
        for line in lines:
            # 尝试分割行（支持多种分隔符）
            for separator in [':', '：', ' ', '　']:
                if separator in line:
                    parts = line.split(separator, 1)
                    key_part = parts[0].strip()
                    value_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    # 检查这个键是否匹配任何我们的关键词
                    for field, keywords in keyword_mappings.items():
                        if any(keyword in key_part for keyword in keywords):
                            if not extracted_info[field] and value_part:  # 只在字段为空时填充
                                extracted_info[field] = value_part
                            break
                    break
        
        # 第二轮：处理特殊情况和没有明确分隔符的情况
        for line in lines:
            # 处理税号（通常是15-20位数字和字母的组合）
            if not extracted_info['tax_id']:
                tax_id_pattern = r'[A-Z0-9]{15,20}'
                tax_matches = re.findall(tax_id_pattern, line)
                if tax_matches:
                    extracted_info['tax_id'] = tax_matches[0]
            
            # 处理银行账号（通常是纯数字）
            if not extracted_info['bank_account']:
                account_pattern = r'\d{16,19}'
                account_matches = re.findall(account_pattern, line)
                if account_matches and not any(keyword in line for keyword in keyword_mappings['tax_id']):
                    extracted_info['bank_account'] = account_matches[0]
            
            # 处理电话号码
            if not extracted_info['phone']:
                phone_pattern = r'(?:1[3-9]\d{9}|0\d{2,3}-\d{7,8})'
                phone_matches = re.findall(phone_pattern, line)
                if phone_matches:
                    extracted_info['phone'] = phone_matches[0]
        
        # 第三轮：使用上下文关系推断
        for i, line in enumerate(lines):
            # 如果一行包含"银行"但不是开户银行行，可能是下一行包含账号
            if '银行' in line and not extracted_info['bank_name']:
                extracted_info['bank_name'] = line
                if i + 1 < len(lines) and not extracted_info['bank_account']:
                    next_line = lines[i + 1]
                    if any(keyword in next_line for keyword in keyword_mappings['bank_account']):
                        parts = next_line.split(':', 1) if ':' in next_line else next_line.split('：', 1) if '：' in next_line else [next_line]
                        extracted_info['bank_account'] = parts[-1].strip()
            
            # 如果地址字段为空，查找可能的地址行
            if not extracted_info['address'] and ('省' in line or '市' in line or '区' in line or '县' in line or '路' in line or '街' in line):
                if not any(keyword in line for field, keywords in keyword_mappings.items() for keyword in keywords if field != 'address'):
                    extracted_info['address'] = line
        
        # 检查是否成功提取了任何信息
        if not any(extracted_info.values()):
            return None
        
        return extracted_info 