# -*- coding: utf-8 -*-
"""PyMagic Response类单元测试.

本模块包含Response类的全面单元测试，覆盖所有方法和功能。

Author: Guyue
License: MIT
Copyright (C) 2024-2025, Guyue.
"""

# 标准库导入 (Standard library imports)
import json
import time
import unittest
from unittest.mock import patch

# 本地/自定义模块导入 (Local/custom module imports)
from pymagic._response import Response, extract_exception_location


class TestExtractExceptionLocation(unittest.TestCase):
    """测试extract_exception_location函数."""
    
    def test_extract_exception_location_with_traceback(self):
        """测试从异常中提取位置信息."""
        def inner_func():
            raise ValueError("测试异常")
        
        try:
            inner_func()
        except Exception as e:
            location, tb_str = extract_exception_location(e, skip_frames=0)
            
            # 验证位置信息格式（实际返回的是调用函数的位置）
            self.assertIn("test_response.py", location)
            self.assertIn("in test_extract_exception_location_with_traceback", location)
            
            # 验证traceback信息
            self.assertIn("Traceback", tb_str)
            self.assertIn("ValueError: 测试异常", tb_str)
    
    def test_extract_exception_location_without_traceback(self):
        """测试没有traceback的异常."""
        exception = ValueError("无traceback异常")
        location, tb_str = extract_exception_location(exception)
        
        self.assertEqual(location, "未知位置")
        self.assertIn("ValueError: 无traceback异常", tb_str)
    
    def test_extract_exception_location_skip_frames(self):
        """测试跳过调用栈帧."""
        def outer_func():
            def inner_func():
                raise RuntimeError("跳帧测试")
            inner_func()
        
        try:
            outer_func()
        except Exception as e:
            # 跳过0帧，应该指向当前测试函数
            location_0, _ = extract_exception_location(e, skip_frames=0)
            self.assertIn("test_response.py", location_0)
            
            # 跳过1帧，验证跳帧功能正常工作
            location_1, _ = extract_exception_location(e, skip_frames=1)
            self.assertIn("test_response.py", location_1)


