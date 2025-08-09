# -*- coding: utf-8 -*-
"""PyMagic基础类模块.

本模块提供了一个具有内置异常处理、日志记录功能和地址解析功能的基础类。
它作为PyMagic库中其他类的基础。

类:
    Base: 具有异常处理和地址解析功能的基础类
    TestExceptionClass: 用于异常处理演示的测试类

Example:
    Base类的基本用法:
    
    >>> class MyClass(Base):
    ...     def __init__(self, address="localhost:8080"):
    ...         super().__init__(address=address)
    ...     
    ...     def my_method(self):
    ...         return f"Connected to {self.host}:{self.port}"
    >>> 
    >>> obj = MyClass("192.168.1.1:3306")
    >>> result = obj.my_method()

作者: Guyue
许可证: MIT
版权所有 (C) 2024-2025, 古月居.
"""

from threading import RLock
from typing import Any, Optional

from loguru import logger

from pymagic.decorator_utils import Decorate
from pymagic.tools_utils import Tools

class Base:
    """提供异常处理、日志记录和地址解析功能的基础类.
    
    此类作为其他类的基础，自动为方法添加异常处理装饰器，
    并为Redis、FTP等各种连接格式提供地址解析功能。
    
    该类支持上下文管理器协议，可以与'with'语句一起使用
    进行自动资源清理。
    
    属性:
        logger: 来自loguru的全局日志记录器实例.
        LOCK: 用于线程安全操作的线程锁.
    
    Example:
        带地址解析的基本用法:
        
        >>> class DatabaseConnection(Base):
        ...     def __init__(self, address="localhost:5432"):
        ...         super().__init__(address=address)
        ...     
        ...     def connect(self):
        ...         return f"Connecting to {self.host}:{self.port}"
        >>> 
        >>> db = DatabaseConnection("user:pass@192.168.1.1:5432")
        >>> print(f"Host: {db.host}, User: {db.user}")
        
        用作上下文管理器:
        
        >>> with DatabaseConnection() as db:
        ...     result = db.connect()
    """
    logger = logger
    LOCK: RLock = RLock()

    def __init__(self, address: Optional[str] = None, **kwargs: Any) -> None:
        """使用可选的地址解析初始化Base类.
        
        Args:
            address: 各种格式的连接地址.
                支持的格式包括:
                - "host:port" (例如: "localhost:8080")
                - "user:pass@host:port" (例如: "admin:secret@192.168.1.1:3306")
                - "protocol://user:pass@host:port/path" (例如: "redis://user:pass@localhost:6379/0")
            **kwargs: 用于未来扩展的额外关键字参数.
        
        注意:
            如果提供了address，它将被解析并设置以下属性:
            host, port, user, password, protocol, path.
        """
        # 自动解析连接地址，如：Redis、FTP地址等
        if kwargs.get("_parse_addr", True):
            self._parse_address(address)

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
        """进入上下文管理器的运行时上下文.
        
        Returns:
            实例本身，用于with语句中.
        """
        return self

    @logger.catch()
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出运行时上下文并清理资源.
        
        此方法在退出上下文管理器时被调用，
        如果存在close()方法，会自动调用它。
        
        Args:
            exc_type: 异常类型，如果没有异常发生则为None.
            exc_val: 异常值，如果没有异常发生则为None.
            exc_tb: 异常回溯，如果没有异常发生则为None.
        """
        if hasattr(self, "close"):
            getattr(self, "close")()

    @property
    def Tools(self) -> type:
        """获取Tools工具类的访问权限.
        
        Returns:
            包含各种实用函数的Tools类，
            用于字符串处理、系统检测、文件操作等.
        """
        return Tools

    @property
    def Decorate(self) -> type:
        """获取Decorate装饰器工具类的访问权限.
        
        Returns:
            包含各种有用装饰器的Decorate类，
            用于异常处理、计时、线程安全等.
        """
        return Decorate

    def close(self) -> None:
        """关闭资源并执行清理操作.
        
        此方法在退出上下文管理器时自动调用。
        子类应该重写此方法以实现特定的资源清理逻辑。
        
        注意:
            这是一个空操作实现。子类应该重写此方法
            以提供实际的清理功能。
        """
        pass

    def _parse_address(self, address: Optional[str] = None) -> None:
        """解析支持多种格式的连接地址字符串.
        
        此方法解析各种连接地址格式，并在对象实例上
        设置相应的属性。
        
        支持的格式:
            - 简单格式: "host:port" (例如: "192.168.1.181:21")
            - 带认证: "user:password@host:port" (例如: "user:pass@192.168.1.181:21")
            - Redis格式: "host:port:db" 或 "user:password@host:port:db"
            - FTP路径: "host:port/path" 或 "user:password@host:port/path"
        
        解析的组件将设置为对象属性:
            - host/port: 主机名和端口号
            - user/password: 用户名和密码(如果提供)
            - db: 数据库编号(用于Redis格式)
            - addr_suffix: 其他后缀信息
        
        Args:
            address: 要解析的地址字符串。如果为None，尝试从
                对象的_address或address属性获取。
        
        注意:
            属性可能带有下划线(_)前缀，这取决于对象是否
            已经定义了_host属性。
        """
        # If no address provided, try to get from object attributes
        if not address:
            if hasattr(self, "_address"):
                address = getattr(self, "_address")
            elif hasattr(self, "address"):
                address = getattr(self, "address")

        # Validate address format
        if not address or not isinstance(address, str) or ":" not in address:
            return

        # Check if attributes use underscore prefix (e.g., _host instead of host)
        use_prefix = hasattr(self, "_host")

        # Parse address components: host, port, user, password and possible db
        logger.debug(f"Parsing address: {address}")

        # Handle username and password part
        if "@" in address:
            # Format: user:password@host:port
            host_part = address.rsplit("@", maxsplit=1)[1]  # host:port part
            user_part = address.rsplit("@", maxsplit=1)[0]  # user:password part

            # Set hostname
            host = host_part.split(":")[0]
            port = host_part.split(":", 1)[1] if ":" in host_part else ""

            # Set username and password (password may contain : so split only at first :)
            user = user_part.split(":", maxsplit=1)[0]
            password = user_part.split(":", maxsplit=1)[1] if ":" in user_part else ""

            # Set values according to attribute naming convention
            if use_prefix:
                self._host = host
                self._user = user
                self._password = password
            else:
                self.host = host
                self.user = user
                self.password = password
        else:
            # Format: host:port
            host = address.split(":")[0]
            port = address.split(":", 1)[1] if ":" in address else ""

            # Set values according to attribute naming convention
            if use_prefix:
                self._host = host
            else:
                self.host = host
        # Handle port and possible additional information (like Redis db or FTP path)
        if port:
            # Check if port contains additional information
            if ":" in port or "/" in port:
                separator = ":" if ":" in port else "/"
                suffix = port.rsplit(separator, 1)[1]
                port = port.split(separator, 1)[0]

                # Handle FTP path, add leading slash
                if separator == "/":
                    suffix = "/" + suffix

                # Handle Redis database number or other suffix
                if suffix.isdigit() and (hasattr(self, "_db") or hasattr(self, "db")):
                    # Set database number
                    if use_prefix:
                        self._db = int(suffix)
                    else:
                        self.db = int(suffix)
                else:
                    # Save unknown suffix
                    logger.warning(f"[Address parsing] Warning, unknown suffix, not handled: {suffix}")
                    if not hasattr(self, "addr_suffix"):
                        self.addr_suffix = suffix

            # Set port
            try:
                port_value = int(port)
                if use_prefix:
                    self._port = port_value
                else:
                    self.port = port_value
            except ValueError:
                logger.warning(f"[Address parsing] Warning, invalid port number: {port}")


class TestExceptionClass(Base):
    """用于演示异常处理功能的测试类.
    
    此类继承自Base，用于测试Base类提供的
    自动异常处理功能。
    
    Example:
        >>> test_obj = TestExceptionClass()
        >>> result = test_obj.test_method()  # 由于异常返回False
    """
    
    def test_method(self) -> Any:
        """引发异常的测试方法.
        
        此方法故意引发ValueError异常，以演示
        Base类提供的自动异常处理功能。
        
        Returns:
            由于异常处理装饰器应该返回False.
            
        抛出:
            ValueError: 总是为测试目的抛出此异常.
        """
        raise ValueError("Test exception")


if __name__ == '__main__':
    # Demonstrate exception handling
    test_instance = TestExceptionClass()
    result = test_instance.test_method()
    print(f"Test result: {result}")  # Should print: Test result: False