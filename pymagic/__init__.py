# -*- coding: utf-8 -*-
"""PyMagic - Python开发实用工具库.

此包为Python开发提供了一套全面的实用工具，
包括日志工具、装饰器、通用工具，以及具有内置异常处理
和地址解析功能的基础类。

模块:
    _base: 具有异常处理和地址解析功能的基础类
    decorator_utils: 有用装饰器的集合
    logger_utils: 基于loguru的增强日志工具
    tools_utils: 通用实用函数和工具

Example:
    PyMagic组件的基本用法:
    
    >>> from pymagic import Base, Tools, logger
    >>> from pymagic.decorator_utils import Decorate
    >>> 
    >>> # 使用具有自动异常处理的基础类
    >>> class MyClass(Base):
    ...     def my_method(self):
    ...         return "Hello PyMagic!"
    >>> 
    >>> # 使用日志工具
    >>> logger.info("PyMagic is working!")
    >>> 
    >>> # 使用实用函数
    >>> system_type = Tools.get_system_type()

作者: Guyue <guyuecw@qq.com>
许可证: MIT
版本: 0.0.1
"""

# Package metadata
__version__ = "0.0.1"
__author__ = "Guyue"
__email__ = "guyuecw@qq.com"
__license__ = "MIT"
__description__ = "A utility library for Python development"

# Import core components
from ._base import Base
from .decorator_utils import Decorate
from .logger_utils import logger, LoggerUtils
from .tools_utils import Tools

# Define public API
__all__ = [
    "Base",
    "Decorate", 
    "logger",
    "LoggerUtils",
    "Tools",
]