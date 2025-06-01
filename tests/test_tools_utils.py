import os
import time
import unittest
from unittest import mock

from pymagic.tools_utils import Tools


class TestTools(unittest.TestCase):
    """测试Tools工具类的核心功能"""

    def test_is_contain_zh(self):
        """测试中文检测功能"""
        self.assertTrue(Tools.is_contain_zh("你好world"))
        self.assertFalse(Tools.is_contain_zh("hello world"))

    def test_is_zh(self):
        """测试全中文检测功能"""
        self.assertTrue(Tools.is_zh("你好世界"))
        self.assertFalse(Tools.is_zh("你好world"))

    def test_is_en(self):
        """测试全英文检测功能"""
        self.assertTrue(Tools.is_en("helloworld"))
        self.assertFalse(Tools.is_en("hello world"))  # 包含空格
        self.assertFalse(Tools.is_en("hello123"))     # 包含数字

    def test_get_system_type(self):
        """测试系统类型检测功能"""
        system_type = Tools.get_system_type()
        self.assertIn(system_type, ["Windows", "Linux", "Darwin"])

    def test_check_system_win(self):
        """测试Windows系统检测功能"""
        with mock.patch('pymagic.tools_utils.Tools.get_system_type', return_value="Windows"):
            is_win, sys_type = Tools.check_system_win()
            self.assertTrue(is_win)
            self.assertEqual(sys_type, "Windows")

        with mock.patch('pymagic.tools_utils.Tools.get_system_type', return_value="Linux"):
            is_win, sys_type = Tools.check_system_win()
            print(Tools.get_system_type())
            self.assertFalse(is_win)
            self.assertEqual(sys_type, "Linux")

    def test_is_windows(self):
        """测试是否为Windows系统"""
        with mock.patch('pymagic.tools_utils.Tools.get_system_type', return_value="Windows"):
            self.assertTrue(Tools.is_windows())

        with mock.patch('pymagic.tools_utils.Tools.get_system_type', return_value="Linux"):
            self.assertFalse(Tools.is_windows())

    def test_is_linux(self):
        """测试是否为Linux系统"""
        with mock.patch('pymagic.tools_utils.Tools.get_system_type', return_value="Linux"):
            self.assertTrue(Tools.is_linux())

        with mock.patch('pymagic.tools_utils.Tools.get_system_type', return_value="Windows"):
            self.assertFalse(Tools.is_linux())

    def test_list_random_shuffle(self):
        """测试列表随机打乱功能"""
        original_list = [1, 2, 3, 4, 5]
        # 由于随机性，我们只能测试返回的列表长度和元素是否相同
        shuffled_list = Tools.list_random_shuffle(original_list.copy())
        self.assertEqual(len(shuffled_list), len(original_list))
        self.assertCountEqual(shuffled_list, original_list)

    def test_check_empty(self):
        """测试空值检测功能"""
        self.assertTrue(Tools.check_empty(None))
        self.assertTrue(Tools.check_empty(""))
        self.assertTrue(Tools.check_empty([]))
        self.assertTrue(Tools.check_empty({}))
        self.assertFalse(Tools.check_empty("hello"))
        self.assertFalse(Tools.check_empty([1, 2, 3]))

    def test_check_type_one(self):
        """测试类型检测功能（匹配一种）"""
        self.assertTrue(Tools.check_type_one("hello", str))
        self.assertTrue(Tools.check_type_one(123, int, float))
        self.assertFalse(Tools.check_type_one("hello", int, float))

    def test_check_str_one(self):
        """测试字符串包含检测功能（包含一种）"""
        self.assertTrue(Tools.check_str_one("hello world", "hello", "python"))
        self.assertFalse(Tools.check_str_one("hello world", "python", "java"))

    def test_check_str_all(self):
        """测试字符串包含检测功能（包含所有）"""
        self.assertTrue(Tools.check_str_all("hello world python", "hello", "python"))
        self.assertFalse(Tools.check_str_all("hello world", "hello", "python"))

    def test_contain_all(self):
        """测试字符串包含所有值功能"""
        self.assertTrue(Tools.contain_all("hello world python", "hello", "world"))
        self.assertFalse(Tools.contain_all("hello world", "hello", "python"))

    def test_contain_any(self):
        """测试字符串包含任一值功能"""
        self.assertTrue(Tools.contain_any("hello world", "hello", "python"))
        self.assertFalse(Tools.contain_any("hello world", "python", "java"))

    def test_format_time(self):
        """测试时间格式化功能"""
        # 使用固定的时间戳进行测试
        timestamp = 1609459200  # 2021-01-01 08:00:00
        self.assertEqual(Tools.format_time(timestamp), "2021-01-01 08:00:00")
        self.assertEqual(Tools.format_time(timestamp, "%Y-%m-%d"), "2021-01-01")

    def test_get_timestamp(self):
        """测试获取时间戳功能"""
        timestamp = Tools.get_timestamp()
        self.assertIsInstance(timestamp, int)
        self.assertTrue(timestamp > 0)

    def test_get_nowdate(self):
        """测试获取当前日期功能"""
        date_str = Tools.get_nowdate()
        # 简单验证格式是否正确
        self.assertRegex(date_str, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')


if __name__ == '__main__':
    unittest.main()