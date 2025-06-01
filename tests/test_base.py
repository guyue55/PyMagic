import unittest
from unittest import mock

from pymagic._base import Base
from pymagic.logger_utils import logger
from pymagic.tools_utils import Tools
from pymagic.decorator_utils import Decorate


class TestBase(unittest.TestCase):
    """测试Base基础类的核心功能"""
    
    def test_init_default(self):
        """测试默认初始化"""
        base = Base()
        self.assertIsNotNone(base)
        self.assertEqual(base.logger, logger)
    
    def test_init_with_params(self):
        """测试带参数初始化"""
        # 测试禁用地址解析
        base = Base(_parse_addr=False)
        self.assertIsNotNone(base)
        
        # 测试禁用异常捕获
        base = Base(_catch=False)
        self.assertIsNotNone(base)
        
        # 测试自定义异常处理参数
        base = Base(err_return=None, retry_num=2, sleep_time=0.1)
        self.assertIsNotNone(base)
    
    def test_context_manager(self):
        """测试上下文管理器功能"""
        # 创建一个继承Base的测试类
        class TestClass(Base):
            def __init__(self):
                super().__init__()
                self.closed = False
            
            def close(self):
                self.closed = True
        
        # 测试with语句
        with TestClass() as test_obj:
            self.assertFalse(test_obj.closed)
        
        # 测试退出上下文后是否调用了close方法
        self.assertTrue(test_obj.closed)
    
    def test_tools_property(self):
        """测试Tools属性"""
        base = Base()
        self.assertEqual(base.Tools, Tools)
    
    def test_decorate_property(self):
        """测试Decorate属性"""
        base = Base()
        self.assertEqual(base.Decorate, Decorate)
    
    def test_parse_address(self):
        """测试地址解析功能"""
        # 测试简单地址解析
        base = Base()
        base._address = "127.0.0.1:8080"
        base._parse_address()
        self.assertEqual(base.host, "127.0.0.1")
        self.assertEqual(base.port, 8080)
        
        # 测试带用户名密码的地址解析
        base = Base()
        base._address = "user:pass@192.168.1.1:21"
        base._parse_address()
        self.assertEqual(base.host, "192.168.1.1")
        self.assertEqual(base.port, 21)
        self.assertEqual(base.user, "user")
        self.assertEqual(base.password, "pass")
        
        # 测试带前缀的字段
        base = Base()
        base._host = "dummy"  # 设置_host属性以触发前缀标志
        base._address = "user:pass@192.168.1.1:21"
        base._parse_address()
        self.assertEqual(base._host, "192.168.1.1")
        self.assertEqual(base._port, 21)
        self.assertEqual(base._user, "user")
        self.assertEqual(base._password, "pass")
    
    def test_exception_handling(self):
        """测试异常处理功能"""
        # 创建一个会抛出异常的测试类
        class TestExceptionClass(Base):
            def test_method(self):
                raise ValueError("Test exception")
        
        # 测试异常被捕获并返回默认值
        obj = TestExceptionClass()
        result = obj.test_method()
        self.assertFalse(result)  # 默认返回False
        
        # 测试自定义返回值
        obj = TestExceptionClass(err_return="Error")
        result = obj.test_method()
        self.assertEqual(result, "Error")


if __name__ == '__main__':
    unittest.main()