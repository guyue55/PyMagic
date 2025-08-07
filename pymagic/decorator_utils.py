# -*- coding: utf-8 -*-
"""PyMagic装饰器工具模块.

本模块提供了一套全面的实用装饰器集合，用于异常处理、性能计时、
线程安全以及自动为类方法应用装饰器等功能。

类:
    MyThread: 增强的线程类，支持返回值获取和超时控制
    Decorate: 主要的装饰器工具类，包含各种装饰器

函数:
    print_log: 使用loguru的增强日志记录函数
    class_func_list: 获取类方法列表，排除私有方法

示例:
    装饰器的基本用法:
    
    >>> from pymagic.decorator_utils import Decorate
    >>> 
    >>> @Decorate.catch(result=None)
    >>> def risky_function():
    ...     raise ValueError("出现错误")
    ...     return "success"
    >>> 
    >>> result = risky_function()  # 返回None而不是抛出异常
    >>> 
    >>> @Decorate.time_run
    >>> def slow_function():
    ...     time.sleep(1)
    ...     return "done"

作者: Guyue
许可证: MIT
版权所有 (C) 2024-2025, 古月居.
"""

from functools import wraps
import threading
import time
from loguru import logger

def print_log(log_msg: str, level: str = None, *args, **kwargs):
    """使用loguru库输出指定级别的日志消息.
    
    此函数提供了一种便捷的方式，使用loguru日志库记录不同
    严重级别的日志消息。
    
    参数:
        log_msg: 要记录的日志消息.
        level: 日志级别，如debug/info/warning/error/exception/critical/success.
            如果为None或"exception"，默认为"error".
        *args: 传递给日志函数的位置参数.
        **kwargs: 传递给日志函数的关键字参数.
    
    注意:
        "exception"级别会映射到"error"级别，因为loguru
        使用"error"进行异常日志记录.
    """
    # loguru的exception实际为error
    if not level or level.lower() == "exception":
        level = "error"
    # 日志等级
    level = level.upper()
    _options = logger._options
    if level == "ERROR":
        _options = (True,) + _options[1:]
    (exception, depth, record, lazy, colors, raw, capture, patcher, extra) = _options
    options = (exception, depth + 1, record, lazy, colors, raw, capture, patcher, extra)
    logger._log(level, False, options, log_msg, args, kwargs)


def class_func_list(cls: object):
    """获取类方法列表，排除私有方法和属性.
    
    此函数返回类或对象的公共方法列表，过滤掉以下划线开头的方法
    和属性特性。
    
    参数:
        cls: 要获取方法的类或对象.
        
    返回:
        list: 包含(方法名, 方法对象)元组的列表，
            包含所有公共可调用方法.
    
    示例:
        >>> class MyClass:
        ...     def public_method(self):
        ...         pass
        ...     def _private_method(self):
        ...         pass
        >>> methods = class_func_list(MyClass)
        >>> print([name for name, _ in methods])  # ['public_method']
    """
    if callable(cls):
        return [(name, getattr(cls, name))
                for name in dir(cls) if not name.startswith('_')
                and not isinstance(getattr(cls.__class__, name, None), property)
                ]
    else:
        return list()


