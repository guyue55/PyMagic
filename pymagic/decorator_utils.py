# coding: utf-8
"""
Decorator Utilities

常用装饰器封装模块，提供异常捕获、性能计时、线程安全等装饰器，以及自动为类的方法添加装饰器的功能。

Copyright (C) 2024-2025, 古月居。
"""

from functools import wraps
import threading
import time
from loguru import logger

def print_log(log_msg: str, level: str = None, *args, **kwargs):
    """
    输出指定等级日志，使用loguru库的日志记录功能。
    
    Args:
        level: 日志等级，如debug/info/warning/error/exception/critical/success
        log_msg: 日志信息
        *args: 传递给日志函数的位置参数
        **kwargs: 传递给日志函数的关键字参数
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
    """
    获取类的方法列表，不包括以下划线开头的方法和property属性。
    
    Args:
        cls: 要获取方法的类或对象
        
    Returns:
        list: 包含(方法名, 方法对象)元组的列表
    """
    if callable(cls):
        return [(name, getattr(cls, name))
                for name in dir(cls) if not name.startswith('_')
                and not isinstance(getattr(cls.__class__, name, None), property)
                ]
    else:
        return list()


class MyThread(threading.Thread):
    """ 
    重写多线程类，支持获取线程执行结果和超时控制。
    
    使用此类可以控制函数运行时间，超时则结束函数运行，并可获取函数返回值。
    """

    def __init__(self, target, args=(), err_result=None):
        """
        初始化线程对象。
        
        扩展了标准threading.Thread类，添加了返回值支持。
        
        Args:
            target: 目标函数
            args: 传递给目标函数的参数元组
            err_result: 发生错误时的返回值
            
        Note:
            此实现参考自: https://www.cnblogs.com/hujq1029/p/7219163.html
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args
        self.result = None
        self.err_result = err_result

    def run(self):
        """
        执行线程的目标函数并保存返回值。
        
        重写了Thread类的run方法，添加了返回值的保存。
        """
        # 接收返回值
        self.result = self.func(*self.args)

    def get_result(self):
        """
        获取线程执行的结果。
        
        如果线程尚未结束或发生异常，将返回预设的错误返回值。
        
        Returns:
            任意类型: 线程函数的返回值或预设的错误返回值
        """
        try:
            return self.result
        except Exception as e:
            logger.exception(f"线程执行失败，MyThread超时: {e}")
        return self.err_result


class Decorate:
    """
    装饰器工具类，提供各种实用的装饰器和自动装饰功能。
    
    包含异常捕获、性能计时、线程安全等装饰器，以及自动为类的方法添加装饰器的功能。
    
    Attributes:
        LOCK (RLock): 线程锁，用于线程安全操作
        DEFAULT_VALUE (bool): 默认的错误返回值
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
        """
        捕获异常装饰器，在函数发生异常时返回预设值。
        
        Args:
            result: 异常时的返回值
            err_info: 异常信息前缀
            err_level: 日志记录的异常级别
            exception: 要捕获的异常类型
            **d_kwargs: 其他参数
            
        Returns:
            callable: 装饰器函数
        
        Examples:
            @Decorate.catch(result=None, err_info="处理数据时出错")
            def process_data(data):
                # 处理可能抛出异常的代码
                return processed_data
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
        """
        测量函数运行时间的装饰器。
        
        Args:
            func: 要测量运行时间的函数
            
        Returns:
            callable: 包装后的函数，执行时会记录并输出运行时间
            
        Note:
            时间以毫秒为单位记录，同时也会转换为分钟显示
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
        """
        线程锁装饰器
                线程锁，有threading.Lock() 和 threading.RLock()
                with lock方式加锁最为简单，也可用acquire()加锁，release()释放锁。

        在Python中一个Lock对象和一个RLock对象有很多区别:
        221: lock                                    rlock
        222: lock对象无法再被其他线程获取，除非持有线程释放     rlock对象可以被其他线程多次获取
        223: lock对象可被任何线程释放                     rlock对象只能被持有的线程释放
        224: lock对象不可以被任何线程拥有                 rlock对象可以被多个线程拥有
        225: 对一个对象锁定是很快的                     对一个对象加rlock比加lock慢
        :param func:
        :return:
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            with Decorate.LOCK:
                return func(*args, **kwargs)

        return _wrapper

    @staticmethod
    def singleton(cls):
        """
        类装饰器，单例模式，线程安全
        注：放在装饰器类中调用出现问题，所以此处单独写本函数
        :return:
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
        """
        Add decorator for each method of a class.
        自动为py类的每个方法添加装饰器
        :return:
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
        """
        装饰器，捕捉异常，可设置重试次数
        
        Args:
            func_name: 被装饰的函数名
            func: 被装饰的函数
            
        Returns:
            object: 返回函数值或设置的异常返回值self.err_return
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
        """
        遍历对象的方法，获取非_开头的方法（即筛除内置方法和自定义的_、__的私有、不可重写等特殊方法）
        
        Args:
            obj: 待遍历对象/类
            flag_property: 是否包含@property装饰的函数
            
        Returns:
            list: 包含(方法名, 方法对象)元组的列表
            
        Note:
            暂不支持已装饰了@property的函数
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
