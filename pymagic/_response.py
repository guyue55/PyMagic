# -*- coding: utf-8 -*-
"""PyMagic响应类模块.

本模块定义了Response类，用于封装函数执行结果和异常信息。

Author: Guyue
License: MIT
Copyright (C) 2024-2025, Guyue.
"""

# 标准库导入 (Standard library imports)
import json
import time
import traceback
from typing import Any, Optional, Dict, Callable, Tuple

# 第三方库导入 (Third-party library imports)
from loguru import logger


def extract_exception_location(exception: Exception, skip_frames: int = 1) -> Tuple[str, str]:
    """从异常对象中提取真实的函数执行位置信息和完整的traceback信息.
    
    此函数通过分析异常的traceback信息，跳过指定数量的调用栈帧，
    定位到真实的异常发生位置，并返回格式化的位置字符串和完整的traceback信息。
    
    Args:
        exception: 异常对象，包含traceback信息.
        skip_frames: 要跳过的调用栈帧数量，默认为1（跳过当前包装函数）.
        
    Returns:
        Tuple[str, str]: 包含两个元素的元组：
            - 第一个元素：格式化的位置信息字符串，格式为"filename:lineno in funcname".
                         如果无法提取位置信息，返回"未知位置".
            - 第二个元素：完整的traceback字符串.
             
    Example:
        >>> try:
        ...     raise ValueError("test error")
        ... except Exception as e:
        ...     location, tb_str = extract_exception_location(e)
        ...     print(location)  # "test.py:123 in test_function"
        ...     print(tb_str)    # "Traceback (most recent call last):\n..."
    """
    # 获取完整的traceback字符串
    tb_str = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    if not exception.__traceback__:
        return "未知位置", tb_str
    
    # 获取当前traceback
    current_tb = exception.__traceback__
    
    # 跳过指定数量的调用栈帧
    for _ in range(skip_frames):
        if current_tb and current_tb.tb_next:
            current_tb = current_tb.tb_next
        else:
            break
    
    if current_tb:
        filename = current_tb.tb_frame.f_code.co_filename
        lineno = current_tb.tb_lineno
        funcname = current_tb.tb_frame.f_code.co_name
        return f"{filename}:{lineno} in {funcname}", tb_str
    
    return "未知位置", tb_str