class MyThread(threading.Thread):
    """增强的线程类，支持返回值获取和超时控制.
    
    此类扩展了标准的threading.Thread，支持从线程执行中获取
    返回值，并为函数执行提供超时控制功能。
    
    属性:
        func: 在线程中执行的目标函数.
        args: 传递给目标函数的参数元组.
        result: 目标函数执行的返回值.
        err_result: 发生错误时返回的值.
    
    示例:
        >>> def slow_function(x, y):
        ...     time.sleep(1)
        ...     return x + y
        >>> 
        >>> thread = MyThread(target=slow_function, args=(1, 2), err_result=0)
        >>> thread.start()
        >>> thread.join()
        >>> result = thread.get_result()  # 返回3
    
    注意:
        此实现基于:
        https://www.cnblogs.com/hujq1029/p/7219163.html
    """

    def __init__(self, target, args=(), err_result=None):
        """初始化增强的线程对象.
        
        通过添加对目标函数结果的捕获和返回支持，
        扩展了标准的threading.Thread类。
        
        参数:
            target: 在线程中执行的目标函数.
            args: 传递给目标函数的参数元组.
                默认为空元组.
            err_result: 执行过程中发生错误时返回的值.
                默认为None.
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args
        self.result = None
        self.err_result = err_result

    def run(self):
        """执行目标函数并保存其返回值.
        
        重写Thread类的run方法，以捕获并存储
        目标函数执行的返回值。
        """
        # 接收返回值
        self.result = self.func(*self.args)

    def get_result(self):
        """获取线程执行的结果.
        
        返回目标函数执行的结果。
        如果线程尚未完成或发生异常，
        返回预定义的错误结果值。
        
        返回:
            Any: 线程函数的返回值或
                预定义的错误结果值.
        
        注意:
            此方法应在线程完成执行后调用
            (在join()之后)以获得有意义的结果.
        """
        try:
            return self.result
        except Exception as e:
            logger.exception(f"线程执行失败，MyThread超时: {e}")
        return self.err_result


class Decorate:
    """装饰器工具类，提供各种实用的装饰器.
    
    此类包含了一套全面的装饰器集合，用于异常处理、性能计时、
    线程安全以及自动为类方法应用装饰器等功能。
    
    该类提供静态装饰器方法和实例方法，
    用于自动为类的所有方法应用装饰器。
    
    属性:
        LOCK (RLock): 用于线程安全操作的线程锁.
        DEFAULT_VALUE (bool): 默认错误返回值.
    
    示例:
        使用静态装饰器:
        
        >>> @Decorate.catch(result="error")
        >>> def risky_function():
        ...     raise ValueError("出现错误")
        >>> 
        >>> @Decorate.time_run
        >>> def slow_function():
        ...     time.sleep(1)
        
        自动装饰类:
        
        >>> class MyClass:
        ...     def method1(self):
        ...         return "result1"
        >>> 
        >>> Decorate(MyClass).catch_class_obj()
    """

    # 线程锁
    LOCK = threading.RLock()
    # 默认返回值
    DEFAULT_VALUE = False

    """ 一、常用装饰器 """

    @staticmethod
    def catch(result=False, err_info: str = "",
              err_level: str = "exception", exception: object = Exception,
              **d_kwargs):
        """异常捕获装饰器，在异常时返回预设值.
        
        此装饰器包装函数以捕获指定的异常，并返回预定义的值
        而不是让异常传播。它还使用指定的日志级别记录异常详情。
        
        参数:
            result: 发生异常时返回的值. 默认为False.
            err_info: 日志中错误消息的前缀字符串. 默认为空字符串.
            err_level: 异常记录的日志级别 (debug/info/warning/error/exception/critical).
                默认为"exception".
            exception: 要捕获的异常类型. 默认为Exception(捕获所有异常).
            **d_kwargs: 用于未来扩展性的额外关键字参数.
            
        返回:
            callable: 包装目标函数的装饰器函数.
        
        示例:
            带自定义返回值的基本用法:
            
            >>> @Decorate.catch(result=None, err_info="数据处理失败")
            >>> def process_data(data):
            ...     # 可能抛出异常的代码
            ...     return processed_data
            
            捕获特定异常类型:
            
            >>> @Decorate.catch(result=0, exception=ValueError)
            >>> def parse_number(text):
            ...     return int(text)
        
        注意:
            装饰器可以带参数或不带参数使用。不带参数使用时，
            使用默认值。
        """

        def decorator(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    log_err = ("fail, %s() %s: %s, \n\t default return: %s" %
                               (func.__name__, err_info, e, str(result)))
                    print_log(log_err, err_level=err_level)
                return result

            return _wrapper

        # 检查decorator是否在没有参数的情况下使用, 避免传参异常
        if callable(result) and not d_kwargs:
            return decorator(result)

        return decorator

    @staticmethod
    def time_run(func):
        """测量函数执行时间的装饰器.
        
        此装饰器包装函数以测量并记录其执行时间。
        它记录开始和结束时间，计算经过的时间，
        并以毫秒和分钟为单位记录结果。
        
        参数:
            func: 要测量执行时间的函数.
            
        返回:
            callable: 调用时记录执行时间的包装函数.
            
        示例:
            >>> @Decorate.time_run
            >>> def slow_operation():
            ...     time.sleep(2)
            ...     return "completed"
            >>> 
            >>> result = slow_operation()  # 记录执行时间
        
        注意:
            时间以毫秒为单位记录，并转换为分钟以提高可读性。
            使用time.perf_counter()获得高精度。
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            logger.info(
                f"\t Begin run time func [{func.__name__}]: {start_time:.8f} ms")

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            elapsed = end_time - start_time
            logger.info(f"\t End run time func [{func.__name__}]: {elapsed * 1000.0:.8f} ms, {elapsed / 60.0:.8f} 分钟")

            return result

        return _wrapper

    @staticmethod
    def synchronized(func):
        """使用RLock的线程同步装饰器.
        
        此装饰器通过使用可重入锁(RLock)确保被装饰函数的线程安全执行。
        它防止多个线程同时访问同一函数时出现竞态条件。
        
        装饰器使用'with lock'模式进行自动锁获取和释放，
        这比手动acquire()/release()更安全。
        
        参数:
            func: 要同步的函数.
            
        返回:
            callable: 具有线程同步功能的包装函数.
            
        示例:
            >>> @Decorate.synchronized
            >>> def critical_section():
            ...     # 线程安全的代码
            ...     shared_resource += 1
            ...     return shared_resource
        
        注意:
            Python中Lock和RLock的区别:
            - Lock: 释放前不能被其他线程再次获取
            - RLock: 可以被同一线程多次获取
            - Lock: 可以被任何线程释放
            - RLock: 只能被获取它的线程释放
            - Lock: 不能被任何线程拥有
            - RLock: 可以被多个线程拥有
            - Lock: 比RLock快
            - RLock: 比Lock慢但更灵活
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            with Decorate.LOCK:
                return func(*args, **kwargs)

        return _wrapper

    @staticmethod
    def singleton(cls):
        """线程安全的单例模式类装饰器.
        
        此装饰器为类实现单例模式，确保被装饰类只能存在一个实例。
        实现使用RLock保证线程安全。
        
        参数:
            cls: 要转换为单例的类.
            
        返回:
            callable: 返回单例实例的包装函数.
            
        示例:
            >>> @Decorate.singleton
            >>> class DatabaseConnection:
            ...     def __init__(self):
            ...         self.connected = True
            >>> 
            >>> db1 = DatabaseConnection()
            >>> db2 = DatabaseConnection()
            >>> assert db1 is db2  # 同一个实例
        
        注意:
            此函数实现为独立函数而不是装饰器类中的方法，
            以避免方法解析和类装饰的潜在问题。
        """
        instances = {}

        @wraps(cls)
        def wrapper(*args, **kw):
            # 线程锁
            with Decorate.LOCK:
                if cls not in instances:
                    instances[cls] = cls(*args, **kw)
                return instances[cls]

        return wrapper

    @staticmethod
    def catch_retry(err_return=False, **d_kwargs):
        """
        (静态)捕捉异常，可设置重试次数
        
        Args:
            err_return: 异常时的返回值
            **d_kwargs: 其他参数
                retry_num (int): 重试次数，小于1时为死循环
                sleep_time (int): 重试间隔时间(秒)
                
        Returns:
            callable: 装饰器函数
        """

        def decorator(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                # err_return = d_kwargs.get("err_return", False)  # 异常返回值
                retry_num = d_kwargs.get("retry_num", 1)  # 循环重试次数
                sleep_time = d_kwargs.get("sleep_time", 3)  # 循环休眠时间，单位秒

                flag = False  # 标志位: 是否死循环
                if retry_num < 1:  # 死循环
                    flag = True
                # 循环处理异常
                while flag or retry_num > 0:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        logger.exception(
                            "error, try_class %s, %s(): %s, \n\t default return: %s"
                            % (retry_num, func.__name__, e, str(err_return)))
                    if not flag:
                        retry_num -= 1
                        if retry_num > 0:
                            time.sleep(sleep_time)
                    else:
                        time.sleep(sleep_time)
                return err_return

            return _wrapper

        # 检查decorator是否在没有参数的情况下使用, 避免传参异常
        if callable(err_return) and not d_kwargs:
            return decorator(err_return)

        return decorator

    """ 二、自动为py类的每个方法添加装饰器 """

    """
        方式1：使用时需要new 一个Decorate对象
        方式2：静态直接以类名调用即可
    """

    def __init__(self, obj: object, err_return: object = False,
                 retry_num: int = 1, sleep_time: float = 3,
                 err_level: str = "exception", **kwargs):
        """
        初始化装饰器
        
        Args:
            obj: 被装饰的类的实例
            err_return: 捕获异常时的返回值
            retry_num: 异常重试次数
            sleep_time: 异常休眠时间
            err_level: 日志等级, 如: debug|info|warn|error|exception
            **kwargs: 其他参数
        """
        # logger.info("装饰器初始化...")
        # 被装饰的类的实例
        self.obj = obj
        # 异常返回值
        self.err_return = err_return
        # 循环重试时间
        self.retry_num = retry_num
        # 循环休眠时间，单位秒
        self.sleep_time = sleep_time
        # 日志等级
        self.err_level = err_level
        # print([(name, getattr(self, name)) for name in dir(self) if not name.startswith('_')])
        # 线程锁
        self.lock = threading.Lock()
        # 死循环处理标志位，为True时启用
        self.flag_retry = False
        if self.retry_num < 1:  # 死循环
            self.flag_retry = True

    def catch_class_obj(self):
        """为类的每个方法添加装饰器.
        
        自动为Python类的每个公共方法添加异常捕获装饰器，
        实现统一的异常处理和重试机制。
        
        返回:
            None: 此方法直接修改类对象，无返回值.
        """
        # 获取类的方法列表
        for name, fn in self.iter_func(self.obj):
            # 是否为可调用方法
            if not isinstance(fn, property) and callable(fn):
                # print("装饰的函数名：", fn.__name__)
                self.catch_retry_obj(name, fn)
        # 获取类的方法列表
        for name, fn in self.iter_func(self.obj):
            # 是否为可调用方法
            # if callable(fn):
            if not isinstance(fn, property) and callable(fn):
                # print("装饰的函数名：", fn.__name__)
                self.catch_retry_obj(name, fn)
            # else:
            #     logger.warning("func %s: %s, %s" % (name, fn, type(fn)))

    def catch_retry_obj(self, func_name: str, func):
        """对象方法装饰器，捕捉异常并支持重试.
        
        为指定的函数添加异常捕获和重试功能，当函数执行失败时
        可以按照配置的次数进行重试，或者进行无限重试。
        
        参数:
            func_name: 被装饰的函数名.
            func: 被装饰的函数对象.
            
        返回:
            object: 返回函数执行结果或设置的异常返回值self.err_return.
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            # 重试次数
            retry_num = self.retry_num
            # 循环处理异常，死循环或重试一定次数
            while self.flag_retry or retry_num > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print_log("error, (catch retry_num %s) %s(): %s, "
                              "\n\t default return: %s" %
                              (retry_num, func.__name__, e,
                               str(self.err_return)), err_level=self.err_level)
                # 是否为死循环
                if not self.flag_retry:
                    # 重试次数-1
                    retry_num -= 1
                    if retry_num > 0:
                        time.sleep(self.sleep_time)
                else:
                    # 休息等待
                    time.sleep(self.sleep_time)
            return self.err_return

        try:
            setattr(self.obj, func_name, _wrapper)
        except:
            pass
        return _wrapper

    @staticmethod
    def iter_func(obj, flag_property: bool = False):
        """遍历对象的方法，获取公共方法列表.
        
        遍历对象的方法，获取非下划线开头的方法，即筛除内置方法
        和自定义的私有、不可重写等特殊方法。
        
        参数:
            obj: 待遍历的对象或类.
            flag_property: 是否包含@property装饰的函数.
                默认为False.
            
        返回:
            list: 包含(方法名, 方法对象)元组的列表.
            
        注意:
            暂不支持已装饰了@property的函数.
        """
        if not flag_property:
            # 非 _ 开头的方法列表
            return [(name, getattr(obj, name))
                    for name in dir(obj) if not name.startswith('_')
                    and not isinstance(getattr(obj.__class__, name, None), property)]
        else:
            list_func = []
            for name in dir(obj):
                if not name.startswith('_'):
                    # 获取属性方法的原始函数
                    original_func = getattr(obj.__class__, name, None)
                    # property装饰的函数
                    if isinstance(original_func, property):
                        try:
                            pass
                            # list_func.append((name, getattr(self.obj, "%s.fget" % name)))
                            # list_func.append((name, original_func.fget(self.obj)))
                            # list_func.append((name, original_func.__get__))
                        except Exception as e:
                            logger.exception(e)
                    # 可调用的函数
                    elif callable(original_func):
                        list_func.append((name, getattr(obj, name)))

            return list_func

    @staticmethod
    def catch_class(cls, **kwargs):
        """
         Add decorator for each method of a class.
        (静态) 类装饰器, 自动为py类的每个方法添加装饰器
        :param cls: 待装饰类
        :param kwargs: 参数
        :return:
        """

        # 获取类的方法列表
        for name, fn in class_func_list(cls):
            for name, fn in Decorate.iter_func(cls, **kwargs):
                if callable(fn):  # 是否为可调用方法
                    Decorate._catch_retry_class(cls, name, fn)
        return cls

        # class Wrapper(cls):
        #     # def __init__(self, *args, **kwargs):
        #     #     self.instance = cls(*args, **kwargs)
        #     # def __init__(self, *args, **kwargs):
        #     #     super().__init__(*args, **kwargs)  # 调用原始类的初始化方法
        #
        #     def __getattribute__(self, name):
        #         if not name.startswith('_'):
        #             # 获取属性方法的原始函数
        #             attr = getattr(cls, name, None)
        #             if callable(attr):
        #                 # attr = getattr(self.instance, name)
        #                 attr = super().__getattribute__(name)
        #                 logger.info("添加捕捉: %s" % attr)
        #                 # return cls.catch(Exception)(attr)
        #                 return Decorate.catch()(attr)
        #                 # return logger.catch()(attr)
        #             else:
        #                 logger.info("不捕捉: %s" % attr)
        #         # return getattr(self.instance, name)
        #         return super().__getattribute__(name)
        #
        # Wrapper.__name__ = cls.__name__
        # # 复制原始类的文档字符串
        # Wrapper.__doc__ = cls.__doc__
        # return Wrapper

    @staticmethod
    def _catch_retry_class(cls: object, name: str, func, **d_kwargs):
        """
        捕捉异常(传入函数func)，可设置重试次数
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            flag = False  # 死循环处理标志位，为True时启用
            err_return = d_kwargs.get("err_return", False)  # 异常返回值
            retry_num = d_kwargs.get("retry_num", 1)  # 循环重试次数
            sleep_time = d_kwargs.get("sleep_time", 3)  # 循环休眠时间，单位秒

            if retry_num < 1:  # 死循环
                flag = True
            # 循环处理异常
            while flag or retry_num > 0:
                try:
                    result = func(*args, **kwargs)
                    if result == err_return:
                        print(
                            "Warn, result is %s, default return True: %s" %
                            (result, func.__name__))
                        return True
                    else:
                        return result
                except Exception as e:
                    logger.exception("error, try_retry2 %s, %s : %s, \n "
                                     "default return: %s" %
                                     (retry_num, func.__name__, e, str(err_return)))
                if not flag:
                    retry_num -= 1
                    if retry_num > 0:
                        time.sleep(sleep_time)
                else:
                    time.sleep(sleep_time)
            return err_return

        setattr(cls, name, _wrapper)
        return _wrapper

    @staticmethod
    def limit_time(limit_time: int, err_result=None):
        """
        限制真实请求时间或函数执行时间
        :param limit_time: 设置最大允许执行时长, 单位:秒
        :param err_result: 默认返回值
        :return: 未超时返回被装饰函数返回值, 超时则返回 None
        """

        def functions(func):
            # 执行操作
            def run(*params):
                thread_func = MyThread(
                    target=func, args=params, err_result=err_result)
                # 主线程结束(超出时长), 则线程方法结束
                thread_func.setDaemon(True)
                thread_func.start()
                # 计算分段沉睡次数
                sleep_num = int(limit_time // 1)
                sleep_nums = round(limit_time % 1, 1)
                # 多次短暂沉睡并尝试获取返回值
                for i in range(sleep_num):
                    time.sleep(0.5)
                    info = thread_func.get_result()
                    if info:
                        return info
                time.sleep(sleep_nums)
                # 最终返回值(不论线程是否已结束)
                if thread_func.get_result():
                    return thread_func.get_result()
                else:
                    # print("请求超时: %s" % func.__name__)
                    logger.warning("请求超时: %s" % func.__name__)
                    return err_result  # 超时返回  可以自定义

            return run

        return functions


# 方便直接导入使用
catch = Decorate.catch
catch_retry = Decorate.catch_retry
singleton = Decorate.singleton
synchronized = Decorate.synchronized
# __all__ = ["synchronized", "catch", "catch_retry", "singleton"]


if __name__ == '__main__':
    pass
    # 工具类实例化
    # utils = Decorate()

    # obj_tmp = Foo()
    # obj_tmp.interface1()
    # obj_tmp.interface2()
    # obj_tmp.interface1()
    # obj_tmp.interface2()
    # obj_tmp._interface3()
    # print(obj_tmp.interface1.__name__)
    '''
    print(dir(obj))
    print("---------------------")
    for item in [(name,getattr(obj, name)) for name in dir(obj)]:
        print(item)'''

    # raise_test()
    # print(dir(Foo()))
    # class_func_list(Decorate)

    # print(class_func_list(RedisUtils))
