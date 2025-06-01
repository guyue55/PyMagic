# coding:utf-8
"""
日志工具模块，封装loguru库，支持生成不同的日志操作实例。

提供了便捷的日志配置和管理功能，支持多种输出格式和目标。

Copyright (C) 2012-2023, 古月居。
"""

# Standard library imports
from typing import Union
from copy import deepcopy
from sys import stderr

# import types

# Third party imports
from loguru import logger
from loguru._logger import Logger, Core


# Local imports


# 原始类名保留为注释，便于理解历史代码
class LoggerUtils(Logger):
    """
    封装loguru库，支持生成不同日志操作实例
    
    该类继承自loguru的Logger类，提供了更多便捷的日志配置和管理功能。
    支持创建多个日志实例，每个实例可以有不同的配置和输出目标。
    
    Attributes:
        logger (Logger): 全局日志实例
        DEFAULT_SINK (str): 默认日志文件路径
        FORMAT (str): 标准日志格式，不包含进程和线程信息
        FORMAT_PT (str): 包含进程和线程信息的日志格式
        FORMAT_PROCESS (str): 包含进程信息的日志格式
        FORMAT_THREAD (str): 包含线程信息的日志格式
        DEFAULT (dict): 默认日志配置参数
    
    参考：https://www.imooc.com/article/321589
    
    基本参数释义：
        sink：日志输出目标，可以是以下类型：
            - file对象，如sys.stderr或open('file.log', 'w')
            - 字符串或pathlib.Path对象，表示文件路径
            - 自定义方法，用于自行定义输出实现
            - logging模块的Handler，如FileHandler、StreamHandler等
            - coroutine function，即返回协程对象的函数
            
        level：日志输出和保存级别
        format：日志格式模板
        filter：决定每条记录是否应发送到sink的可选指令
        colorize：是否将格式化消息中的颜色标记转换为终端着色的ANSI代码
        serialize：是否在发送到sink前将记录转换为JSON字符串
        backtrace：异常跟踪是否应向上扩展，显示完整堆栈
        diagnose：异常跟踪是否显示变量值以简化调试（生产环境建议设为False）
        enqueue：是否通过多进程安全队列处理日志消息，使日志记录非阻塞
        catch：是否自动捕获sink处理日志消息时的错误
        
    当sink是协程函数时的特殊参数：
        loop：用于调度和执行异步日志任务的事件循环
        
    当sink是文件路径时的特殊参数：
        rotation：指示何时应关闭当前日志文件并开始新文件的条件
        retention：过滤旧文件的指令，用于删除旧日志文件
        compression：日志文件关闭时转换的压缩格式
        delay：是否延迟创建文件到第一条日志记录时
        mode：文件打开模式，默认为'a'（追加模式）
        buffering：文件缓冲策略
        encoding：文件编码
    """

    logger: Logger = logger
    # 默认日志文件路径
    DEFAULT_SINK = "log/logger.log"

    # 日志格式定义
    # 可用变量: {process} {thread} {process.name} {thread.name} {time} {level} 
    # {name} {function} {line} {module} {message}

    # 标准格式，不包含进程和线程信息
    FORMAT = "<green>{time:YY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | " \
             "<cyan>[{module}</cyan>:<cyan>{" \
             "function}</cyan>:<cyan>{line}]</cyan>: " \
             "<level>{message}</level>"
    # 消息格式, 显示: 增加进程和线程信息
    FORMAT_PT = "<green>{time:YY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | " \
                "<yellow>[pid{process: <4}:{thread.name: <4}]</yellow>| <cyan>[{" \
                "module}</cyan>:<cyan>{" \
                "function}</cyan>:<cyan>{line}]</cyan>: " \
                "<level>{message}</level>"
    # 消息格式, 显示: 增加进程信息
    FORMAT_PROCESS = "<green>{time:YY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | " \
                     "<yellow>[pid{process: <4}]</yellow>| <cyan>[{module}</cyan>:<cyan>{" \
                     "function}</cyan>:<cyan>{line}]</cyan>: " \
                     "<level>{message}</level>"
    # 消息格式, 显示: 增加线程信息
    FORMAT_THREAD = "<green>{time:YY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | " \
                    "<yellow>[{thread.name: <2}]</yellow>| <cyan>[{module}</cyan>:<cyan>{" \
                    "function}</cyan>:<cyan>{line}]</cyan>: " \
                    "<level>{message}</level>"
    # 默认配置
    DEFAULT = dict(
        # 操作目标
        # sink=None,
        sink=DEFAULT_SINK,
        # 日志的轮转策略, rotation 参数支持大小和时间两种,
        # 时间单位有：second、minute、hour、day 和 week，
        # 以及自定义的时间格式，如 W0:00 表示每周日的午夜，0:00 表示每天的午夜。
        rotation='50 MB',
        # rotation='1 day',  # 每天轮转一次
        backtrace=True,  # 启用轮转回溯，以避免轮转过程中丢失日志。
        retention='7 days',  # 最多留存 7 天
        # 异常跟踪是否应显示变量值以便于调试。在生产中应将其设置为“False”，以避免泄露敏感数据。
        diagnose=True,
        # 消息格式, 可选择是否包含 进程和线程信息 {process} {thread}
        # format=FORMAT,
        format=FORMAT_THREAD,  # 包含线程信息
        encoding='utf-8',
        level="INFO",
        # 在后台异步进行日志写入, 可能会导致一些异步处理的影响, 如: 日志的实时性可能会有所降低
        enqueue=True,
        # 是否延迟日志消息的处理, 配合enqueue=True参数, 延迟创建文件，有日志输出才生成文件
        delay=True,
        compression='zip'  # 压缩格式, 压缩轮转的日志文件
        # serialize=True,  # 序列化日志消息
        # colorize=True  # 输出文件带色彩
    )

    @staticmethod
    def get_log() -> Logger:
        """获取全局日志实例。
        
        Returns:
            Logger: 全局日志实例
        """
        return logger

    @classmethod
    @logger.catch()
    def set_log(cls, log_obj: Union[Logger, str] = None, sink=None, level="INFO",
                rotation="50 MB", retention="7 days", filter_level: str = None,
                output_stderr: bool = True,
                output_file: bool = True,
                **kwargs):
        """
        配置日志实例。
        
        Args:
            log_obj: 日志实例或日志文件路径
            sink: 日志输出目标，可以是文件路径或file对象
            level: 日志级别，如"INFO"、"DEBUG"、"ERROR"等
            rotation: 日志轮转策略，如"50 MB"或"1 day"
            retention: 日志保留时间，如"7 days"
            filter_level: 过滤指定级别的日志，如"ERROR"将错误日志单独记录
            output_stderr: 是否输出到控制台
            output_file: 是否输出到文件
            **kwargs: 其他loguru配置参数
            
        Returns:
            Logger: 配置后的日志实例
        """
        # 去除可能存在的logging库参数
        kwargs.pop("log_name", "")
        kwargs.pop("log_level", "")

        sink = kwargs.pop("log_filename", sink)
        # 为了符合习惯, 默认文件名
        if log_obj and isinstance(log_obj, str):
            sink = log_obj
            log_obj = None

        if not sink:
            sink = LoggerUtils.DEFAULT_SINK

        if not log_obj:
            log_obj = LoggerUtils.get_log()
        # log_obj.debug("set log...: %s" % sink)
        # 配置
        setting = deepcopy(LoggerUtils.DEFAULT)

        # 日志文件
        # 如: 'test_{time}.log'  # test_2020-12-10_16-59-15_207786.log
        setting["sink"] = sink

        # 日志级别
        setting["level"] = level

        # 保留大小
        setting["rotation"] = rotation
        # 保留时间
        setting["retention"] = retention

        # 日志过滤
        if filter_level:
            setting["filter"] = lambda x: filter_level in str(x['level']).upper()
        # 更新配置
        setting.update(kwargs)

        '''
        logger.add('runtime_{time}.log', rotation="500 MB")
        通过这样的配置我们就可以实现每 500MB 存储一个文件，每个 log 文件过大就会新创建一个 log 文件。
        我们在配置 log 名字时加上了一个 time 占位符，这样在生成时可以自动将时间替换进去，生成一个文件名包含时间的 log 文件。
        '''

        ''' 删除重复处理器, 因为同一个日志示例重复add会导致日志重复输出 '''
        # 移除所有旧处理器配置
        # log_obj.remove()
        # 查找并移除旧的处理器
        # if log_obj._core.handlers:
        #     for handler_id, handler in log_obj._core.handlers.items():
        #         if hasattr(handler, "_name") \
        #                 and getattr(handler, "_name") == "'%s'" % sink:
        #             # 移除特定的处理器
        #             log_obj.remove(handler_id)
        #             break

        # 自定义处理器记录, sink: [处理器id]
        if not hasattr(log_obj, "_guyue_record_handlers"):
            setattr(log_obj, "_guyue_record_handlers", dict())
        record_handlers = getattr(log_obj, "_guyue_record_handlers")

        ''' 同一级别的日志输出仅保留一份, 避免重复输出 '''
        # 记录标志
        flag_key = level
        # 首次记录, 直接清除
        if not record_handlers:
            if output_stderr:
                # 移除所有旧处理器配置, 否则会遗留默认的控制台输出配置, 导致重复输出
                log_obj.remove()
        else:
            # 删除相同(日志文件)的处理器配置
            if flag_key and record_handlers.get(flag_key):
                print("[Log Set] 清除旧的(日志文件)的处理器配置: %s" % flag_key)
                for handler_id in record_handlers.pop(flag_key):
                    log_obj.remove(handler_id)

        # 记录处理器id
        record_sink = list()
        record_handlers[flag_key] = record_sink
        if output_stderr:
            # 添加控制台输出配置
            handler_id_st = log_obj.add(stderr, format=setting["format"], level=setting["level"],
                                        colorize=setting.get("colorize", True), enqueue=True)
            record_sink.append(handler_id_st)

        if output_file:
            setting.pop("colorize", "")
            # 添加日志文件输出配置, 且默认不带色彩(colorize=False)
            handler_id_file = log_obj.add(**setting)
            # 记录处理器id
            record_sink.append(handler_id_file)

        # 控制台输出一个就够了, 否则重复, 所以记录到一起方便清除
        # record_handlers.setdefault("stderr", dict())[handler_id_st] = log_obj
        # cls.RECORD_HANDLERS.setdefault("stderr", dict())[handler_id_st] = log_obj

        # 设置/添加功能函数
        cls.set_log_func(log_obj)
        return log_obj

    @classmethod
    def set_log_func(cls, log_obj: Logger):
        """
        设置/添加功能函数
        :return:
        """
        # 添加功能函数
        log_obj.get_log = cls.get_log
        log_obj.set_log = cls.set_log
        log_obj.new = cls.new
        if not hasattr(log_obj, "warn"):
            log_obj.warn = log_obj.warning

    @classmethod
    def new(cls, sink: str, level="INFO", **kwargs) -> Logger:
        """
        生成新日志实例
        :param sink: 日志文件路径
        :param level: 日志级别
        :param kwargs: 其余参数
        :return:
        """

        import atexit
        import sys

        from loguru import _defaults as defaults

        # logger_new = Logger(Core(), None, 0, False, False, False, False, True, None, {})
        logger_new = LoggerUtils(Core(), None, 0, False, False, False, False, True, None, {})

        if defaults.LOGURU_AUTOINIT and sys.stderr:
            logger_new.add(sys.stderr)
        # 注册函数, 在Python解释器退出时执行
        atexit.register(logger_new.remove)

        # 设置
        cls.set_log(logger_new, sink=sink, level=level, **kwargs)
        return logger_new


# 设置日志实例
LoggerUtils.set_log(logger)

# (这里为了方便编辑器联想重复设置) 添加功能函数,
logger.get_log = LoggerUtils.get_log
logger.set_log = LoggerUtils.set_log
logger.new = LoggerUtils.new
