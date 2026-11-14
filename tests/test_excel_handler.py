#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ExcelHandler 模板回退与客户缺失兜底逻辑的单元测试"""

import os
import shutil
import tempfile
import unittest

from src.models.contract import Contract, ContractItem
from src.models.customer import Customer
from src.utils.excel_handler import ExcelHandler, _BlankCustomer


class ExcelHandlerTests(unittest.TestCase):
    def setUp(self):
        self._home = tempfile.mkdtemp(prefix="contractg-test-")
        self._old_home = os.environ.get("CONTRACTG_HOME")
        os.environ["CONTRACTG_HOME"] = self._home
        self.handler = ExcelHandler()

    def tearDown(self):
        if self._old_home is None:
            os.environ.pop("CONTRACTG_HOME", None)
        else:
            os.environ["CONTRACTG_HOME"] = self._old_home
        shutil.rmtree(self._home, ignore_errors=True)

    def _make_contract(self, customer=None, company=None):
        return Contract(
            number="SC-20260101-001",
            customer=customer,
            company=company,
            items=[ContractItem(name="商品", model="M1", unit="台", price=100.0, quantity=1, amount=100.0)],
            sign_date="2026年01月01日",
            total_amount=100.0,
            service_fee=0.0,
            grand_total=100.0,
        )

    def _clear_template_config(self):
        self.handler.config_manager.set_setting("Templates", "contract_templates", "")
        self.handler.config_manager.set_setting("General", "contract_template", "")

    # ---------- 模板回退 ----------

    def test_builtin_template_returns_none(self):
        self.assertIsNone(self.handler._select_template_path("contract", "builtin"))
        self.assertIsNone(self.handler._select_template_path("quote", "builtin"))

    def test_no_specs_returns_none(self):
        self._clear_template_config()
        self.assertIsNone(self.handler._select_template_path("contract", "任意ID"))

    def test_unknown_template_id_falls_back_to_first_spec(self):
        template_path = os.path.join(self._home, "templates", "自定义模板.xlsx")
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, "w", encoding="utf-8"):
            pass
        self.handler.config_manager.set_setting(
            "Templates", "contract_templates", "自定义::templates/自定义模板.xlsx"
        )

        resolved = self.handler._select_template_path("contract", "不存在的ID")

        self.assertEqual(os.path.realpath(resolved), os.path.realpath(template_path))

    # ---------- 客户缺失（None）兜底 ----------

    def test_context_with_none_customer_is_blank(self):
        ctx = self.handler._build_template_context(self._make_contract(customer=None), "contract")
        self.assertEqual(ctx["甲方名称"], "")
        self.assertEqual(ctx["甲方联系人"], "")
        self.assertEqual(ctx["甲方税号"], "")
        self.assertEqual(ctx["文档类型"], "合同")

    def test_context_with_customer_populates_party_a(self):
        customer = Customer(name="甲方公司", contact="张三", phone="13800138000")
        ctx = self.handler._build_template_context(self._make_contract(customer=customer), "quote")
        self.assertEqual(ctx["甲方名称"], "甲方公司")
        self.assertEqual(ctx["甲方联系人"], "张三")
        self.assertEqual(ctx["文档类型"], "报价单")

    def test_output_basename_handles_none_customer(self):
        contract = self._make_contract(customer=None, company={"name": "乙方公司"})
        basename = self.handler._build_output_basename(contract)
        self.assertIn("乙方公司", basename)
        self.assertTrue(basename.startswith("未知"))

    def test_blank_customer_placeholder_is_empty(self):
        self.assertEqual(_BlankCustomer.name, "")
        self.assertEqual(_BlankCustomer.contact, "")
        self.assertEqual(_BlankCustomer.tax_id, "")


if __name__ == "__main__":
    unittest.main()
