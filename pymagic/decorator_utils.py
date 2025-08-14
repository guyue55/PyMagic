# -*- coding: utf-8 -*-
"""PyMagic装饰器工具模块.

本模块提供了一套全面的实用装饰器集合，用于异常处理、性能计时、
线程安全以及自动为类方法应用装饰器等功能。

Author: Guyue
License: MIT
Copyright (C) 2024-2025, Guyue.
"""

import threading
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from loguru import logger


def log_with_level(message: str, 
                   level: Optional[str] = None, 
                   *args: Any, 
                   **kwargs: Any) -> None:
    """使用loguru库输出指定级别的日志消息.
    
    此函数提供了一种便捷的方式，使用loguru日志库记录不同
    严重级别的日志消息。
    
    Args:
        message: 要记录的日志消息.
        level: 日志级别，如debug/info/warning/error/exception/critical/success.
            如果为None或"exception"，默认为"error".
        *args: 传递给日志函数的位置参数.
        **kwargs: 传递给日志函数的关键字参数.
    
    Note:
        "exception"级别会映射到"error"级别，因为loguru
        使用"error"进行异常日志记录.
    """
    # 标准化日志级别
    if not level or level.lower() == "exception":
        level = "error"
    
    level = level.upper()
    options = logger._options
    
    # 为ERROR级别启用异常追踪
    if level == "ERROR":
        options = (True,) + options[1:]
    
    # 解包选项并调整调用深度
    (exception, depth, record, lazy, colors, raw, capture, patcher, extra) = options
    new_options = (exception, depth + 1, record, lazy, colors, raw, capture, patcher, extra)
    logger._log(level, False, new_options, message, args, kwargs)


def get_public_methods(obj: Any) -> List[Tuple[str, Callable]]:
    """获取对象的公共方法列表.
    
    此函数返回对象的公共方法列表，过滤掉以下划线开头的方法
    和属性特性。
    
    Args:
        obj: 要获取方法的对象或类.
        
    Returns:
        包含(方法名, 方法对象)元组的列表，
        包含所有公共可调用方法.
    
    Example:
        >>> class MyClass:
        ...     def public_method(self):
        ...         pass
        ...     def _private_method(self):
        ...         pass
        >>> methods = get_public_methods(MyClass)
        >>> print([name for name, _ in methods])  # ['public_method']
    """
    if not hasattr(obj, '__dict__') and not hasattr(obj, '__class__'):
        return []
    
    methods = []
    for name in dir(obj):
        if name.startswith('_'):
            continue
            
        try:
            attr = getattr(obj, name)
            class_attr = getattr(obj.__class__, name, None) if hasattr(obj, '__class__') else None
            
            if not isinstance(class_attr, property) and callable(attr):
                methods.append((name, attr))
        except (AttributeError, TypeError):
            # 忽略无法访问的属性
            continue
    
    return methods