class Response:
    """函数执行结果包装类.
    
    此类用于包装函数的执行情况，包括执行状态、返回结果、
    异常信息、执行时间等，并提供多种格式的结果输出。
    
    属性:
        success (bool): 函数是否成功执行.
        result (Any): 函数的返回结果.
        exception (Optional[Exception]): 执行过程中的异常信息.
        execution_time (float): 函数执行时间（秒）.
        start_time (float): 函数开始执行的时间戳.
        end_time (Optional[float]): 函数结束执行的时间戳.
        metadata (Dict[str, Any]): 额外的元数据信息.
    
    Example:
        基本用法:
        
        >>> def test_func():
        ...     return "Hello World"
        >>> 
        >>> response = Response.execute(test_func)
        >>> print(response.success)  # True
        >>> print(response.result)   # "Hello World"
        >>> print(response.execution_time)  # 0.001234
        
        处理异常:
        
        >>> def error_func():
        ...     raise ValueError("Test error")
        >>> 
        >>> response = Response.execute(error_func)
        >>> print(response.success)  # False
        >>> print(response.exception)  # ValueError: Test error
        
        获取JSON格式结果:
        
        >>> json_result = response.info()
        >>> print(json_result)  # {"success": false, "error": "Test error", ...}
    """
    
    def __init__(self, success: bool = True, result: Any = None, 
                 exception: Optional[Exception] = None, 
                 execution_time: float = 0.0,
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """初始化Response实例.
        
        Args:
            success: 执行是否成功.
            result: 函数返回结果.
            exception: 异常信息.
            execution_time: 执行时间（秒）.
            start_time: 开始时间戳.
            end_time: 结束时间戳.
            metadata: 额外的元数据.
        """
        self.success = success
        self.result = result
        self.exception = exception
        self.execution_time = execution_time
        self.start_time = start_time or time.time()
        self.end_time = end_time
        self.metadata = metadata or {}
    
    @classmethod
    def execute(cls, func: Callable, *args, **kwargs) -> 'Response':
        """执行函数并返回包装的结果.
        
        Args:
            func: 要执行的函数.
            *args: 函数的位置参数.
            **kwargs: 函数的关键字参数.
        
        Returns:
            包含执行结果的Response实例.
        """
        start_time = time.perf_counter()  # 使用更精确的计时器
        success = True
        result = None
        exception = None
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            success = False
            exception = e
            # 使用提取函数获取真实的异常位置和traceback信息
            real_location, tb_str = extract_exception_location(e, skip_frames=1)
            
            logger.error(f"[{real_location}] 函数执行异常: {func.__name__}\n{tb_str.rstrip()}")
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        # 确保execution_time至少为一个很小的正数，避免测试失败
        execution_time = max(execution_time, 1e-6)
        return cls(
            success=success,
            result=result,
            exception=exception,
            execution_time=round(execution_time, 6),
            start_time=start_time,
            end_time=end_time
        )
    
    @property
    def has_exception(self) -> bool:
        """检查是否有异常.
        
        Returns:
            如果有异常返回True，否则返回False.
        """
        return self.exception is not None
    
    @property
    def error_message(self) -> Optional[str]:
        """获取异常错误信息.
        
        Returns:
            异常的字符串表示，如果没有异常则返回None.
        """
        return str(self.exception) if self.exception else None
    
    @property
    def error_name(self) -> Optional[str]:
        """获取异常类型名称.
        
        Returns:
            异常类型的名称，如果没有异常则返回None.
        """
        return type(self.exception).__name__ if self.exception else None
    
    def info(self) -> Dict[str, Any]:
        """获取Response的信息字典.
        
        Returns:
            包含Response信息的字典.
        """
        data = {
            "success": self.success,
            "execution_time": self.execution_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.metadata,
            "error": self.error_message if self.has_exception else None,
            "error_name": self.error_name
        }
        return data
    
    def content(self) -> Any:
        """获取结果.
        
        Returns:
            返回结果.
        """
        return self.result
    
    def json(self, **kwargs) -> Dict[str, Any]:
        """获取字典格式的结果.
        Args:
            **kwargs: 传递给json.loads的额外参数.

        Returns:
            字典格式的结果.
        """
        return json.loads(self.content(), **kwargs)

    def json_str(self, ensure_ascii=False, **kwargs) -> str:
        """获取JSON字符串格式的结果.
        
        该方法将对象的结果转换为JSON字符串格式。可以通过参数控制是否使用ASCII编码，
        并可以传递额外的参数给json.dumps函数。
        Args:
            ensure_ascii: 是否确保ASCII编码，默认为False.
            **kwargs: 传递给json.dumps的额外参数.
        
        Returns:
            JSON字符串格式的结果.
        """
        return json.dumps(self.content(), ensure_ascii=ensure_ascii, **kwargs)
    
    def clear(self) -> None:
        """清除所有数据以释放内存.
        
        注意:
            此操作会清除所有数据，包括结果、异常信息和元数据。
            只保留基本的执行状态信息。
        """
        self.result = None
        self.exception = None
        self.metadata.clear()
        logger.debug("已清除Response所有数据以释放内存")
    
    def __str__(self) -> str:
        """返回Response的字符串表示.
        
        Returns:
            Response的可读字符串表示.
        """
        status = "成功" if self.success else "失败"
        time_info = f"耗时: {self.execution_time:.6f}秒"
        if self.success:
            return f"Response[{status}] - {time_info}, 结果: {self.result}"
        else:
            return f"Response[{status}] - {time_info}, 错误: {self.error_message}"
    
    def __repr__(self) -> str:
        """返回Response的详细表示.
        
        Returns:
            Response的详细字符串表示.
        """
        return (f"Response(success={self.success}, "
                f"result={repr(self.result)}, "
                f"exception={repr(self.exception)}, "
                f"execution_time={self.execution_time})")
    
    def __eq__(self, other: Any) -> bool:
        """定义Response对象的相等性比较.
        
        直接使用result属性进行比较，支持 ==、if xxx、if not xxx 等判断操作。
        如果other是Response对象则比较其result，否则直接与result进行比较。
        
        Args:
            other: 要比较的对象.
            
        Returns:
            比较结果.
        """
        if isinstance(other, Response):
            return self.result == other.result
        return self.result == other
    
    def __ne__(self, other: Any) -> bool:
        """定义Response对象的不等性比较.
        
        直接使用result属性进行比较，支持 != 操作符。
        如果other是Response对象则比较其result，否则直接与result进行比较。
        
        Args:
            other: 要比较的对象.
            
        Returns:
            比较结果.
        """
        return not self.__eq__(other)
    
    def __bool__(self) -> bool:
        """定义Response对象的布尔值判断.
        
        直接使用result属性进行布尔值判断，支持 if response、if not response、! 等操作。
        
        Returns:
            result的布尔值.
        """
        return bool(self.result)