# coding: utf-8
"""
基础父类，用于继承的模板。

提供了异常捕获、日志记录、地址解析等基础功能，可作为其他类的父类使用。

Copyright (C) 2012-2023, 古月居。
"""

# Standard library imports
from typing import Any, Optional
from threading import RLock

# Third party imports
from loguru import logger

# Local imports
from pymagic.tools_utils import Tools
from pymagic.decorator_utils import Decorate


class Base:
    """
    基础父类，提供异常捕获、日志记录和地址解析等功能。
    
    可作为其他类的父类使用，自动为子类方法添加异常捕获和日志记录功能。
    支持解析各种连接地址格式，如Redis、FTP等地址。
    
    Attributes:
        logger: 日志实例，用于记录日志
        LOCK: 线程锁，用于线程安全操作
    """
    logger = logger
    LOCK = RLock()

    def __init__(self, **kwargs):
        """
        初始化基础类。
        
        Args:
            **kwargs: 关键字参数
                _parse_addr (bool): 是否自动解析地址，默认为True
                _catch (bool): 是否自动添加异常捕获，默认为True
                err_return (Any): 异常时的返回值，默认为False
                retry_num (int): 异常重试次数，默认为1
                sleep_time (float): 异常重试间隔时间，默认为1秒
                err_level (str): 异常日志级别，默认为"exception"
        """
        # 自动解析连接地址，如：Redis、FTP地址等
        if kwargs.get("_parse_addr", True):
            self._parse_address()

        # 自动为类的所有非下划线开头的方法添加异常捕获装饰器
        if kwargs.get("_catch", True):
            err_return: Any = kwargs.get("err_return", False)
            retry_num: int = kwargs.get("retry_num", 1)
            sleep_time: float = kwargs.get("sleep_time", 1)
            err_level: str = kwargs.get("err_level", "exception")

            # 注: 暂不支持已装饰了@property的函数
            Decorate(self,
                     err_return=err_return,
                     retry_num=retry_num,
                     sleep_time=sleep_time,
                     err_level=err_level).catch_class_obj()

    def __enter__(self) -> 'Base':
        """上下文管理器入口。
        
        Returns:
            Base: 返回自身实例
        """
        return self

    @logger.catch()
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        上下文管理器退出时调用，自动关闭资源。
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        if hasattr(self, "close"):
            getattr(self, "close")()

    @property
    def Tools(self):
        """
        获取工具类。
        
        Returns:
            Tools: 工具类，包含各种实用函数
        """
        return Tools

    @property
    def Decorate(self):
        """
        获取装饰器类。
        
        Returns:
            Decorate: 装饰器类，包含各种实用装饰器
        """
        return Decorate

    def close(self) -> None:
        """
        关闭资源，配合with语句使用。
        
        子类可重写此方法以实现资源的释放。
        """
        pass

    def _parse_address(self, address: Optional[str] = None) -> None:
        """
        解析连接地址字符串，支持多种格式。
        
        支持的格式:
            - 简单格式: "host:port" (如 "192.168.1.181:21")
            - 带认证格式: "user:password@host:port" (如 "user:pass@192.168.1.181:21")
            - Redis格式: "host:port:db" 或 "user:password@host:port:db"
            - FTP路径格式: "host:port/path" 或 "user:password@host:port/path"
        
        解析结果会设置到对象的相应属性中:
            - host/port: 主机和端口
            - user/password: 用户名和密码(如果提供)
            - db: 数据库编号(Redis格式)
            - addr_suffix: 其他后缀信息
        
        Args:
            address: 待解析的地址字符串，如果为None则尝试从对象的_address或address属性获取
        """
        # 如果未提供地址，尝试从对象属性获取
        if not address:
            if hasattr(self, "_address"):
                address = getattr(self, "_address")
            elif hasattr(self, "address"):
                address = getattr(self, "address")

        # 验证地址格式
        if not address or not isinstance(address, str) or ":" not in address:
            return

        # 检查属性是否使用下划线前缀（如 _host 而不是 host）
        use_prefix = hasattr(self, "_host")

        # 解析地址组件：host, port, user, password 和可能的 db
        logger.debug(f"解析地址: {address}")

        # 处理用户名和密码部分
        if "@" in address:
            # 格式: user:password@host:port
            host_part = address.rsplit("@", maxsplit=1)[1]  # host:port 部分
            user_part = address.rsplit("@", maxsplit=1)[0]  # user:password 部分

            # 设置主机名
            host = host_part.split(":")[0]
            port = host_part.split(":", 1)[1] if ":" in host_part else ""

            # 设置用户名和密码（密码可能包含:字符，所以只在第一个:处分割）
            user = user_part.split(":", maxsplit=1)[0]
            password = user_part.split(":", maxsplit=1)[1] if ":" in user_part else ""

            # 根据属性命名方式设置值
            if use_prefix:
                self._host = host
                self._user = user
                self._password = password
            else:
                self.host = host
                self.user = user
                self.password = password
        else:
            # 格式: host:port
            host = address.split(":")[0]
            port = address.split(":", 1)[1] if ":" in address else ""

            # 根据属性命名方式设置值
            if use_prefix:
                self._host = host
            else:
                self.host = host
        # 处理端口和可能的额外信息（如Redis的db或FTP的路径）
        if port:
            # 检查端口中是否包含额外信息
            if ":" in port or "/" in port:
                separator = ":" if ":" in port else "/"
                suffix = port.rsplit(separator, 1)[1]
                port = port.split(separator, 1)[0]

                # 处理FTP路径，添加前导斜杠
                if separator == "/":
                    suffix = "/" + suffix

                # 处理Redis数据库编号或其他后缀
                if suffix.isdigit() and (hasattr(self, "_db") or hasattr(self, "db")):
                    # 设置数据库编号
                    if use_prefix:
                        self._db = int(suffix)
                    else:
                        self.db = int(suffix)
                else:
                    # 保存未知后缀
                    logger.warning(f"[地址解析] 警告, 未知结尾, 不处理: {suffix}")
                    if not hasattr(self, "addr_suffix"):
                        self.addr_suffix = suffix

            # 设置端口
            try:
                port_value = int(port)
                if use_prefix:
                    self._port = port_value
                else:
                    self.port = port_value
            except ValueError:
                logger.warning(f"[地址解析] 警告, 无效端口号: {port}")


class TestExceptionClass(Base):
    def test_method(self):
        raise ValueError("Test exception")

if __name__ == '__main__':
    print(TestExceptionClass().test_method())