class ThreadWithResult(threading.Thread):
    """增强的线程类，支持返回值获取和异常处理.
    
    此类扩展了标准的threading.Thread，支持从线程执行中获取
    返回值，并提供异常处理功能。
    
    Attributes:
        target_func: 在线程中执行的目标函数.
        args: 传递给目标函数的参数元组.
        kwargs: 传递给目标函数的关键字参数.
        result: 目标函数执行的返回值.
        exception: 执行过程中发生的异常.
        default_result: 发生错误时返回的默认值.
    
    Example:
        >>> def slow_function(x, y):
        ...     time.sleep(1)
        ...     return x + y
        >>> 
        >>> thread = ThreadWithResult(target=slow_function, args=(1, 2))
        >>> thread.start()
        >>> thread.join()
        >>> result = thread.get_result()  # 返回3
    """

    def __init__(self, 
                 target: Callable[..., Any], 
                 args: Tuple[Any, ...] = (), 
                 kwargs: Optional[Dict[str, Any]] = None,
                 default_result: Any = None) -> None:
        """初始化增强的线程对象.
        
        Args:
            target: 在线程中执行的目标函数.
            args: 传递给目标函数的参数元组.
            kwargs: 传递给目标函数的关键字参数.
            default_result: 执行过程中发生错误时返回的值.
        """
        super().__init__()
        self.target_func = target
        self.args = args
        self.kwargs = kwargs or {}
        self.result: Any = None
        self.exception: Optional[Exception] = None
        self.default_result = default_result

    def run(self) -> None:
        """执行目标函数并保存其返回值或异常."""
        try:
            self.result = self.target_func(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
            logger.exception(f"线程执行失败: {e}")

    def get_result(self) -> Any:
        """获取线程执行的结果.
        
        Returns:
            线程函数的返回值或默认结果值.
            
        Raises:
            Exception: 如果线程执行过程中发生异常且未设置默认值.
        """
        if self.exception is not None:
            if self.default_result is not None:
                return self.default_result
            raise self.exception
        return self.result

    def has_exception(self) -> bool:
        """检查线程执行是否发生异常."""
        return self.exception is not None


class DecoratorFactory:
    """装饰器工厂类，提供各种实用的装饰器.
    
    此类包含了一套全面的装饰器集合，用于异常处理、性能计时、
    线程安全等功能。所有装饰器都以静态方法的形式提供。
    
    Attributes:
        _lock: 用于线程安全操作的可重入锁.
        _singleton_instances: 单例模式实例缓存.
    """

    _lock: threading.RLock = threading.RLock()
    _singleton_instances: Dict[Type[Any], Any] = {}

    @staticmethod
    def exception_handler(default_return: Any = None, 
                         error_message: str = "",
                         log_level: str = "error", 
                         exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
                         reraise: bool = False) -> Callable:
        """异常处理装饰器.
        
        此装饰器包装函数以捕获指定的异常，并返回预定义的值
        或重新抛出异常。
        
        Args:
            default_return: 发生异常时返回的值.
            error_message: 日志中错误消息的前缀字符串.
            log_level: 异常记录的日志级别.
            exception_types: 要捕获的异常类型.
            reraise: 是否重新抛出异常.
            
        Returns:
            装饰器函数.
        
        Example:
            >>> @DecoratorFactory.exception_handler(default_return=0, error_message="计算失败")
            >>> def divide(a, b):
            ...     return a / b
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    error_msg = f"函数 {func.__name__} 执行失败"
                    if error_message:
                        error_msg = f"{error_message}: {error_msg}"
                    error_msg += f" - {e}"
                    if default_return is not None:
                        error_msg += f", 返回默认值: {default_return}"
                    
                    log_with_level(error_msg, level=log_level)
                    
                    if reraise:
                        raise
                    return default_return
            return wrapper
        return decorator

    @staticmethod
    def timer(func: Callable[..., Any]) -> Callable[..., Any]:
        """性能计时装饰器.
        
        此装饰器测量并记录函数的执行时间。
        
        Args:
            func: 要测量执行时间的函数.
            
        Returns:
            包装后的函数.
            
        Example:
            >>> @DecoratorFactory.timer
            >>> def slow_operation():
            ...     time.sleep(2)
            ...     return "completed"
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            logger.info(f"开始执行函数 [{func.__name__}]")

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                logger.info(f"函数 [{func.__name__}] 执行完成: "
                           f"{elapsed * 1000:.2f}ms ({elapsed:.4f}秒)")
        return wrapper

    @staticmethod
    def thread_safe(func: Callable[..., Any]) -> Callable[..., Any]:
        """线程安全装饰器.
        
        此装饰器通过使用可重入锁确保被装饰函数的线程安全执行。
        
        Args:
            func: 要同步的函数.
            
        Returns:
            具有线程同步功能的包装函数.
            
        Example:
            >>> @DecoratorFactory.thread_safe
            >>> def critical_section():
            ...     # 线程安全的代码
            ...     pass
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with DecoratorFactory._lock:
                return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def singleton(cls: Type[Any]) -> Callable[..., Any]:
        """线程安全的单例模式类装饰器.
        
        此装饰器为类实现单例模式，确保被装饰类只能存在一个实例。
        
        Args:
            cls: 要转换为单例的类.
            
        Returns:
            返回单例实例的包装函数.
            
        Example:
            >>> @DecoratorFactory.singleton
            >>> class DatabaseConnection:
            ...     def __init__(self):
            ...         self.connected = True
        """
        @wraps(cls)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with DecoratorFactory._lock:
                if cls not in DecoratorFactory._singleton_instances:
                    DecoratorFactory._singleton_instances[cls] = cls(*args, **kwargs)
                return DecoratorFactory._singleton_instances[cls]
        return wrapper

    @staticmethod
    def retry(max_attempts: int = 3, 
              delay: float = 1.0, 
              backoff_factor: float = 1.0,
              exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
              default_return: Any = None) -> Callable:
        """重试装饰器.
        
        此装饰器为函数添加重试功能，当函数执行失败时
        可以按照配置的次数进行重试。
        
        Args:
            max_attempts: 最大重试次数.
            delay: 重试间隔时间(秒).
            backoff_factor: 退避因子，每次重试延迟时间的倍数.
            exception_types: 需要重试的异常类型.
            default_return: 所有重试失败后的默认返回值.
                
        Returns:
            装饰器函数.
            
        Example:
            >>> @DecoratorFactory.retry(max_attempts=3, delay=1.0)
            >>> def unstable_function():
            ...     # 可能失败的操作
            ...     pass
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exception_types as e:
                        last_exception = e
                        if attempt < max_attempts - 1:  # 不是最后一次尝试
                            logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, "
                                         f"{current_delay:.1f}秒后重试")
                            time.sleep(current_delay)
                            current_delay *= backoff_factor
                        else:
                            logger.error(f"函数 {func.__name__} 所有 {max_attempts} 次尝试均失败")
                
                if default_return is not None:
                    return default_return
                
                # 重新抛出最后一个异常
                if last_exception:
                    raise last_exception
                    
            return wrapper
        return decorator

    @staticmethod
    def timeout(seconds: float, default_return: Any = None) -> Callable:
        """超时控制装饰器.
        
        限制函数的最大执行时间，超时后返回默认值。
        
        Args:
            seconds: 最大允许执行时长(秒).
            default_return: 超时时的默认返回值.
            
        Returns:
            装饰器函数.
            
        Example:
            >>> @DecoratorFactory.timeout(5.0, default_return="timeout")
            >>> def slow_function():
            ...     time.sleep(10)
            ...     return "completed"
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                thread = ThreadWithResult(
                    target=func, 
                    args=args, 
                    kwargs=kwargs,
                    default_result=default_return
                )
                thread.daemon = True
                thread.start()
                thread.join(timeout=seconds)
                
                if thread.is_alive():
                    logger.warning(f"函数 {func.__name__} 执行超时 ({seconds}秒)")
                    return default_return
                
                return thread.get_result()
            return wrapper
        return decorator


class ClassDecorator:
    """类装饰器，用于自动为类的方法添加装饰器.
    
    此类提供了为类的所有公共方法自动添加装饰器的功能。
    
    Attributes:
        target_class: 被装饰的类.
        decorator_func: 要应用的装饰器函数.
        method_filter: 方法过滤函数.
    """

    def __init__(self, 
                 target_class: Type[Any],
                 decorator_func: Callable,
                 method_filter: Optional[Callable[[str, Callable], bool]] = None) -> None:
        """初始化类装饰器.
        
        Args:
            target_class: 被装饰的类.
            decorator_func: 要应用的装饰器函数.
            method_filter: 方法过滤函数，用于决定哪些方法需要装饰.
        """
        self.target_class = target_class
        self.decorator_func = decorator_func
        self.method_filter = method_filter or self._default_filter

    def _default_filter(self, name: str, method: Callable) -> bool:
        """默认的方法过滤器，过滤掉私有方法和特殊方法."""
        return not name.startswith('_') and callable(method)

    def apply(self) -> Type[Any]:
        """应用装饰器到类的所有符合条件的方法.
        
        Returns:
            装饰后的类.
        """
        methods = get_public_methods(self.target_class)
        
        for name, method in methods:
            if self.method_filter(name, method):
                try:
                    decorated_method = self.decorator_func(method)
                    setattr(self.target_class, name, decorated_method)
                except Exception as e:
                    logger.warning(f"无法装饰方法 {name}: {e}")
        
        return self.target_class

    @staticmethod
    def apply_to_instance(instance: Any,
                         err_return: Any = False,
                         retry_num: int = 1,
                         sleep_time: float = 1.0,
                         err_level: str = "exception") -> None:
        """为实例的所有公共方法添加异常处理装饰器.
        
        此方法为给定实例的所有公共方法添加异常处理和重试功能，
        替代原来的 catch_class_obj 方法。
        
        Args:
            instance: 要装饰的实例对象.
            err_return: 发生异常时的返回值.
            retry_num: 重试次数.
            sleep_time: 重试间隔时间(秒).
            err_level: 日志级别.
        """
        methods = get_public_methods(instance)
        
        for name, method in methods:
            try:
                # 创建带重试和异常处理的装饰器
                if retry_num > 1:
                    decorated_method = DecoratorFactory.retry(
                        max_attempts=retry_num,
                        delay=sleep_time,
                        default_return=err_return
                    )(method)
                else:
                    decorated_method = DecoratorFactory.exception_handler(
                        default_return=err_return,
                        log_level=err_level
                    )(method)
                
                # 将装饰后的方法绑定到实例
                setattr(instance, name, decorated_method)
            except Exception as e:
                logger.warning(f"无法为实例方法 {name} 添加装饰器: {e}")

    @staticmethod
    def exception_safe_class(exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
                           default_return: Any = None,
                           log_level: str = "error") -> Callable:
        """类装饰器，为类的所有公共方法添加异常处理.
        
        Args:
            exception_types: 要捕获的异常类型.
            default_return: 异常时的默认返回值.
            log_level: 日志级别.
            
        Returns:
            类装饰器函数.
        """
        def class_decorator(cls: Type[Any]) -> Type[Any]:
            decorator_func = DecoratorFactory.exception_handler(
                default_return=default_return,
                exception_types=exception_types,
                log_level=log_level
            )
            
            class_dec = ClassDecorator(cls, decorator_func)
            return class_dec.apply()
        
        return class_decorator


# 便捷的装饰器别名，保持向后兼容
DecoratorFactory.catch = DecoratorFactory.exception_handler
exception_handler = DecoratorFactory.exception_handler
timer = DecoratorFactory.timer
thread_safe = DecoratorFactory.thread_safe
singleton = DecoratorFactory.singleton
retry = DecoratorFactory.retry
timeout = DecoratorFactory.timeout

# 保持向后兼容的旧名称
Decorate = DecoratorFactory
Decorator = DecoratorFactory
catch = exception_handler
time_run = timer
synchronized = thread_safe
catch_retry = retry
limit_time = timeout

# 导出的公共接口
__all__ = [
    'DecoratorFactory',
    'Decorate',
    'Decorator',
    'ThreadWithResult', 
    'ClassDecorator',
    'log_with_level',
    'get_public_methods',
    'exception_handler',
    'timer',
    'thread_safe',
    'singleton',
    'retry',
    'timeout',
    # 向后兼容的别名
    'catch',
    'time_run',
    'synchronized',
    'catch_retry',
    'limit_time'
]


if __name__ == '__main__':
    # 示例用法
    @exception_handler(default_return="error occurred")
    def test_function():
        raise ValueError("测试异常")
    
    @timer
    def slow_function():
        time.sleep(0.1)
        return "completed"
    
    print(test_function())  # 输出: error occurred
    print(slow_function())  # 输出: completed (带时间日志)
