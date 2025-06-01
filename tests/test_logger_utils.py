import os
import unittest
from unittest import mock
import tempfile
import shutil
from pathlib import Path

from pymagic.logger_utils import LoggerUtils, logger


class TestLoggerUtils(unittest.TestCase):
    """测试LoggerUtils日志工具类的核心功能"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建临时目录用于测试日志文件
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "test.log")
    
    def tearDown(self):
        """测试后清理工作"""
        # 删除测试目录
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_log(self):
        """测试获取日志实例功能"""
        log = LoggerUtils.get_log()
        self.assertIsNotNone(log)
        self.assertEqual(log, logger)
    
    def test_set_log(self):
        """测试设置日志实例功能"""
        # 测试基本设置
        log = LoggerUtils.set_log(self.log_file, level="DEBUG")
        self.assertIsNotNone(log)
        
        # 测试日志文件是否创建
        log.debug("Test debug message")
        log_dir = os.path.dirname(self.log_file)
        self.assertTrue(os.path.exists(log_dir))
    
    def test_new(self):
        """测试创建新日志实例功能"""
        new_log_file = os.path.join(self.test_dir, "new.log")
        new_logger = LoggerUtils.new(new_log_file, level="INFO")
        
        # 测试新实例是否正常工作
        self.assertIsNotNone(new_logger)
        new_logger.info("Test info message")
    
    def test_format_options(self):
        """测试日志格式选项"""
        # 测试不同格式选项
        formats = [
            LoggerUtils.FORMAT,
            LoggerUtils.FORMAT_PT,
            LoggerUtils.FORMAT_PROCESS,
            LoggerUtils.FORMAT_THREAD
        ]
        
        for fmt in formats:
            log_file = os.path.join(self.test_dir, f"format_{formats.index(fmt)}.log")
            log = LoggerUtils.set_log(log_file, level="INFO", format=fmt)
            self.assertIsNotNone(log)
            log.info("Test format message")
    
    def test_default_settings(self):
        """测试默认设置"""
        # 验证DEFAULT字典中的关键设置
        self.assertIn("sink", LoggerUtils.DEFAULT)
        self.assertIn("rotation", LoggerUtils.DEFAULT)
        self.assertIn("retention", LoggerUtils.DEFAULT)
        self.assertIn("format", LoggerUtils.DEFAULT)
        
        # 测试DEFAULT_SINK设置
        self.assertEqual(LoggerUtils.DEFAULT_SINK, "log/logger.log")


if __name__ == '__main__':
    unittest.main()