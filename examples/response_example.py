# -*- coding: utf-8 -*-
"""Response类使用示例.

本文件演示了Response类的各种功能和使用方法，
包括函数执行包装、异常处理、结果格式化等。

Author: Guyue
License: MIT
Copyright (C) 2024-2025, Guyue.
"""

# 标准库导入 (Standard library imports)
import time

# 本地/自定义模块导入 (Local/custom module imports)
from pymagic import Response


def demo_basic_usage():
    """演示基本用法."""
    print("=== Response类基本用法演示 ===")
    
    # 定义一个简单的函数
    def add_numbers(a, b):
        """简单的加法函数."""
        return a + b
    
    # 使用Response.execute执行函数
    response = Response.execute(add_numbers, 10, 20)
    
    print(f"执行成功: {response.success}")
    print(f"执行结果: {response.result}")
    print(f"执行时间: {response.execution_time:.6f}秒")
    print(f"字符串表示: {response}")
    print()


def demo_exception_handling():
    """演示异常处理."""
    print("=== 异常处理演示 ===")
    
    def divide_numbers(a, b):
        """除法函数，可能抛出异常."""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    # 正常执行
    response1 = Response.execute(divide_numbers, 10, 2)
    print(f"正常执行: {response1}")
    
    # 异常执行
    response2 = Response.execute(divide_numbers, 10, 0)
    print(f"异常执行: {response2}")
    print(f"是否有异常: {response2.has_exception}")
    print(f"异常类型: {response2.error_type}")
    print(f"异常信息: {response2.error_message}")
    print()


def demo_json_output():
    """演示JSON格式输出."""
    print("=== JSON格式输出演示 ===")
    
    def get_user_info(user_id):
        """获取用户信息."""
        return {
            "id": user_id,
            "name": "张三",
            "age": 25,
            "skills": ["Python", "JavaScript", "SQL"]
        }
    
    response = Response.execute(get_user_info, 123)
    response.add_metadata("api_version", "v1.0")
    response.add_metadata("request_id", "req_001")
    
    # 紧凑JSON格式
    print("紧凑JSON格式:")
    print(response.to_json())
    print()
    
    # 格式化JSON
    print("格式化JSON:")
    print(response.to_json(indent=2))
    print()
    
    # 简化字典格式
    print("简化字典格式:")
    print(response.to_simple_dict())
    print()


def demo_timing_measurement():
    """演示执行时间测量."""
    print("=== 执行时间测量演示 ===")
    
    def slow_operation(duration):
        """模拟耗时操作."""
        time.sleep(duration)
        return f"操作完成，耗时{duration}秒"
    
    def fast_operation():
        """快速操作."""
        return sum(range(1000))
    
    # 测量慢操作
    print("执行慢操作...")
    slow_response = Response.execute(slow_operation, 0.1)
    print(f"慢操作结果: {slow_response}")
    
    # 测量快操作
    print("执行快操作...")
    fast_response = Response.execute(fast_operation)
    print(f"快操作结果: {fast_response}")
    print()


def demo_memory_management():
    """演示内存管理功能."""
    print("=== 内存管理演示 ===")
    
    def generate_large_data():
        """生成大量数据."""
        return list(range(100000))  # 生成10万个数字的列表
    
    response = Response.execute(generate_large_data)
    response.add_metadata("data_size", len(response.result))
    
    print(f"生成数据成功: {response.success}")
    print(f"数据大小: {response.get_metadata('data_size')}")
    print(f"结果类型: {type(response.result)}")
    
    # 清除结果以释放内存
    print("清除结果数据...")
    response.clear_result()
    print(f"清除后结果: {response.result}")
    print(f"执行状态仍保留: {response.success}")
    print(f"元数据仍保留: {response.get_metadata('data_size')}")
    print()


def demo_result_handling():
    """演示结果处理功能."""
    print("=== 结果处理演示 ===")
    
    def risky_operation(should_fail=False):
        """可能失败的操作."""
        if should_fail:
            raise RuntimeError("操作失败")
        return "操作成功"
    
    # 成功的情况
    success_response = Response.execute(risky_operation, False)
    result1 = success_response.get_result_or_default("默认值")
    print(f"成功情况下的结果: {result1}")
    
    # 失败的情况
    failed_response = Response.execute(risky_operation, True)
    result2 = failed_response.get_result_or_default("默认值")
    print(f"失败情况下的结果: {result2}")
    
    # 转换为字典（包含异常详情）
    print("\n失败响应的详细信息:")
    error_dict = failed_response.to_dict(include_exception_details=True)
    for key, value in error_dict.items():
        print(f"  {key}: {value}")
    print()


def demo_manual_creation():
    """演示手动创建Response实例."""
    print("=== 手动创建Response实例演示 ===")
    
    # 创建成功的响应
    success_response = Response(
        success=True,
        result="手动创建的成功结果",
        execution_time=0.001234
    )
    success_response.add_metadata("source", "manual")
    
    print(f"手动成功响应: {success_response}")
    
    # 创建失败的响应
    failed_response = Response(
        success=False,
        exception=ValueError("手动创建的异常"),
        execution_time=0.002345
    )
    failed_response.add_metadata("source", "manual")
    
    print(f"手动失败响应: {failed_response}")
    print()


def main():
    """主函数，运行所有演示."""
    print("Response类功能演示\n")
    
    demo_basic_usage()
    demo_exception_handling()
    demo_json_output()
    demo_timing_measurement()
    demo_memory_management()
    demo_result_handling()
    demo_manual_creation()
    
    print("=== 演示完成 ===")


if __name__ == '__main__':
    main()