class TestResponse(unittest.TestCase):
    """测试Response类."""
    
    def setUp(self):
        """测试前的设置."""
        self.test_result = "测试结果"
        self.test_exception = ValueError("测试异常")
        self.test_metadata = {"key": "value"}
    
    def test_init_success_response(self):
        """测试成功响应的初始化."""
        response = Response(
            success=True,
            result=self.test_result,
            execution_time=0.5,
            metadata=self.test_metadata
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.result, self.test_result)
        self.assertIsNone(response.exception)
        self.assertEqual(response.execution_time, 0.5)
        self.assertEqual(response.metadata, self.test_metadata)
        self.assertIsNotNone(response.start_time)
    
    def test_init_failure_response(self):
        """测试失败响应的初始化."""
        response = Response(
            success=False,
            exception=self.test_exception,
            execution_time=0.3
        )
        
        self.assertFalse(response.success)
        self.assertIsNone(response.result)
        self.assertEqual(response.exception, self.test_exception)
        self.assertEqual(response.execution_time, 0.3)
        self.assertEqual(response.metadata, {})
    
    def test_init_default_values(self):
        """测试默认值初始化."""
        response = Response()
        
        self.assertTrue(response.success)
        self.assertIsNone(response.result)
        self.assertIsNone(response.exception)
        self.assertEqual(response.execution_time, 0.0)
        self.assertEqual(response.metadata, {})
        self.assertIsNotNone(response.start_time)
    
    def test_execute_successful_function(self):
        """测试执行成功的函数."""
        def test_func(x, y):
            return x + y
        
        response = Response.execute(test_func, 3, 5)
        
        self.assertTrue(response.success)
        self.assertEqual(response.result, 8)
        self.assertIsNone(response.exception)
        self.assertGreater(response.execution_time, 0)
        self.assertIsNotNone(response.start_time)
        self.assertIsNotNone(response.end_time)
        self.assertGreater(response.end_time, response.start_time)
    
    def test_execute_function_with_kwargs(self):
        """测试执行带关键字参数的函数."""
        def test_func(name, age=25):
            return f"{name} is {age} years old"
        
        response = Response.execute(test_func, "Alice", age=30)
        
        self.assertTrue(response.success)
        self.assertEqual(response.result, "Alice is 30 years old")
    
    @patch('pymagic._response.logger')
    def test_execute_function_with_exception(self, mock_logger):
        """测试执行抛出异常的函数."""
        def error_func():
            raise ValueError("测试异常")
        
        response = Response.execute(error_func)
        
        self.assertFalse(response.success)
        self.assertIsNone(response.result)
        self.assertIsInstance(response.exception, ValueError)
        self.assertEqual(str(response.exception), "测试异常")
        self.assertGreater(response.execution_time, 0)
        
        # 验证日志记录
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        self.assertIn("函数执行异常", call_args)
        self.assertIn("error_func", call_args)
    
    def test_has_exception_property(self):
        """测试has_exception属性."""
        success_response = Response(success=True)
        failure_response = Response(success=False, exception=self.test_exception)
        
        self.assertFalse(success_response.has_exception)
        self.assertTrue(failure_response.has_exception)
    
    def test_error_message_property(self):
        """测试error_message属性."""
        success_response = Response(success=True)
        failure_response = Response(success=False, exception=self.test_exception)
        
        self.assertIsNone(success_response.error_message)
        self.assertEqual(failure_response.error_message, "测试异常")
    
    def test_error_name_property(self):
        """测试error_name属性."""
        success_response = Response(success=True)
        failure_response = Response(success=False, exception=self.test_exception)
        
        self.assertIsNone(success_response.error_name)
        self.assertEqual(failure_response.error_name, "ValueError")
    
    def test_info_method_success(self):
        """测试成功响应的info方法."""
        response = Response(
            success=True,
            result=self.test_result,
            execution_time=0.5,
            start_time=1000.0,
            end_time=1000.5,
            metadata=self.test_metadata
        )
        
        info = response.info()
        
        expected_keys = {
            "success", "execution_time", "start_time", "end_time", 
            "metadata", "error", "error_name"
        }
        self.assertEqual(set(info.keys()), expected_keys)
        
        self.assertTrue(info["success"])
        self.assertEqual(info["execution_time"], 0.5)
        self.assertEqual(info["start_time"], 1000.0)
        self.assertEqual(info["end_time"], 1000.5)
        self.assertEqual(info["metadata"], self.test_metadata)
        self.assertIsNone(info["error"])
        self.assertIsNone(info["error_name"])
    
    def test_info_method_failure(self):
        """测试失败响应的info方法."""
        response = Response(
            success=False,
            exception=self.test_exception,
            execution_time=0.3
        )
        
        info = response.info()
        
        self.assertFalse(info["success"])
        self.assertEqual(info["error"], "测试异常")
        self.assertEqual(info["error_name"], "ValueError")
    
    def test_content_method(self):
        """测试content方法."""
        response = Response(result=self.test_result)
        
        self.assertEqual(response.content(), self.test_result)
    
    def test_json_method(self):
        """测试json方法."""
        # 测试有效的JSON字符串结果
        json_string = '{"name": "Alice", "age": 30}'
        response = Response(result=json_string)
        
        result = response.json()
        self.assertEqual(result, {"name": "Alice", "age": 30})
        
        # 测试无效的JSON字符串
        invalid_response = Response(result="invalid json")
        with self.assertRaises(json.JSONDecodeError):
            invalid_response.json()
        
        # 测试非字符串结果
        dict_response = Response(result={"key": "value"})
        with self.assertRaises(TypeError):
            dict_response.json()
    
    def test_json_str_method(self):
        """测试json_str方法."""
        # 测试字典结果
        dict_result = {"name": "Alice", "age": 30, "items": [1, 2, 3]}
        response = Response(result=dict_result)
        
        json_str = response.json_str()
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed, dict_result)
        
        # 测试列表结果
        list_result = [1, 2, 3, "hello"]
        list_response = Response(result=list_result)
        
        json_str = list_response.json_str()
        parsed = json.loads(json_str)
        self.assertEqual(parsed, list_result)
        
        # 测试ensure_ascii参数
        chinese_result = {"名字": "张三"}
        chinese_response = Response(result=chinese_result)
        
        # 不使用ASCII编码
        json_str_unicode = chinese_response.json_str(ensure_ascii=False)
        self.assertIn("张三", json_str_unicode)
        
        # 使用ASCII编码
        json_str_ascii = chinese_response.json_str(ensure_ascii=True)
        self.assertNotIn("张三", json_str_ascii)
        self.assertIn("\\u", json_str_ascii)
    
    @patch('pymagic._response.logger')
    def test_clear_method(self, mock_logger):
        """测试clear方法."""
        response = Response(
            success=True,
            result=self.test_result,
            exception=self.test_exception,
            metadata=self.test_metadata.copy()
        )
        
        response.clear()
        
        self.assertIsNone(response.result)
        self.assertIsNone(response.exception)
        self.assertEqual(len(response.metadata), 0)
        
        # 验证日志记录
        mock_logger.debug.assert_called_once_with("已清除Response所有数据以释放内存")
    
    def test_str_method_success(self):
        """测试成功响应的字符串表示."""
        response = Response(
            success=True,
            result=self.test_result,
            execution_time=0.123456
        )
        
        str_repr = str(response)
        
        self.assertIn("成功", str_repr)
        self.assertIn("0.123456", str_repr)
        self.assertIn(self.test_result, str_repr)
    
    def test_str_method_failure(self):
        """测试失败响应的字符串表示."""
        response = Response(
            success=False,
            exception=self.test_exception,
            execution_time=0.234567
        )
        
        str_repr = str(response)
        
        self.assertIn("失败", str_repr)
        self.assertIn("0.234567", str_repr)
        self.assertIn("测试异常", str_repr)
    
    def test_repr_method(self):
        """测试repr方法."""
        response = Response(
            success=True,
            result=self.test_result,
            exception=self.test_exception,
            execution_time=0.5
        )
        
        repr_str = repr(response)
        
        self.assertIn("Response(", repr_str)
        self.assertIn("success=True", repr_str)
        self.assertIn(f"result={repr(self.test_result)}", repr_str)
        self.assertIn(f"exception={repr(self.test_exception)}", repr_str)
        self.assertIn("execution_time=0.5", repr_str)
    
    def test_execution_timing_accuracy(self):
        """测试执行时间计算的准确性."""
        def slow_func():
            time.sleep(0.1)  # 睡眠100毫秒
            return "完成"
        
        response = Response.execute(slow_func)
        
        self.assertTrue(response.success)
        self.assertEqual(response.result, "完成")
        self.assertGreaterEqual(response.execution_time, 0.1)
        self.assertLess(response.execution_time, 0.2)  # 应该不会超过200毫秒
        self.assertIsNotNone(response.start_time)
        self.assertIsNotNone(response.end_time)
        self.assertGreater(response.end_time, response.start_time)
    
    def test_metadata_handling(self):
        """测试元数据处理."""
        # 测试默认空元数据
        response1 = Response()
        self.assertEqual(response1.metadata, {})
        
        # 测试传入元数据（创建副本以避免引用问题）
        test_metadata_copy = self.test_metadata.copy()
        response2 = Response(metadata=test_metadata_copy)
        self.assertEqual(response2.metadata, test_metadata_copy)
        
        # 测试元数据修改不影响原始数据
        response2.metadata["new_key"] = "new_value"
        self.assertNotIn("new_key", self.test_metadata)
    
    def test_time_properties(self):
        """测试时间相关属性."""
        start_time = 1000.0
        end_time = 1000.5
        
        response = Response(
            start_time=start_time,
            end_time=end_time,
            execution_time=0.5
        )
        
        self.assertEqual(response.start_time, start_time)
        self.assertEqual(response.end_time, end_time)
        self.assertEqual(response.execution_time, 0.5)
    
    def test_complex_result_types(self):
        """测试复杂结果类型的处理."""
        # 测试字典结果
        dict_result = {"name": "Alice", "age": 30, "items": [1, 2, 3]}
        response1 = Response(result=dict_result)
        self.assertEqual(response1.result, dict_result)
        
        # 测试列表结果
        list_result = [1, "hello", {"key": "value"}]
        response2 = Response(result=list_result)
        self.assertEqual(response2.result, list_result)
        
        # 测试None结果
        response3 = Response(result=None)
        self.assertIsNone(response3.result)
    
    def test_exception_types(self):
        """测试不同异常类型的处理."""
        exceptions = [
            ValueError("值错误"),
            TypeError("类型错误"),
            KeyError("键错误"),
            RuntimeError("运行时错误")
        ]
        
        for exc in exceptions:
            response = Response(success=False, exception=exc)
            self.assertEqual(response.exception, exc)
            self.assertEqual(response.error_message, str(exc))
            self.assertEqual(response.error_name, type(exc).__name__)


if __name__ == '__main__':
    unittest.main()