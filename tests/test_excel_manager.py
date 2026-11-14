#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ExcelManager 客户单价历史（最近单价）逻辑的单元测试"""

import os
import shutil
import tempfile
import unittest

from src.database.excel_manager import ExcelManager


class ExcelManagerPriceHistoryTests(unittest.TestCase):
    """价格历史持久化测试

    每个用例使用独立的临时 CONTRACTG_HOME，避免污染真实用户数据目录。
    """

    def setUp(self):
        self._home = tempfile.mkdtemp(prefix="contractg-test-")
        self._old_home = os.environ.get("CONTRACTG_HOME")
        os.environ["CONTRACTG_HOME"] = self._home
        self.manager = ExcelManager()

    def tearDown(self):
        if self._old_home is None:
            os.environ.pop("CONTRACTG_HOME", None)
        else:
            os.environ["CONTRACTG_HOME"] = self._old_home
        shutil.rmtree(self._home, ignore_errors=True)

    def test_no_history_returns_none(self):
        self.assertIsNone(self.manager.get_recent_price("客户A", "商品X", "型号1"))

    def test_record_then_get_normalizes_price(self):
        self.manager.record_prices([("客户A", "商品X", "型号1", "123.4")])
        self.assertEqual(self.manager.get_recent_price("客户A", "商品X", "型号1"), "123.40")

    def test_history_is_scoped_per_customer(self):
        self.manager.record_prices([("客户A", "商品X", "型号1", 100)])
        self.assertIsNone(self.manager.get_recent_price("客户B", "商品X", "型号1"))

    def test_latest_record_overwrites_previous(self):
        self.manager.record_prices([("客户A", "商品X", "型号1", 100)])
        self.manager.record_prices([("客户A", "商品X", "型号1", 200)])
        self.assertEqual(self.manager.get_recent_price("客户A", "商品X", "型号1"), "200.00")

    def test_price_key_ignores_surrounding_whitespace(self):
        self.manager.record_prices([(" 客户A ", " 商品X ", " 型号1 ", 100)])
        self.assertEqual(self.manager.get_recent_price("客户A", "商品X", "型号1"), "100.00")

    def test_skips_entries_without_customer_or_name(self):
        self.manager.record_prices([
            ("", "商品X", "型号1", 100),
            ("客户A", "", "型号1", 100),
        ])
        self.assertFalse(self.manager.price_history_file.exists())

    def test_skips_invalid_price(self):
        self.manager.record_prices([("客户A", "商品X", "型号1", "not-a-number")])
        self.assertIsNone(self.manager.get_recent_price("客户A", "商品X", "型号1"))

    def test_corrupted_history_file_returns_none(self):
        with open(self.manager.price_history_file, "w", encoding="utf-8") as fp:
            fp.write("{ this is not valid json")
        self.assertIsNone(self.manager.get_recent_price("客户A", "商品X", "型号1"))


if __name__ == "__main__":
    unittest.main()
