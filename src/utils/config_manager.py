#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
"""

import os
import json
import configparser
import re

from src.models.company import Company
from src.utils.runtime_paths import ensure_writable_layout
from src.utils.text_parser import TextParser

class ConfigManager:
    """配置管理类"""
    def __init__(self):
        base_dir = ensure_writable_layout()
        self.config_dir = str(base_dir / 'config')
        self.company_file = os.path.join(self.config_dir, 'company.json')
        self.settings_file = os.path.join(self.config_dir, 'settings.ini')
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 确保配置文件存在
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """确保配置文件存在"""
        # 公司信息文件
        if not os.path.exists(self.company_file):
            # 创建默认公司信息
            companies = [
                {
                    'name': '示例公司名称',
                    'contact': '联系人',
                    'phone': '电话',
                    'address': '公司地址',
                    'bank_name': '开户银行',
                    'bank_account': '银行账号',
                    'tax_id': '税号',
                    'is_default': True
                }
            ]
            self.save_companies(companies)
        
        # 设置文件
        if not os.path.exists(self.settings_file):
            # 创建默认设置
            config = configparser.ConfigParser()
            config['General'] = {
                'contract_template': 'templates/contract_template.xlsx',
                'quote_template': 'templates/quote_template.xlsx',
                'output_dir': 'output'  # 直接使用output目录，不再使用子目录
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                config.write(f)
    
    def get_companies(self):
        """获取所有公司信息"""
        try:
            if not os.path.exists(self.company_file):
                return []
            
            with open(self.company_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
                if not isinstance(companies_data, list):
                    companies_data = [companies_data]
                return [Company.from_dict(company) for company in companies_data]
        except Exception as e:
            print(f"读取公司信息出错: {e}")
            return []
    
    def save_companies(self, companies):
        """保存公司信息"""
        try:
            # 如果传入的是Company对象列表，转换为字典列表
            if companies and isinstance(companies[0], Company):
                companies_data = [company.to_dict() for company in companies]
            else:
                companies_data = companies
            
            with open(self.company_file, 'w', encoding='utf-8') as f:
                json.dump(companies_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存公司信息出错: {e}")
            return False
    
    def get_default_company(self):
        """获取默认公司信息"""
        companies = self.get_companies()
        for company in companies:
            if company.is_default:
                return company
        return companies[0] if companies else None
    
    def parse_company_info(self, text):
        """解析文本中的公司信息（复用 TextParser，与客户信息解析逻辑保持一致）"""
        info = TextParser.parse_customer_info(text)
        if info is None:
            return None
        info['is_default'] = False
        return info
    
    def get_setting(self, section, key, default=None):
        """获取设置"""
        try:
            config = configparser.ConfigParser()
            config.read(self.settings_file, encoding='utf-8')
            return config.get(section, key, fallback=default)
        except Exception:
            return default
    
    def set_setting(self, section, key, value):
        """设置配置"""
        try:
            config = configparser.ConfigParser()
            config.read(self.settings_file, encoding='utf-8')
            
            if not config.has_section(section):
                config.add_section(section)
            
            config.set(section, key, value)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            return True
        except Exception as e:
            print(f"保存设置出错: {e}")
            return False

    def add_template(self, doc_type: str, display_name: str, relative_path: str) -> bool:
        try:
            doc_type = (doc_type or "").strip().lower()
            if doc_type not in ("contract", "quote"):
                return False

            if not display_name or not relative_path:
                return False

            key = "contract_templates" if doc_type == "contract" else "quote_templates"

            config = configparser.ConfigParser()
            config.read(self.settings_file, encoding='utf-8')

            if not config.has_section("Templates"):
                config.add_section("Templates")

            current = config.get("Templates", key, fallback="") or ""
            current = current.strip()

            entry = f"{display_name}::{relative_path}"
            if current:
                new_value = f"{current}; {entry}"
            else:
                new_value = entry

            config.set("Templates", key, new_value)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                config.write(f)

            return True
        except Exception as e:
            print(f"添加模板出错: {e}")
            return False

    def remove_template(self, doc_type: str, template_id: str):
        try:
            doc_type = (doc_type or "").strip().lower()
            template_id = (template_id or "").strip()
            if doc_type not in ("contract", "quote"):
                return False, None
            if not template_id or template_id == "builtin":
                return False, None

            list_key = "contract_templates" if doc_type == "contract" else "quote_templates"
            default_key = "contract_template_default" if doc_type == "contract" else "quote_template_default"

            config = configparser.ConfigParser()
            config.read(self.settings_file, encoding='utf-8')
            if not config.has_section("Templates"):
                return False, None

            raw = config.get("Templates", list_key, fallback="") or ""
            parts = [p.strip() for p in re.split(r"[;,]\s*", raw) if p.strip()]
            kept = []
            removed_entry = None
            removed_path_part = None
            still_referenced = False

            for part in parts:
                name = None
                path_part = part
                for sep in ("::", "=", "|"):
                    if sep in part:
                        left, right = part.split(sep, 1)
                        left = left.strip()
                        right = right.strip()
                        if left and right:
                            name = left
                            path_part = right
                        break

                if (name or "").strip() == template_id:
                    removed_entry = {"name": name, "path": path_part}
                    removed_path_part = (path_part or "").strip()
                    continue

                kept.append(part)
                if removed_path_part and (path_part or "").strip() == removed_path_part:
                    still_referenced = True

            if removed_entry is None:
                return False, None

            config.set("Templates", list_key, "; ".join(kept))

            current_default = (config.get("Templates", default_key, fallback="") or "").strip()
            if current_default == template_id:
                config.set("Templates", default_key, "")

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                config.write(f)

            removed_entry["still_referenced"] = still_referenced
            return True, removed_entry
        except Exception as e:
            print(f"删除模板出错: {e}")
            return False, None
