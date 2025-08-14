# coding: utf-8
"""常用工具函数模块.

常用工具函数模块，提供各种实用功能，封装常用方法，尽量不涉及复杂逻辑，仅提供基础功能支持。

Author: Guyue
License: MIT
Copyright (C) 2024-2025, Guyue.
"""

import os
import random
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse

# Third party imports
from loguru import logger

# Local imports
from .decorator_utils import Decorate

# 系统类型，windows or linux
g_system_type: str = ""
# 是否为windows系统
g_flag_windows: bool = False


class Tools:
    """常用工具方法类.
    
    封装类型划分如下（可通过下列编号搜索代码分布）：
    一、一些简单判断或功能：如 类型、空值判断等
    二、一些处理：字符串替換等
    三、时间和数字相关，时间、休眠方法（定时整数、随机整数、随机浮点数等休眠）
    四、Json转换：json格式、字符串互转等
    五、文档操作：读取写入、读为json、读为列表、删除等
    六、目录（文件）操作：创建、删除、获取文件大小等
    七、一些特殊功能: python语法相关，如获取类属性、类函数等
    八、一些调用，如执行cmd、linux命令、加载配置等
    九、http及网络爬虫相关，如：指纹验证(ja3)
    """

    """ 一、一些简单判断 或其它功能 """

    @staticmethod
    def is_contain_zh(val: Iterable[str]) -> bool:
        """判断字符串中是否包含中文.
        
        Args:
            val: 需要检测的字符串.
            
        Returns:
            包含返回True，不包含返回False.
        """
        for ch in val:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    @staticmethod
    def is_zh(val: Iterable[str]) -> bool:
        """检查整个字符串是否均为中文.
        
        Args:
            val: 需要检查的字符串.
            
        Returns:
            如果全部为中文返回True，否则返回False.
        """
        for ch in val:
            if ch < '\u4e00' or ch > '\u9fff':
                return False
        return True

    @staticmethod
    def is_en(val: Iterable[str]) -> bool:
        """检查整个字符串是否均为英文字母.
        
        Args:
            val: 需要检查的字符串.
            
        Returns:
            如果全部为英文字母返回True，否则返回False.
        """
        import string
        for char in val:
            if char not in string.ascii_letters:
                return False
        return True

    @staticmethod
    def get_system_type() -> str:
        """获取操作系统类型.
        
        Returns:
            操作系统类型字符串.
        """
        import platform
        # 获取平台类型
        return platform.system()

    @classmethod
    def check_system_win(cls) -> Tuple[bool, str]:
        """检查当前系统是否为Windows.
        
        Returns:
            (是否为Windows系统的布尔值, 系统类型字符串).
        """
        global g_flag_windows
        global g_system_type

        if g_system_type:
            return g_flag_windows, g_system_type

        # 获取系统类型
        sys_str = cls.get_system_type()
        g_system_type = sys_str

        flag_windows = sys_str == "Windows"
        g_flag_windows = flag_windows
        
        logger.debug(f"[系统] 当前运行环境：{sys_str}系统，路径：{os.getcwd()}")

        return flag_windows, sys_str

    @classmethod
    def is_windows(cls) -> bool:
        """是否为Windows系统.
        
        Returns:
            如果是Windows系统返回True，否则返回False.
        """
        return cls.get_system_type() == "Windows"

    @classmethod
    def is_linux(cls) -> bool:
        """是否为Linux系统.
        
        Returns:
            如果是Linux系统返回True，否则返回False.
        """
        return cls.get_system_type() == "Linux"

    @staticmethod
    def get_disk_space(path: str = ".", unit: str = 'MB', flag_json: bool = False) -> Union[Dict[str, float], Tuple[Optional[float], Optional[float], Optional[float]], None]:
        """获取指定路径的磁盘大小和剩余空间.
        
        Args:
            path: 路径.
            unit: 单位, bytes/MB/GB.
            flag_json: 字典格式返回结果.
            
        Returns:
            如果flag_json为True，返回包含total、free、used的字典；
            否则返回(总空间, 剩余空间, 已用空间)的元组.
        """
        # 定位到绝对路径
        if path and not path.startswith("/"):
            path = os.path.abspath(path)
            if os.path.isfile(path):
                path = os.path.dirname(os.path.abspath(path))
        try:
            import shutil
            # 获取磁盘信息
            disk_info = shutil.disk_usage(path)
            total_space = float(disk_info.total)
            free_space = float(disk_info.free)
            used_space = float(disk_info.used)

            if unit.lower() in ('mb', 'm'):
                total_space /= (1024 ** 2)
                free_space /= (1024 ** 2)
                used_space /= (1024 ** 2)
            elif unit.lower() in ('gb', 'g'):
                total_space /= (1024 ** 3)
                free_space /= (1024 ** 3)
                used_space /= (1024 ** 3)

            if flag_json:
                return {
                    'total': total_space,
                    'free': free_space,
                    'used': used_space
                }
            return total_space, free_space, used_space
        except Exception as e:
            logger.warning(e)
        if flag_json:
            return None
        return None, None, None

    @classmethod
    def check_disk_space(cls, path: str = ".",
                         size: Union[int, float] = 100,
                         unit: str = "MB") -> Optional[bool]:
        """检测磁盘空间是否足够.
        
        Args:
            path: 路径.
            size: 大小.
            unit: 单位, bytes/MB/GB.
            
        Returns:
            如果空间足够返回True，不足返回False，检测失败返回None.
        """
        _, free, _ = cls.get_disk_space(path, unit=unit, flag_json=False)
        if free is None:
            return None
        return free >= size

    @staticmethod
    def list_random_shuffle(list_target: List[Any]) -> List[Any]:
        """打乱列表顺序，生成新列表.
        
        Args:
            list_target: 需混淆的列表.
            
        Returns:
            打乱顺序后的列表.
        """
        random.shuffle(list_target)
        return list_target

    @staticmethod
    def check_empty(*args: Any) -> bool:
        """判断一个或多个变量值是否存在空值.
        
        Args:
            *args: 需要判断的值.
            
        Returns:
            如果存在空值返回True，否则返回False.
        """
        for name in args:
            if name is None:
                logger.warning(f"警告, 变量为空值: {str(args)}")
                return True
            elif isinstance(name, str) and name.strip() == "":
                logger.warning(f"警告, 变量为空值: {str(args)}")
                return True
            elif not name:
                logger.warning(f"警告, 变量为空值: {str(args)}")
                return True
        return False

    @staticmethod
    def check_type_one(name: Any, *args: type) -> bool:
        """判断是否为想要的类型, 匹配一种即符合.
        
        Args:
            name: 需要判断类型的变量.
            *args: 需要判断的类型.
            
        Returns:
            如果匹配任一类型返回True，否则返回False.
        """
        if name is None:
            return False
        
        name_type = type(name)
        for target_type in args:
            if name_type is target_type:
                return True
        return False

    @staticmethod
    def check_type_all(name: Any, *args: type) -> bool:
        """判断是否为想要的类型, 全部匹配才符合.
        
        Args:
            name: 需要判断类型的变量.
            *args: 传入的类型参数.
            
        Returns:
            如果匹配所有类型返回True，否则返回False.
        """
        if name is None or not args:
            return False
            
        name_type = type(name)
        for target_type in args:
            if name_type is not target_type:
                return False
        return True

    @staticmethod
    def check_str_one(value: str, *args: str) -> bool:
        """判断字符串内是否含有所需值，包含一个即可.
        
        Args:
            value: 需检查的字符串.
            *args: 需要判断的参数.
            
        Returns:
            如果包含任一值返回True，否则返回False.
        """
        if not isinstance(value, str):
            return False
        
        for target in args:
            if target in value:
                return True
        return False

    @staticmethod
    def check_str_all(value: str, *args: str) -> bool:
        """判断字符串内是否含有所需值，包含所有参数.
        
        Args:
            value: 需检查的字符串.
            *args: 需要判断的参数.
            
        Returns:
            如果包含所有值返回True，否则返回False.
        """
        if not isinstance(value, str):
            return False
            
        for target in args:
            if target not in value:
                return False
        return True

    @staticmethod
    def contain_all(value: str, *args: str) -> bool:
        """判断字符串内是否包含所有值.
        
        Args:
            value: 需检查的字符串.
            *args: 需要判断的参数.
            
        Returns:
            如果包含所有值返回True，否则返回False.
        """
        return all(target in value for target in args)

    @staticmethod
    def contain_any(value: str, *args: str) -> bool:
        """判断字符串内是否包含任一值.
        
        Args:
            value: 需检查的字符串.
            *args: 需要判断的参数.
            
        Returns:
            如果包含任一值返回True，否则返回False.
        """
        return any(target in value for target in args)

    """ 二、一些处理"""

    @staticmethod
    def deal_jsonstr(value: str) -> Optional[str]:
        """处理JSON字符串格式.
        
        将Python格式的字符串转换为标准JSON格式。
        
        Args:
            value: 需要处理的字符串.
            
        Returns:
            处理后的JSON格式字符串，如果输入为空则返回原值.
        """
        if value and ("True" in value or "False" in value or "'" in value):
            # 字符串特殊处理
            return value.replace("'", "\"").replace("True", "true") \
                .replace("False", "false") \
                .replace("None", "null")
        return value

    """ 三、时间和数字相关，时间、休眠方法（定时整数、随机整数、随机浮点数等休眠）"""

    @staticmethod
    def format_time(timestamp: Union[float, int], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """转换时间(日期)格式.
        
        Args:
            timestamp: 时间戳.
            fmt: 时间格式字符串.
            
        Returns:
            格式化后的时间字符串.
        """
        return time.strftime(fmt, time.localtime(timestamp))

    @staticmethod
    @Decorate.catch(None)
    def to_timestamp(time_str: str, fmt: Optional[str] = None) -> Optional[int]:
        """时间字符串转时间戳，单位：秒.
        
        Args:
            time_str: 时间字符串.
            fmt: 时间格式字符串，如果为None则使用第三方库解析.
            
        Returns:
            时间戳（秒），转换失败返回None.
        """
        if not fmt:
            return Tools.to_timestamp_other(time_str)
        # "2011-09-28 10:00:00"转化为时间戳
        # time.mktime(time.strptime("2011-09-28 10:00:00", '%Y-%m-%d %H:%M:%S'))
        try:
            return int(time.mktime(time.strptime(time_str.strip(), fmt)))
        except Exception:
            return Tools.to_timestamp_datetime(time_str.strip(), fmt)

    @staticmethod
    @Decorate.catch(None)
    def to_timestamp_datetime(time_str: str, fmt: Optional[str] = None) -> Optional[int]:
        """使用datetime模块将时间字符串转时间戳，单位：秒.
        
        Args:
            time_str: 时间字符串.
            fmt: 时间格式字符串.
            
        Returns:
            时间戳（秒），转换失败返回None.
        """
        import datetime
        # 将时间字符串转换为datetime对象
        obj = datetime.datetime.strptime(time_str, fmt)

        # 将datetime对象转换为时间戳
        return int(obj.timestamp())

    @staticmethod
    @Decorate.catch(0)
    def to_timestamp_other(time_str: str) -> int:
        """使用第三方库pendulum将时间字符串转时间戳，单位：秒.
        
        Args:
            time_str: 时间字符串.
            
        Returns:
            时间戳（秒），转换失败返回0.
        """
        try:
            from pendulum import parse
        except ImportError:
            cmd = "python3 -m pip install pendulum"
            logger.warning("not found library pendulum, default install...: %s" % cmd)
            # 安装
            Tools.execute_command(cmd)
            Tools.sleep(3)
        # pip install pendulum == 2.1.2
        from pendulum import parse
        return int(parse(time_str).timestamp())

    @staticmethod
    def get_timestamp() -> int:
        """获取当前时间戳，单位：秒.
        
        Returns:
            当前时间戳（秒）.
        """
        return int(time.time())

    @staticmethod
    def get_timestamp_float() -> float:
        """获取当前时间戳，单位：秒（浮点数）.
        
        Returns:
            当前时间戳（秒，浮点数）.
        """
        return time.time()

    @staticmethod
    def get_timestamp_ms() -> int:
        """获取当前时间戳，单位：毫秒.
        
        Returns:
            当前时间戳（毫秒）.
        """
        return int(time.time() * 1000)

    @staticmethod
    def get_timestamp_us() -> int:
        """获取当前时间戳，单位：微秒.
        
        Returns:
            当前时间戳（微秒）.
        """
        return int(time.time() * 1000000)

    @staticmethod
    def get_timelock() -> float:
        """
        获取当前精确时间，计算时间使用，如装饰器中的函数运行时间
        
        Returns:
            float: 当前时间的高精度计时器值
            
        Note:
            使用time.perf_counter()替代已弃用的time.clock()
        """
        return time.perf_counter()

    @staticmethod
    def get_nowdate(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前系统日期，精确到秒.
        
        Args:
            fmt: 时间格式字符串.
            
        Returns:
            格式化的当前日期时间字符串.
        """
        return time.strftime(fmt, time.localtime())

    @staticmethod
    def get_nowdate_ms(fmt: str = "%Y-%m-%d %H:%M:%S.%f") -> str:
        """获取当前系统日期，精确到毫秒.
        
        Args:
            fmt: 时间格式字符串.
            
        Returns:
            格式化的当前日期时间字符串（毫秒精度）.
        """
        import datetime
        return datetime.datetime.now().strftime(fmt)[:-3]

    @staticmethod
    def get_nowdate_us(fmt: str = "%Y-%m-%d %H:%M:%S.%f") -> str:
        """获取当前系统日期，精确到微秒.
        
        Args:
            fmt: 时间格式字符串.
            
        Returns:
            格式化的当前日期时间字符串（微秒精度）.
        """
        import datetime
        return datetime.datetime.now().strftime(fmt)

    @staticmethod
    def get_nowdate_number(fmt: str = "%Y%m%d%H%M%S") -> str:
        """获取当前系统日期，纯数字格式，精确到秒.
        
        Args:
            fmt: 时间格式字符串.
            
        Returns:
            纯数字格式的当前日期时间字符串.
            
        注意:
            精确到毫秒可使用格式 %Y%m%d%H%M%S%f.
        """
        return Tools.get_nowdate(fmt=fmt)

    @staticmethod
    def get_localtime_tuple(timestamp: Optional[int] = None) -> time.struct_time:
        """获取时间各单位的元组.
        
        Args:
            timestamp: 时间戳（单位秒），默认使用当前时间.
            
        Returns:
            时间结构体，包含(year, mon, day, hour, min, sec, weekday, jday, isdst).
        """
        return time.localtime(timestamp)

    @staticmethod
    def get_date_tuple(timestamp: Optional[int] = None) -> Tuple[int, int, int, int, int, int, int, int, int]:
        """获取时间各单位的元组（星期已调整）.
        
        Args:
            timestamp: 时间戳（单位秒），默认使用当前时间.
            
        Returns:
            时间元组(year, mon, day, hour, min, sec, weekday, jday, isdst)，
            其中weekday已调整为1-7（1代表星期一）.
        """
        # 日期参数格式化（年月日时分秒）
        year, mon, day, hour, min, sec, weekday, jday, isdst = Tools.get_localtime_tuple(timestamp)
        # 星期需+1（星期 – 取值区间为[0,6]，其中0代表星期一，1代表星期二）
        return year, mon, day, hour, min, sec, weekday + 1, jday, isdst

    @classmethod
    def get_now_year(cls) -> int:
        """获取当前年份.
        
        Returns:
            当前年份.
        """
        return cls.get_localtime_tuple()[0]

    @classmethod
    def get_now_month(cls) -> int:
        """获取当前月份.
        
        Returns:
            当前月份，取值区间为[1,12].
        """
        return cls.get_localtime_tuple()[1]

    @classmethod
    def get_now_day(cls) -> int:
        """获取当前日期.
        
        Returns:
            一个月中的日期，取值区间为[1,31].
        """
        return cls.get_localtime_tuple()[2]

    @classmethod
    def get_now_hour(cls) -> int:
        """获取当前小时.
        
        Returns:
            当前小时，取值区间为[0,23].
        """
        return cls.get_localtime_tuple()[3]

    @classmethod
    def get_now_minute(cls) -> int:
        """获取当前分钟.
        
        Returns:
            当前分钟，取值区间为[0,59].
        """
        return cls.get_localtime_tuple()[4]

    @classmethod
    def get_now_second(cls) -> int:
        """获取当前秒数.
        
        Returns:
            当前秒数，取值区间为[0,59].
        """
        return cls.get_localtime_tuple()[5]

    @classmethod
    def get_now_week(cls) -> int:
        """获取当前星期.
        
        Returns:
            星期，取值区间为[0,6]，其中0代表星期一，1代表星期二，以此类推.
        """
        return cls.get_localtime_tuple()[6]

    @classmethod
    def get_now_yday(cls) -> int:
        """获取今年的第几天.
        
        Returns:
            从每年的1月1日开始的天数，取值区间为[1,366].
        """
        return cls.get_localtime_tuple()[7]

    @classmethod
    def get_now_isdst(cls) -> int:
        """获取夏令时标识符.
        
        Returns:
            夏令时标识符，实行夏令时时为正数，不实行时为0，不了解情况时为负数.
        """
        return cls.get_localtime_tuple()[8]

    @staticmethod
    def sleep(seconds: float, max_seconds: Optional[float] = None) -> None:
        """定时休眠.
        
        Args:
            seconds: 休眠秒数.
            max_seconds: 最大休眠时间，如果指定则调用随机休眠.
        """
        if max_seconds:
            # 随机休眠
            Tools.sleep_random(seconds, max_seconds)
        else:
            time.sleep(seconds)

    @staticmethod
    def sleep_random_int(int_start: int = 1, int_end: int = 5) -> None:
        """随机休眠，单位：整秒.
        
        Args:
            int_start: 最小休眠秒数.
            int_end: 最大休眠秒数.
        """
        if int_start > int_end:
            int_end = int_start + 1
        # randint(a, b)， 随机生成整数：[a-b]区间的整数（包含两端）
        Tools.sleep(random.randint(int_start, int_end))

    @staticmethod
    def sleep_random(float_start: float = 1.8, float_end: float = 5.0) -> None:
        """随机休眠，单位：秒，浮点数.
        
        Args:
            float_start: 最小休眠秒数.
            float_end: 最大休眠秒数.
        """
        if float_start > float_end:
            float_end = float_start + 0.1
        # uniform(a, b)  产生: [a-b]区间的随机浮点数，区间可以不是整数
        Tools.sleep(random.uniform(float_start, float_end))

    """ 四、Json转换 """

    @staticmethod
    @Decorate.catch(None)
    def to_json(obj: Union[str, dict], encoding: str = "utf-8") -> Optional[dict]:
        """对象转JSON字典.
        
        Args:
            obj: 需转为JSON的目标对象.
            encoding: JSON解码格式.
            
        Returns:
            解析后的字典对象，失败返回None.
        """
        if not Tools.check_empty(obj):
            try:
                import json
                return json.loads(obj, encoding=encoding)
            except ValueError as e:
                logger.warning(e)
                if Tools.check_type_one(obj, str):
                    obj = Tools.deal_jsonstr(obj)
                    import json
                    return json.loads(obj, encoding=encoding)
        return None

    @staticmethod
    @Decorate.catch(None)
    def to_jsonstr(obj: Union[str, dict, list, tuple]) -> Optional[str]:
        """对象转JSON字符串.
        
        主要针对字典、列表等对象的JSON序列化。
        
        Args:
            obj: 需转为JSON字符串的目标对象.
            
        Returns:
            JSON格式字符串，失败返回None.
            
        注意:
            字符串会进行特殊处理以确保JSON格式正确.
        """
        # 可迭代对象或不为空
        if isinstance(obj, Iterable) or not Tools.check_empty(obj):
            if isinstance(obj, str):
                # 字符串特殊处理
                return Tools.deal_jsonstr(obj)
            else:
                import json
                # 避免中文乱码
                return json.dumps(obj, ensure_ascii=False)
        return None

    """ 五、文档操作 """

    @staticmethod
    def write(filename: str, data: Union[bytes, str, list], mode: str = 'w',
              encoding: str = 'utf-8', flag_mkdir: bool = True) -> bool:
        """写入文件.
        
        Args:
            filename: 文件路径.
            data: 需写入的数据.
            mode: 文件操作模式，常见 w、w+、a、a+.
            encoding: 文件编码格式.
            flag_mkdir: 是否需要创建目录.
            
        Returns:
            写入成功返回True，失败返回False.
        """
        if flag_mkdir is True:
            Tools.makedirs(filename, flag_file=True)
        if "b" in mode:
            # 二进制文件不支持utf-8模式打开，会抛出异常
            encoding = None
        try:
            with open(filename, mode=mode, encoding=encoding) as f:
                # 列表使用writelines写入
                if isinstance(data, list):
                    f.writelines(data)
                else:
                    f.write(data)
            return True
        except Exception as e:
            logger.error("fail, write file of mode %s... %s: %s" % (mode, filename, e))
        return False

    @staticmethod
    def write_str(filename: str, data: Any, mode: str = 'w', encoding: str = 'utf-8') -> bool:
        """写入字符串到文件.
        
        Args:
            filename: 文件路径.
            data: 需写入的数据.
            mode: 写入模式.
            encoding: 文件编码格式.
            
        Returns:
            写入成功返回True，失败返回False.
        """
        if not isinstance(data, str):
            data = str(data)
        return Tools.write(filename, data, mode=mode, encoding=encoding)

    @staticmethod
    def write_str_list(filename: str, datas: Union[List[Any], set], end: str = '\n', mode: str = 'w',
                       encoding: str = 'utf-8') -> bool:
        """写入字符串列表到文件.
        
        Args:
            filename: 文件路径.
            datas: 需写入的数据列表.
            end: 行结尾字符，默认换行.
            mode: 写入模式.
            encoding: 文件编码格式.
            
        Returns:
            写入成功返回True，失败返回False.
        """
        return Tools.write(filename, [str(i) + end for i in datas], mode=mode, encoding=encoding)

    @staticmethod
    def write_json(filename: str, data: Union[dict, str, list, Any],
                   mode: str = 'w', encoding: str = 'utf-8') -> bool:
        """以JSON格式写入文件.
        
        Args:
            filename: 文件路径.
            data: 需写入的数据.
            mode: 写入模式.
            encoding: 文件编码格式.
            
        Returns:
            写入成功返回True，失败返回False.
        """
        # 非空路径
        if not Tools.check_empty(filename):
            data = Tools.to_jsonstr(data)
            Tools.makedirs(filename, flag_file=True)
            return Tools.write(filename, data, mode=mode, encoding=encoding)
        return False

    @staticmethod
    def write_json_list(filename: str, datas: List[dict or str], end: str = '\n', mode: str = 'w',
                        encoding: str = 'utf-8') -> bool:
        """清空或创建文件，以JSON格式写入数据列表。
        
        Args:
            filename: 文件路径
            datas: 需写入的数据列表
            end: 结尾字符，默认换行
            mode: 写入模式
            encoding: 文件编码格式
            
        Returns:
            写入成功返回True，否则返回False
        """
        # 非空路径
        if not Tools.check_empty(filename):
            Tools.makedirs(filename, flag_file=True)
            return Tools.write(filename, [Tools.to_jsonstr(i) + end if isinstance(i, dict) else
                                          str(i) + end for i in datas], mode=mode,
                               encoding=encoding)
        return False

    @staticmethod
    def save_str(filename: str, data: object, end: str = '\n', mode: str = 'a',
                 encoding: str = 'utf-8') -> bool:
        """字符串保存，默认换行。
        
        Args:
            filename: 文件路径
            data: 需写入的数据
            end: 结尾字符，默认换行
            mode: 写入模式
            encoding: 文件编码格式
            
        Returns:
            写入成功返回True，否则返回False
        """
        # if type(data) is not str:
        #     data = str(data)
        return Tools.write(filename, "%s%s" % (data, end), mode=mode, encoding=encoding)

    @staticmethod
    def save_str_list(filename: str, datas: Union[List[Any], set], end: str = '\n', mode: str = 'a',
                      encoding: str = 'utf-8') -> bool:
        """保存字符串列表，默认换行。
        
        Args:
            filename: 文件路径
            datas: 需写入的数据列表或集合
            end: 结尾字符，默认换行
            mode: 写入模式
            encoding: 文件编码格式
            
        Returns:
            写入成功返回True，否则返回False
        """
        return Tools.write(filename, [str(i) + end for i in datas],
                           mode=mode, encoding=encoding)

    @staticmethod
    def save_json(filename: str, data: Union[dict, str], end: str = '\n',
                  mode: str = 'a', encoding: str = 'utf-8') -> bool:
        """JSON格式保存，默认换行。
        
        Args:
            filename: 文件路径
            data: 需写入的数据
            end: 结尾字符，默认换行
            mode: 写入模式
            encoding: 文件编码格式
            
        Returns:
            写入成功返回True，否则返回False
        """
        if Tools.check_type_one(data, dict, str):
            data = Tools.to_jsonstr(data)
        return Tools.write(filename, "%s%s" % (data, end), mode=mode, encoding=encoding)

    @staticmethod
    def save_json_list(filename: str, datas: List[dict or str], end: str = '\n', mode: str = 'a',
                       encoding: str = 'utf-8') -> bool:
        """JSON格式保存列表，默认换行。
        
        Args:
            filename: 文件路径
            datas: 需写入的数据列表
            end: 结尾字符，默认换行
            mode: 写入模式
            encoding: 文件编码格式
            
        Returns:
            写入成功返回True，否则返回False
        """
        return Tools.write(filename, [Tools.to_jsonstr(i) + end
                                      if isinstance(i, dict) else str(i) + end
                                      for i in datas],
                           mode=mode, encoding=encoding)

    '''
    读取文件操作
        read([size])方法从文件当前位置起读取size个字节，若无参数size，则表示读取至文件结束为止，它返回为字符串对象。

        readline是默认一行一行的读dao取，每读取一行，指针就放在这一行的“\n”换行符结尾位置，再次读取则从这一行结尾处到下一行的换行符位置。返回的是一个列表对象。
        即该方法每次读出一行内容，所以，读取时占用内存小，比较适合大文件，该方法返回一个字符串对象。

        readlines()方法读取整个文件所有行，保存在一个列表(list)变量中，每行作为一个元素，但读取大文件会比较占内存。
    '''

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch(None)
    def read(filename: str, size: int = -1, mode: str = 'r', encoding: str = 'utf-8') \
            -> Union[str, None]:
        """读取整个文件。
        
        read([size])方法从文件当前位置起读取size个字节，若无参数size，则表示读取至文件结束为止，它返回为字符串对象。
        
        Args:
            filename: 文件路径
            size: 读取大小，默认读取所有
            mode: 操作模式
            encoding: 文件打开编码
            
        Returns:
            文件内容字符串，读取失败返回None
        """
        # 二进制不设置格式
        if "b" in mode:
            encoding = None
        # errors = "ignore"  # ignore 忽略错误
        with open(filename, mode=mode, encoding=encoding) as f:
            return f.read(size)

    @staticmethod
    def read_list(filename: str, mode: str = 'r', encoding: str = 'utf-8') -> List[str]:
        """默认读取列表方法，按行读取。
        
        Args:
            filename: 文件路径
            mode: 操作模式
            encoding: 文件打开编码
            
        Returns:
            文件内容列表
        """
        return Tools.read_list_line(filename, mode=mode, encoding=encoding)

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch(list())
    def read_list_line(filename: str, mode: str = 'r', encoding: str = 'utf-8') -> List[str]:
        """推荐：一行行读取，节省内存。
        
        Args:
            filename: 文件路径
            mode: 操作模式
            encoding: 文件打开编码
            
        Returns:
            文件内容列表
        """
        list_tmp = []
        with open(filename, mode=mode, encoding=encoding) as f:
            while True:
                line = f.readline().strip()
                if line == "":
                    break
                if line:
                    list_tmp.append(line)
        return list_tmp

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch(list())
    def read_list_lines(filename: str, mode: str = 'r', encoding: str = 'utf-8') -> List[str]:
        """预选整个文件保存列表。
        
        注意：不太推荐，占内存
        
        Args:
            filename: 文件路径
            mode: 操作模式
            encoding: 文件打开编码
            
        Returns:
            文件内容列表
        """
        list_tmp = []
        with open(filename, mode=mode, encoding=encoding) as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    list_tmp.append(line)
        return list_tmp

    @staticmethod
    def read_json(filename: str, mode: str = 'r', encoding: str = 'utf-8-sig') -> Optional[dict]:
        """读取json文件，返回json。
        
        Args:
            filename: 文件路径
            mode: 操作模式
            encoding: 文件打开编码
            
        Returns:
            JSON数据字典，如果读取失败返回None
        """
        data = Tools.read(filename, mode=mode, encoding=encoding)
        if data:
            return Tools.to_json(data)
        return None

    """ 六、目录（文件）操作：创建、删除、获取文件大小等 """

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch(-1)
    def get_file_size(filename: str) -> int:
        """获取文件大小（字节）。
        
        Args:
            filename: 文件路径
            
        Returns:
            文件大小（字节），失败时返回-1
        """
        return int(os.path.getsize(filename))

    @staticmethod
    @Decorate.catch(-1)
    def get_file_mtime(filename: str) -> float:
        """获取文件修改时间。
        
        Args:
            filename: 文件路径
            
        Returns:
            文件修改时间戳（例如：1644566050.978794），失败时返回-1
        """
        return os.stat(filename).st_mtime

    @staticmethod
    def exists(path: str) -> bool:
        """
        判断目录或文件是否存在
        
        Args:
            path: 文件或目录路径，可以是string, bytes, os.PathLike或integer类型
            
        Returns:
            bool: 如果路径存在返回True，否则返回False
        """
        if path is not None and os.path.exists(path):
            return True
        logger.warning(f"Path does not exist: {path}")
        return False

    @staticmethod
    def isdir(path: str) -> bool:
        """判断目标是否为目录。
        
        Args:
            path: 路径（string, bytes, os.PathLike or integer）
            
        Returns:
            如果是目录返回True，否则返回False
        """
        if path is not None and os.path.isdir(path):
            return True
        return False

    @staticmethod
    def isfile(file: str) -> bool:
        """判断目标是否为文件。
        
        Args:
            file: 文件路径（string, bytes, os.PathLike or integer）
            
        Returns:
            如果是文件返回True，否则返回False
        """
        if file is not None and os.path.isfile(file):
            return True
        return False

    @staticmethod
    def is_same_file(src: str, dest: str) -> Optional[bool]:
        """判断是否为同一文件。
        
        Args:
            src: 源文件路径
            dest: 目标文件路径
            
        Returns:
            如果是同一文件返回True，不是返回False，无法判断返回None
        """
        if Tools.isfile(src) and Tools.isfile(dest):
            return Tools.encode_md5_file(src) == Tools.encode_md5_file(dest)
        # 未知，无法判断
        return None

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch(list())
    def listdirs(path: str) -> List[str]:
        """遍历返回目录（文件）名列表。
        
        Args:
            path: 目录路径
            
        Returns:
            目录和文件名列表
        """
        return os.listdir(path)

    @classmethod
    @Decorate.catch(list())
    def listdirs_scandir(cls, path_dir: str, mode: int = 0, depth: int = 1) -> List[str]:
        """遍历目标路径。
        
        Args:
            path_dir: 需遍历目标路径
            mode: 模式选择（0：所有，1：文件夹，2：文件）
            depth: 遍历深度（<=-1 则遍历所有）
            
        Returns:
            符合条件的路径列表
        """
        list_dirs: list = list()

        with os.scandir(path_dir) as it:

            # 深度判断
            depth = depth if depth <= 0 else depth - 1
            for entry in it:
                '''提供的属性和方法
                    name: 条目的文件名，相对于 scandir path 参数( 对应于 os.listdir的返回值)
                    path: 输入路径 NAME ( 不一定是绝对路径) --与 os.path.join(scandir_path, entry.name)
                    is_dir(*, follow_symlinks=True): 类似于 pathlib.Path.is_dir()，但返回值在 DirEntry 对象上是缓存；大多数情况下不需要系统调用；如果 follow_symlinks 是 false，则不要跟随符号链接。
                    is_file(*, follow_symlinks=True): 类似于 pathlib.Path.is_file()，但返回值在 DirEntry 对象上是缓存；大多数情况下不需要系统调用；如果 follow_symlinks 是 false，则不要跟随符号链接。
                    is_symlink(): 类似 pathlib.Path.is_symlink()，但返回值缓存在 DirEntry 对象上；大多数情况下不需要系统调用
                    stat(*, follow_symlinks=True): 类似 os.stat()，但返回值缓存在 DirEntry 对象上；不需要对 Windows (。除了符号符号外) 进行系统调用；如果 follow_symlinks 是 false，则不跟随符号链接( 像 os.lstat() )。
                    inode(): 返回项的节点数；返回值在 DirEntry 对象上缓存
                '''
                if mode == 0 or mode == 1 and entry.is_dir() or mode == 2 and entry.is_file():
                    # 添加拼接后路径
                    list_dirs.append(cls.join_path(path_dir, entry.name))
                # 是否抵达指定深度
                if depth != 0 and entry.is_dir():
                    # 深度判断
                    # depth_tmp = depth if depth <= -1 else depth - 1
                    depth_tmp = depth
                    # 递归调用，添加符合路径
                    list_dirs.extend(cls.listdirs_scandir
                                     (cls.join_path(path_dir, entry.name),
                                      mode=mode,
                                      depth=depth_tmp))
        return list_dirs

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch(list())
    def listdirs_walk(path: str, mode: int = 0, flag_complete: bool = True,
                      flag_tree: bool = False) -> List[str]:
        """推荐：遍历目标目录下的所有目录（或文件或文件夹）列表，可遍历整个目录树。
        
        Args:
            path: 需遍历目标路径
            mode: 模式选择（0：所有，1：文件夹，2：文件）
            flag_complete: 是否返回完整路径
            flag_tree: 是否遍历整个目录树
            
        Returns:
            符合条件的路径列表
        """
        # 绝对路径
        if flag_complete is True:
            # 目标绝对路径，拼接完整目录时使用
            path = os.path.abspath(path)
        list_result = []
        ''' os.walk遍历整个目录树，每次返回三个参数：目标目录、文件夹列表、文件列表
                topdown --可选，为 True，则优先遍历 top 目录，否则优先遍历 top 的子目录(默认为开启)。
                如果 topdown 参数为 True，walk 会遍历top文件夹，与top 文件夹中每一个子目录。
        '''
        # for parent, dirs, files in os.walk(path, topdown=True):
        for parent, dirs, files in os.walk(path):
            # print('parent', parent, dirs)
            list_tmp = []
            # 所有 或 文件夹
            if mode == 0 or mode == 1:
                list_tmp.extend(dirs)
            # 所有 或 文件
            if mode == 0 or mode == 2:
                list_tmp.extend(files)
                # print(files)
            if flag_complete is True:
                # 完整路径
                '''
                    三种拼接方式
                        1. 标准的写法，不生存新列表，而是通过列表索引改列表中的内容
                        for i, k in enumerate(dirs):
                            dirs[i] = k + 1
                        2. 匿名函数lambad
                        result_dir = map(lambda x: os.path.join(parent, x), dirs)
                        或者在map() 前面加个 list() 转化成列表输出
                        3. 列表解析式
                        dirs = [i+1 for i in dirs]
                '''
                list_result.extend([os.path.join(parent, i) for i in list_tmp])
            elif flag_tree is False:
                # 仅遍历当前目录，直接赋值即可
                list_result = list_tmp
            else:
                list_result.extend(list_tmp)
            if flag_tree is True:
                # 遍历整个目录树
                pass
            else:
                # 仅遍历当前目录
                break
        return list_result

    @staticmethod
    def join_path(*args) -> str:
        """拼接路径。
        
        注意：发现os.path.join会对绝对路径去重，导致与预期路径不符
        
        Args:
            *args: 路径组件
            
        Returns:
            拼接后的路径
        """
        path_all = ""
        # 路径分隔符，一般为 /
        sep = os.path.sep
        # 循环拼接
        for i in args:
            i = str(i)
            if i:
                # 已存在分隔符 如 /
                if path_all.endswith(sep) or i.startswith(sep):
                    path_all += i
                elif path_all:
                    # 需添加分隔符
                    path_all = path_all + sep + i
                else:
                    # 直接复制
                    path_all = i
        return path_all

    @classmethod
    def deal_path(cls, data: str, replace: str = "_") -> str:
        """处理（替换）路径中命名中的不规范字符。
        
        Args:
            data: 原始路径字符串
            replace: 替换字符
            
        Returns:
            处理后的路径字符串
        """
        if data and not cls.is_windows():
            # '|', '"', ':', '?', '*', '<', '>'   '\' '/'
            for char in ('|', '"', '：', '?', '*', '<', '>'):
                data = data.replace(char, replace)
        return data

    @staticmethod
    @Decorate.catch()
    def makedir(path: str, flag_file: bool = False) -> bool:
        """创建单层目录，或剔除文件名创建单层目录。
        
        Args:
            path: 目录路径或文件路径
            flag_file: 是否包含文件名（如果为True，会剔除文件名部分）
            
        Returns:
            创建成功返回True
        """
        if flag_file is True:
            # 切割路径和文件名
            path = os.path.split(path)[0]
        
        if not Tools.check_empty(path):
            if Tools.isdir(path):
                print("目录已存在, 无需创建: %s" % path)
            else:
                print("创建单层目录: %s" % path)
                os.mkdir(path)  # 创建单层目录，无返回值
        return True

    @staticmethod
    @Decorate.catch(log_level="warn")
    def makedirs(path: str, flag_file: bool = False) -> bool:
        """递归创建目录，或剔除文件名创建目录。
        
        Args:
            path: 目录路径或文件路径
            flag_file: 是否包含文件路径文件
            
        Returns:
            创建成功返回True
        """
        if flag_file is True:
            # 切割路径和文件名
            path = os.path.split(path)[0]
            if path == "":
                return True

        os.makedirs(path, exist_ok=True)
        return True

    @staticmethod
    def get_file_path(file_name: str) -> Optional[str]:
        """获取文件目录。
        
        Args:
            file_name: 源文件路径
            
        Returns:
            文件所在目录路径，如果输入为空返回None
        """
        if file_name:
            return os.path.split(file_name)[0]
        return None

    @staticmethod
    def get_file_name(file_name: str) -> Optional[str]:
        """获取文件名。
        
        Args:
            file_name: 源文件路径
            
        Returns:
            文件名，如果输入为空返回None
        """
        if file_name:
            return os.path.split(file_name)[-1]
        return None

    @staticmethod
    def get_abspath(path_src: str) -> Optional[str]:
        """获取文件/目录的绝对路径。
        
        Args:
            path_src: 文件/目录路径
            
        Returns:
            绝对路径，如果输入为空返回原值
        """
        if not path_src:
            return path_src
        return os.path.abspath(path_src)

    @classmethod
    def unzip_file(cls, filename: str, unzip_path: Optional[str] = None, file_suffix: Optional[str] = None) -> bool:
        """解压文件。
        
        Args:
            filename: 待解压文件路径
            unzip_path: 指定解压路径，默认为None
            file_suffix: 指定文件后缀类型，默认为None
            
        Returns:
            解压成功返回True，否则返回False
        """
        # 结果
        ret = False
        # 解压命令
        command = ""
        # 文件后缀
        if not file_suffix:
            file_suffix = filename.rsplit(".", 1)[-1]

        # if file_path:
        #     os.chdir(file_path)
        # 解压路径以 / 结尾
        if unzip_path and not unzip_path.endswith("/"):
            unzip_path += "/"
            # 创建解压目录
            if not Tools.isdir(unzip_path):
                Tools.makedirs(unzip_path)

        # 根据后缀匹配命令（解压并默认覆盖）
        if file_suffix == 'zip':
            command = 'unzip -o "%s"' % filename
            if unzip_path:
                command += ' -d "%s"' % unzip_path
        elif file_suffix == 'rar':
            command = 'unrar x "%s"' % filename
            if unzip_path:
                command += ' "%s"' % unzip_path
        elif file_suffix == 'gz':
            command = 'tar -zxvf "%s"' % filename
            if unzip_path:
                command += ' -C "%s"' % unzip_path
        elif file_suffix == '7z':
            # sudo yum install -y epel-release
            # sudo yum install -y p7zip
            # 使用密码 -pxxxx
            command = '7za x -y "%s"' % filename
            if unzip_path:
                # 【注意】：-o 与解压缩的路径之间没用空格
                command += ' -o"%s"' % unzip_path
        elif file_suffix == 'bz2':
            # tar -jxvf xxx.tar.bz2
            command = 'bunzip2 -f "%s"' % filename
            if unzip_path:
                command += ' "%s"' % unzip_path
        elif file_suffix == 'lz4':
            command = 'lz4 -d -f "%s"' % filename
            if unzip_path:
                command += ' "%s"' % unzip_path
        else:
            logger.error("[unzip] Error, not found suffix: %s, %s" % (file_suffix, filename))
            return ret

        # # 切换路径
        # file_path = Tools.get_file_path(filename)
        # # 是否需要切换路径再解压
        # if file_path:
        #     command = 'cd "%s" && %s' % (file_path, command)

        try:
            logger.debug(
                '[unzip] start, unzip is in progress: %s, %s' % (file_suffix, filename))
            print('[unzip] command exec: %s' % command)
            # result = os.system(command)
            # result = Tools.execute_command_popen(command, False)
            ''' 使用管道输出 '''
            # with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) as res:
            # command += " >/dev/null"
            import subprocess
            try:
                res = subprocess.run(command + " >/dev/null", shell=True, capture_output=True)
                result = res.returncode
            except:
                result = os.system(command)
                # res = subprocess.run(command, shell=True)
                # with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) as res:
                #     pass
            # result = res.returncode
            if result == 0 or result in (1, 2) and not cls.is_windows():
                logger.info('[unzip] ok, unzip successfully, ret: %s, [%s] %s'
                            % (result, file_suffix, filename))
                ret = True
            else:
                logger.warning('[unzip] Warn, unzip fail, ret: %s, [%s] %s'
                               % (result, file_suffix, filename))
                # zip压缩文件过大导致无法解压，尝试使用7za解压
                if file_suffix == 'zip':
                    logger.info("[unzip] try, change decompression mode(%s ==>> %s): %s" % (
                        file_suffix, "7z", filename
                    ))
                    file_suffix = "7z"
                    return Tools.unzip_file(filename, unzip_path, file_suffix)
        except BaseException as e:
            logger.error(
                '[unzip] Error, unzip %s! %s: %s' % (file_suffix, filename, e))
        return ret

    ''' 文件的创建时间、修改时间、访问时间
        import os
        from datetime import datetime
        ctime = os.path.getctime("test") #创建时间
        ctime_string = datetime.fromtimestamp(int(ctime))
         
        mtime = os.path.getmtime("test") #修改时间
        mtime_string = datetime.fromtimestamp(int(ctime))
         
        atime = os.path.getatime("test") #访问时间
        atime_string = datetime.fromtimestamp(int(ctime))
    '''

    @staticmethod
    def get_create_time(file: str) -> float:
        """获取文件或目录创建时间。
        
        Args:
            file: 文件或目录路径
            
        Returns:
            创建时间戳
        """
        return os.path.getctime(file)

    @staticmethod
    def get_modify_time(file: str) -> float:
        """获取文件或目录的最后修改时间。
        
        Args:
            file: 文件或目录路径
            
        Returns:
            最后修改时间戳
        """
        return os.path.getmtime(file)

    @staticmethod
    def get_access_time(file: str) -> float:
        """获取文件访问时间。
        
        Args:
            file: 文件路径
            
        Returns:
            最后访问时间戳
        """
        return os.path.getatime(file)

    '''
    删除目录
        os.remove(path)  # path是文件的路径，如果这个路径是一个文件夹，则会抛出OSError的错误，这时需用用rmdir()来删除
        os.rmdir(path)  # path是文件夹路径，注意文件夹需要时空的才能被删除
        os.unlink('F:\新建文本文档.txt')  # unlink的功能和remove一样是删除一个文件，但是删除一个删除一个正在使用的文件会报错。
        
        os.removedirs(path)  # 递归地删除目录。如果子目录成功被删除，则将会成功删除父目录，子目录没成功删除，将抛异常。
        
        另一种方法
        shutil.rmtree()
        shutil算是os模块的高级操作模块，许多操作更直接方便，如删除目录，默认删除内所有文件
    '''

    @staticmethod
    @Decorate.catch()
    def del_file(file: str) -> bool:
        """删除文件。
        
        Args:
            file: 文件路径
            
        Returns:
            删除成功返回True
        """
        if os.path.exists(file):
            os.remove(file)
        return True

    @staticmethod
    def del_dirs(path: str, del_tree: bool = True) -> bool:
        """推荐：删除整个目录（包含文件）。
        
        Args:
            path: 文件夹路径
            del_tree: 是否删除整个目录树
            
        Returns:
            删除成功返回True
        """
        if del_tree:
            return Tools.del_dirs_tree(path)
        # 删除空目录
        return Tools.del_dirs_empty(path)

    @staticmethod
    @Decorate.catch()
    def del_dirs_tree(path: str) -> bool:
        """推荐：强制删除目录树。
        
        Args:
            path: 目录路径
            
        Returns:
            删除成功返回True
        """
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)
        return True

    @staticmethod
    @Decorate.catch()
    def del_dirs_empty(path: str) -> bool:
        """递归删除空目录。
        
        注意：如果子目录成功被删除，则将会成功删除父目录，子目录没成功删除，将抛异常。
        
        Args:
            path: 目录路径
            
        Returns:
            删除成功返回True
        """
        if Tools.exists(path):
            os.removedirs(path)
        return True

    @staticmethod
    @Decorate.catch()
    def del_dirone_empty(path: str) -> bool:
        """删除单个空目录。
        
        Args:
            path: 目录路径
            
        Returns:
            删除成功返回True
        """
        if Tools.exists(path):
            os.rmdir(path)
        return True

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch()
    def rename(name: str, new_name: str) -> bool:
        """重命名文件或目录。
        
        注意：经测试使用shutil模块的移动函数重命名比os模块单纯的移动效率更高
        
        Args:
            name: 源目标路径
            new_name: 新名称路径
            
        Returns:
            重命名成功返回True
        """
        return Tools.move(name, new_name)

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch()
    def rename_os(name: str, new_name: str) -> bool:
        """使用os模块重命名目录（文件夹、文件）。
        
        Args:
            name: 源目标路径
            new_name: 新名称路径
            
        Returns:
            重命名成功返回True，失败返回False
        """
        if Tools.exists(name):
            os.rename(name, new_name)
            return True
        return False

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch()
    def move(name: str, new_name: str, flag_cover: bool = True,
             flag_mk_parent: bool = False) -> bool:
        """移动目录，同时有重命名功能。
        
        Args:
            name: 源目标路径
            new_name: 移动地址
            flag_cover: 是否覆盖（默认True覆盖）
            flag_mk_parent: 是否创建目标路径的父级目录（默认False不创建）
            
        Returns:
            移动成功返回True，失败返回False
        """
        if flag_cover is False:
            if Tools.exists(new_name):
                logger.warning("Warn, target exists and not cover: %s" % new_name)
                return False
        if Tools.exists(name):
            if flag_mk_parent:
                Tools.makedirs(new_name, True)
            import shutil
            shutil.move(name, new_name)
            return True
        logger.warning("Warn, move fail, not found target: %s ==>> %s" % (name, new_name))
        return False

    @staticmethod
    @Decorate.catch()
    def copy_file(source: str, dst: str) -> bool:
        """复制文件。
        
        Args:
            source: 来源文件路径
            dst: 目标文件路径
            
        Returns:
            复制成功返回True，失败返回False
        """
        if Tools.isfile(source):
            # 创建上级目录
            Tools.makedirs(dst, flag_file=True)
            import shutil
            shutil.copy(source, dst)
            return True
        return False

    @staticmethod
    # @Decorate.time_run
    @Decorate.catch()
    def copy_dirtree(path: str, copy_path: str) -> bool:
        """将源目录的内容复制到目标目录。
        
        注意：使用copytree时，需要确保src存在而dst不存在。即使顶层目录不包含任何内容，copytree也不会工作
        
        Args:
            path: 源目录路径
            copy_path: 目标目录路径
            
        Returns:
            复制成功返回True，失败返回False
        """
        if Tools.exists(path):
            import shutil
            if Tools.exists(copy_path):
                shutil.rmtree(copy_path)
            shutil.copytree(path, copy_path)
            return True
        return False

    @staticmethod
    @Decorate.catch()
    def copy_dir(path: str, copy_path: str) -> bool:
        """将源文件的内容复制到目标文件或目录。
        
        注意：使用的前提是必须要有 os.chdir(你要处理的路径)
        
        Args:
            path: 源路径
            copy_path: 目标路径
            
        Returns:
            复制成功返回True，失败返回False
        """
        if Tools.exists(path):
            import shutil
            shutil.copy(path, copy_path)
            return True
        return False

    @classmethod
    # @Decorate.catch()
    def compress_archive(cls, source: str, output_archive: str, fmt: str = "zip") -> bool:
        """压缩指定文件夹中的文件为归档。
        
        Args:
            source: 要压缩的文件夹路径
            output_archive: 输出归档文件的路径
            fmt: 压缩格式，默认为"zip"（可选值包括"zip", "tar", "gztar", "bztar", "xztar"）
            
        Returns:
            压缩成功返回True，失败返回False
        """
        if not cls.exists(source):
            logger.warning("Warn, 未找到目录/文件: %s" % source)
            return False

        from shutil import make_archive
        try:
            make_archive(output_archive, fmt, source)
        except Exception as e:
            logger.exception(f"压缩文件夹失败：{e}")
            return False
        return True

    @classmethod
    def extract_archive(cls, archive: str, output: str) -> bool:
        """解压归档文件到指定文件夹。
        
        Args:
            archive: 归档文件的路径
            output: 解压文件的目标文件夹路径
            
        Returns:
            解压成功返回True，失败返回False
        """
        if not cls.isfile(archive):
            logger.warning("Warn, 未找到文件: %s" % archive)
            return False

        from shutil import unpack_archive
        try:
            unpack_archive(archive, output)
        except Exception as e:
            logger.exception(f"解压文件失败：{e}")
            return False
        return True

    """ 七、一些特殊功能: python语法相关，如获取类属性、类函数等 """

    @staticmethod
    def get_func_name() -> str:
        """获取正在调用此函数(或方法)的名称。
        
        Returns:
            当前函数的名称
        """
        import inspect
        result_name = inspect.stack()[1][3]
        print("当前函数名称: %s" % result_name)
        return result_name

    @staticmethod
    @Decorate.catch(list())
    def get_cls_all(obj) -> List[Tuple[str, Any]]:
        """获取类或实例的所有属性（函数和变量），以下划线开头的特殊函数和变量除外。
        
        Args:
            obj: 类或实例对象
            
        Returns:
            每个元素为元组的列表，(函数名或变量名, 具体函数或变量值)
        """
        return [(name, getattr(obj, name)) for name in dir(obj) if not name.startswith("_")]

    @staticmethod
    def get_cls_fuclist(obj) -> List[Tuple[str, Any]]:
        """获取类或实例的可调用函数。
        
        Args:
            obj: 类或实例对象
            
        Returns:
            每个元素为元组的列表，包含函数名和函数对象
        """
        temp = []
        for name, func in Tools.get_cls_all(obj):
            if callable(func):
                temp.append((name, func))
        return temp

    @staticmethod
    def get_cls_fucdict(obj) -> Dict[str, Any]:
        """获取类或实例的可调用函数。
        
        Args:
            obj: 类或实例对象
            
        Returns:
            包含所有可调用函数的字典
        """
        temp = {}
        for name, func in Tools.get_cls_all(obj):
            # 可调用对象
            if callable(func):
                temp[name] = func
        return temp

    @staticmethod
    def get_cls_attrdict(obj) -> Dict[str, Any]:
        """获取类或实例的属性。
        
        Args:
            obj: 类或实例对象
            
        Returns:
            包含所有非可调用属性的字典
        """
        temp = {}
        for name, func in Tools.get_cls_all(obj):
            # 不可调用对象
            if not callable(func):
                temp[name] = func
        return temp

    """ 八、一些调用，如执行cmd、linux命令、加载配置等
        (命令执行一般使用os、subprocess模块)
    """

    @staticmethod
    @Decorate.catch()
    def execute_paramlist_run(list_params: List[str]) -> bytes:
        """执行系统命令，列表形式参数组装命令，返回输出结果。
        
        例：获取视频时长(调用工具ffprobe)
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            media_time = float(result.stdout)
            
        Args:
            list_params: 参数列表
            
        Returns:
            命令执行的输出结果
        """
        import subprocess
        # 参数stdin, stdout, stderr分别表示程序的标准输入、输出、错误句柄。他们可以是PIPE、文件描述符或文件对象，
        # 也可以设置为None，表示从父进程继承。
        result_sub = subprocess.run(list_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result_sub.stdout

    @staticmethod
    @Decorate.catch()
    def execute_command_system(command: str) -> bool:
        """简单粗暴的执行系统(cmd)命令，返回结果为0表示执行成功, 默认打印控制台内容。
        
        返回命令执行结果的返回值，system()函数在执行过程中进行了以下三步操作：
            1.fork一个子进程；
            2.在子进程中调用exec函数去执行命令；
            3.在父进程中调用wait（阻塞）去等待子进程结束。
            对于fork失败，system()函数返回-1。
            注：有些用户使用该函数经常会莫名其妙地出现错误，但是直接执行命令并没有问题。
            
        更多：使用system执行多条命令
            为了保证system执行多条命令可以成功，多条命令需要在同一个子进程中运行；
            import os
            os.system('cd /usr/local && mkdir aaa.txt')
            # 或者
            os.system('cd /usr/local ; mkdir aaa.txt')
            
        Args:
            command: 要执行的系统命令
            
        Returns:
            执行成功返回True，失败返回False
        """
        result_os = os.system(command)
        # 或使用 result_os = subprocess.call(command)
        if result_os == 0:
            return True
        logger.warning("fail, execute_command_os: %s, %s" % (result_os, command))
        return False

    @staticmethod
    @Decorate.catch(None)
    def execute_command_popen(command: str, flag_os: bool = True) -> Optional[str]:
        """执行系统命令, 返回控制台输出。
        
        popen() 创建一个管道，通过fork一个子进程,然后该子进程执行命令。返回值在标准IO流中，该管道用于父子进程间通信。
        父进程要么从管道读信息，要么向管道写信息，至于是读还是写取决于父进程调用popen时传递的参数（w或r）。

        注：Popen非常强大，支持多种参数和模式。使用前需要from subprocess import Popen, PIPE。但是Popen函数有一个缺陷，
            就是它是一个阻塞的方法。如果运行cmd时产生的内容非常多，函数非常容易阻塞住。解决办法是不使用wait()方法，
            但是也不能获得执行的返回值了。
        更多： 使用commands.getstatusoutput方法（commands是提供linux系统环境下支持使用shell命令的一个模块）
            这个方法也不会打印出cmd在linux上执行的信息。这个方法唯一的优点是，它不是一个阻塞的方法。
            即没有Popen函数阻塞的问题。
            例如：
            import commands
            status, output = commands.getstatusoutput("ls")
            # 还有只获得output和status的方法：
            # commands.getoutput("ls")
            # commands.getstatus("ls")
            
        Args:
            command: 要执行的命令
            flag_os: 是否使用os模块，否则使用subprocess模块
            
        Returns:
            命令执行的输出结果，失败时返回None
        """
        # popen返回文件对象，跟open操作一样
        if flag_os is True:
            with os.popen(command, "r") as f:
                result_popen = f.read()  # 读
                print("success, execute command of os: %s" % command)
        else:
            # 使用管道输出
            import subprocess
            with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) as f:
                result_data = f.stdout.read()
                try:
                    result_popen = result_data.decode('gbk').strip('\r\n')
                except Exception as e:
                    result_popen = result_data.decode('utf-8').strip('\r\n')
                    print("%s, result: %s" % (e, result_popen))
                print("success, execute command of subprocess: %s" % command)
        return result_popen

    @staticmethod
    def execute_command(command: str) -> Optional[str]:
        """执行系统命令。
        
        Args:
            command: 要执行的命令
            
        Returns:
            命令执行的输出结果
        """
        # 执行系统命令，不打印
        return Tools.execute_command_popen(command)

    @staticmethod
    def get_host_name() -> str:
        """查询本机电脑名。
        
        Returns:
            本机电脑名
        """
        import socket
        # 获取本机电脑名
        return socket.getfqdn(socket.gethostname())

    @staticmethod
    def get_host() -> str:
        """查询本机ip地址。
        
        Returns:
            本机IP地址
        """
        return Tools.get_host_dns()

    @staticmethod
    def get_host_win() -> str:
        """查询本机ip地址(Linux中可能报错)。
        
        Returns:
            本机IP地址
        """
        import socket
        host = socket.gethostbyname(Tools.get_host_name())
        print("本机IP: %s" % host)
        return host

    @staticmethod
    @Decorate.catch("")
    def get_host_dns(dns: str = "8.8.8.8", port: int = 80) -> str:
        """查询本机ip地址。
        
        Args:
            dns: DNS服务器地址，默认为"8.8.8.8"
            port: 端口号，默认为80
            
        Returns:
            本机IP地址，失败时返回空字符串
        """
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((dns, port))
            ip = s.getsockname()[0]
            print("本机IP: %s" % ip)
            return ip



    @staticmethod
    def read_config_local(name_config: str, encoding: str = "utf-8-sig",
                          flag_base_conf: bool = True, **kwargs) \
            -> Tuple[Optional[dict], Optional[dict]]:
        """读取本地配置文件，获取所有配置参数。
        
        注：所有配置默认为字符串类型，获取后需自行转换类型
        参考: 利用configparser模块读写配置文件
             https://www.cnblogs.com/imyalost/p/8857896.html
        
        Args:
            name_config: 配置文件路径
            encoding: 编码格式
            flag_base_conf: 是否使用基础的INI文件读取类RawConfigParser，
                           否则使用ConfigParser (含有%时会抛出异常)
            **kwargs: 其他参数
            
        Returns:
            元组，包含两个字典：按划分存储配置参数, 按键值存储所有配置参数
        """
        # logger.debug("read local config file: %s" % name_config)
        # print("read local config file: %s" % name_config)
        # 参数配置, 按照(section)划分
        dict_config = {}
        # 参数配置, 存放所有参数键值对
        dict_all = {}

        '''RawConfigParser是最基础的INI文件读取类，ConfigParser、SafeConfigParser支持对%(value)s变量的解析'''
        import configparser
        if flag_base_conf:
            config_obj = configparser.RawConfigParser()
        else:
            config_obj = configparser.ConfigParser()
        # 默认配置名为小写形式，重载为大小写正常
        config_obj.optionxform = lambda option: option
        try:
            # 文件是是否存在
            if not Tools.isfile(name_config):
                log_err = "not found config file: %s" % name_config
                raise Exception(log_err)

            config_obj.read(name_config, encoding=encoding)
            # section列表
            dict_config["sections"] = config_obj.sections()
            # 循环处理所有section
            for section in config_obj.sections():
                # 划分的部件名
                # section = tuple_section[0]
                # print("Section:", section)
                # options(section) 得到section下的所有option, 即配置参数的键
                # list_option = config_obj.options(section)
                # print(list_option)
                # items 得到section的所有键值对, 如[('node_id', 'IRM_112'), ('windows_ip', '192.168.1.111')]
                list_tuple = config_obj.items(section)
                # print(list_tuple)
                # 存放当前section内所有配置参数
                dict_section = {}
                for tuple_item in list_tuple:
                    # 所有配置参数
                    dict_all[tuple_item[0]] = tuple_item[1]
                    # section内的配置
                    dict_section[tuple_item[0]] = tuple_item[1]
                # 每个setion内的数据.0
                dict_config[section] = dict_section
            return dict_config, dict_all
        except Exception as e:
            # logger.exception("异常，读取配置文件失败(%s): %s" % (name_config, e))
            logger.exception("异常，读取配置文件失败(%s): %s" % (name_config, e))
        return None, None

    @staticmethod
    def load_config_ini(file_conf: str, **kwargs) -> Optional[Dict[str, str]]:
        """加载本地INI配置文件。
        
        Args:
            file_conf: 配置文件路径
            **kwargs: 其他参数
            
        Returns:
            配置参数字典，失败时返回None
        """
        return Tools.read_config_local(file_conf, **kwargs)[1]

    @staticmethod
    def exec_func_old(module_name: str, func_name: str, *args, **kwargs):
        """执行（字符串）函数，并限制执行时间。
        
        Args:
            module_name: 模块名
            func_name: 函数名
            *args: 位置参数列表
            **kwargs: 关键字参数字典
            
        Returns:
            函数执行结果
        """
        if module_name:
            exec("import %s" % module_name)
        return eval("%s.%s" % (module_name, func_name))(*args, **kwargs)

    @staticmethod
    def exec_func(module_name: Union[str, object], func_name: str, *args, **kwargs):
        """通过字符串执行类的函数。
        
        Args:
            module_name: 模块或模块名
            func_name: 函数名
            *args: 位置参数列表
            **kwargs: 关键字参数字典
            
        Returns:
            函数执行结果
        """
        from importlib import import_module
        # 'a.b' 相当于：from a import b
        if not isinstance(module_name, str):
            return getattr(module_name, func_name)(*args, **kwargs)
        return getattr(import_module(module_name), func_name)(*args, **kwargs)

    @staticmethod
    @Decorate.catch()
    def reload_module(module: Union[str, object]):
        """重新加载导入的模块。
        
        Args:
            module: 模块或模块名
        """
        from importlib import import_module, reload
        if isinstance(module, str):
            reload(import_module(module))
        else:
            reload(module)

    @staticmethod
    def exit(int_flag: int = 0, time_delay: int = 3):
        """退出程序。
        
        注： exit() vs sys.exit()
                exit()会直接将python程序终止，之后的所有代码都不会继续执行。
                sys.exit()会引发一个异常：SystemExit，如果这个异常没有被捕获，
                那么python解释器将会退出。如果有捕获此异常的代码，那么这些代码还是会执行。
                捕获这个异常可以做一些额外的清理工作。0为正常退出，其他数值（1-127）为不正常，可抛异常事件供捕获。
        
        Args:
            int_flag: 0为正常退出，其他数值（1-127）为不正常，可抛异常事件供捕获
            time_delay: 延迟退出，单位秒
        """
        print("警告：程序即将退出 exit: %s！！！！！！！！" % int_flag)
        logger.error("警告：程序即将退出 exit: %s！！！！！！！！" % int_flag)
        Tools.sleep(time_delay)
        # os._exit(int_flag)
        getattr(os, "_exit")(int_flag)

    @classmethod
    def kill(cls, pid: int = os.getpid()):
        """终止进程。
        
        默认终止本进程
        
        Args:
            pid: 进程ID
        """
        if cls.is_windows():
            cmd = "taskkill / PID %s / F" % pid
        else:
            cmd = "sudo kill -9 %s" % pid
        Tools.execute_command(cmd)

    @classmethod
    def run_in_background(cls, output: str = '/dev/null') -> bool:
        """程序后台运行。
        
        Args:
            output: 重定向输出路径
            
        Returns:
            成功返回True，否则返回False
        """
        if cls.is_windows():
            logger.warning("警告, 转入后台失败, 不支持当前类型系统: %s" % cls.get_system_type())
            return False

        import os
        import sys
        import signal
        # 创建一个子进程
        try:
            pid = os.fork()
            if pid > 0:
                # 在父进程中退出，让子进程独立运行
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"Fork failed: {e}\n")
            sys.exit(1)

        # 子进程成为新的会话组长和进程组长，脱离终端控制
        os.setsid()

        # 忽略控制终端的信号
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

        # 将标准输出和标准错误重定向到 /dev/null
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(output, 'r')
        so = open(output, 'a+')
        se = open(output, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        return True

    @staticmethod
    def parse_args(args: Union[list, tuple] = None, start: str = "--",
                   seq: str = "=") -> Dict[str, str]:
        """解析命令行参数。
        
        示例：python xxx.py --log=file
        
        Args:
            args: 参数列表，默认为None时使用sys.argv
            start: 参数前缀，默认为"--"
            seq: 参数分隔符，默认为"="
            
        Returns:
            解析后的参数字典
        """
        # 输入参数
        dict_arg = dict()
        if not args:
            import sys
            args: List[str] = sys.argv
        # 遍历处理
        for item in args:
            # 提取 --xxx=xxx 格式参数
            if isinstance(item, str) and item.startswith(start) and seq in item:
                # 切割
                key, val = item.split(seq, 1)
                dict_arg[key.replace(start, "", 1)] = val
        return dict_arg

    @staticmethod
    def generate_get_set_str(class_obj, style_java: bool = False, return_type: bool = True) -> str:
        """根据类的属性生成get、set方法字符串。
        
        Args:
            class_obj: 类对象
            style_java: 是否使用Java风格（驼峰命名），默认为False（Python下划线风格）
            return_type: 是否包含返回值类型注解，默认为True
            
        Returns:
            生成的get、set方法字符串
        """
        # 结果
        result = ""
        ''' 生成get、set '''
        set_str = "set_"
        get_str = "get_"
        for key in class_obj.__dict__:
            # java风格，驼峰型，无下划线
            if style_java:
                set_str = "set"
                get_str = "get"
                # 首字母大些，其余不变
                key_upper = key[0].upper() + key[1:]
                if "_" in key_upper:
                    # print(key_upper)
                    key_upper = key_upper.title().replace("_", "")
                    # print(key_upper)

            # 变量类型
            # print(type(eval("class_obj.%s" % key)), key)
            # <class 'int'>
            type_key = str(type(eval("class_obj.%s" % key))) \
                .replace("<class '", "").replace("'>", "")
            # print("\t # 变量类型:", type_key, key)
            # result += "\t# parameter: %s %s\n" % (type_key, key)
            # 标明返回值类型
            if return_type and type_key != "NoneType":
                # set
                result += "\tdef %s%s(self, %s: %s):\n" \
                          "\t\t\"\"\"Set attribute %s.\n\n" \
                          "\t\tArgs:\n" \
                          "\t\t\t%s: Value to set\n\t\t\"\"\"\n" \
                          % (set_str, key_upper, key, type_key, key, key)
                # (定制化) 转换格式
                # result += "\t\tself.set_params(\"%s\", %s, %s)\n" % (key, key, type_key)

                result += "\t\tself.%s = %s\n\n" % (key, key)

                # get
                result += "\tdef %s%s(self) -> %s:\n" \
                          "\t\t\"\"\"Get attribute %s.\n\n" \
                          "\t\tReturns:\n" \
                          "\t\t\t%s: The %s value\n\t\t\"\"\"\n" \
                          % (get_str, key_upper, type_key, key, type_key, key)
                result += "\t\treturn self.%s\n\n" % key
            else:
                # set
                result += "\tdef %s%s(self, %s):\n" \
                          "\t\t\"\"\"Set attribute %s.\n\n" \
                          "\t\tArgs:\n" \
                          "\t\t\t%s: Value to set\n\t\t\"\"\"\n" \
                          % (set_str, key_upper, key, key, key)
                result += "\t\tself.%s = %s\n\n" % (key, key)

                # get
                result += "\tdef %s%s(self):\n" \
                          "\t\t\"\"\"Get attribute %s.\n\n" \
                          "\t\tReturns:\n" \
                          "\t\t\tThe %s value\n\t\t\"\"\"\n" \
                          % (get_str, key_upper, key, key)
                result += "\t\treturn self.%s\n\n" % key

            # print("def set_" + k + "(self," + k + "):")
            # print("\tself." + k, "=" + k)
            # print("def get_" + k + "(self):")
            # print("\treturn self." + k)
        print(result)
        return result

    # 打印变量名
    # import inspect
    # import re
    # def debugPrint(x):
    #     frame = inspect.currentframe().f_back
    #     s = inspect.getframeinfo(frame).code_context[0]
    #     r = re.search(r"\((.*)\)", s).group(1)
    #     print("{} = {}".format(r, x))

    """ 加解密相关 md5/sha1/base64 """

    # TODO 加解密相关 md5/sha1/base64

    @staticmethod
    def encode_sha1(data: Union[str, bytes], encoding: str = "utf-8") -> str:
        """SHA1编码。
        
        Args:
            data: 待编码数据
            encoding: 编码格式
            
        Returns:
            SHA1编码后的十六进制字符串
        """
        from hashlib import sha1
        # print("\t 进行sha1编码: %s" % str(data[:80]))
        if isinstance(data, bytes):
            return sha1(data).hexdigest()
        else:
            return sha1(bytes(data, encoding=encoding)).hexdigest()

    @staticmethod
    def encode_md5(data: Union[str, bytes], encoding: str = "utf-8") -> str:
        """MD5编码。
        
        Args:
            data: 待编码数据
            encoding: 编码格式
            
        Returns:
            MD5编码后的十六进制字符串
        """
        from hashlib import md5
        # print("\t 进行md5编码: %s" % str(data[:80]))
        if isinstance(data, bytes):
            return md5(data).hexdigest()
        else:
            return md5(data.encode(encoding=encoding)).hexdigest()

    @staticmethod
    def encode_md5_file(filename: str, size: int = 2048) -> str:
        """计算文件MD5编码。
        
        Args:
            filename: 文件路径
            size: 读取大小，-1则读取所有
            
        Returns:
            文件MD5编码后的十六进制字符串
        """
        from hashlib import md5
        # 创建md5对象
        m = md5()
        with open(filename, 'rb') as fp:
            while True:
                # 每次读取一定大小，默认2MB
                data = fp.read(size)
                if not data:
                    break
                # 更新md5对象
                m.update(data)
        return m.hexdigest()

    @staticmethod
    @Decorate.catch()
    def encode_base64(data: Union[str, bytes], encoding: str = 'utf-8') -> bytes:
        """Base64编码。
        
        Args:
            data: 待编码数据
            encoding: 编码方式
            
        Returns:
            Base64编码后的字节数据
        """
        from base64 import b64encode
        # print("\t 进行base64编码: %s" % str(data[:80]))
        if isinstance(data, str):
            data = data.encode(encoding=encoding, errors='strict')
        return b64encode(data)

    @staticmethod
    @Decorate.catch()
    def encode_base64_str(data: Union[str, bytes], encoding: str = 'utf-8') -> str:
        """将数据进行Base64编码并返回字符串。
        
        Args:
            data: 需要编码的数据，可以是字符串或字节
            encoding: 编码方式，默认为utf-8
            
        Returns:
            Base64编码后的字符串
        """
        return Tools.encode_base64(data, encoding=encoding).decode(encoding=encoding)

    @staticmethod
    @Decorate.catch()
    def decode_base64(data: str, validate: bool = False) -> bytes:
        """Base64解码。
        
        Args:
            data: 需要解码的数据
            validate: 是否忽略错误
            
        Returns:
            Base64解码后的字节数据
        """
        from base64 import b64decode
        # print("\t 进行base64解码: %s" % str(data[:80]))
        return b64decode(data, validate=validate)

    @staticmethod
    @Decorate.catch()
    def decode_base64_str(data: str, validate: bool = False, encoding: str = 'utf-8') -> str:
        """Base64解码并返回字符串。
        
        Args:
            data: 需要解码的数据
            validate: 是否忽略错误
            encoding: 编码方式
            
        Returns:
            Base64解码后的字符串
        """
        from base64 import b64decode
        # print("\t 进行base64解码: %s" % str(data[:80]))
        return b64decode(data, validate=validate).decode(encoding=encoding)

    @staticmethod
    def eval_sec(value):
        """eval的安全替代方案。
        
        注：ast.literal_eval是python针对eval方法存在的安全漏洞而提出的一种安全处理方式。
            简单点说ast模块就是帮助Python应用来处理抽象的语法解析的。而该模块下的literal_eval()函数：则会判断需
            要计算的内容计算后是不是合法的Python类型，如果是则进行运算，否则就不进行运算。
        
        Args:
            value: 支持strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
            
        Returns:
            计算结果
        """
        from ast import literal_eval
        return literal_eval(value)

    @classmethod
    def eval(cls, value):
        """eval的安全替代方案。
        
        Args:
            value: 支持strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
            
        Returns:
            计算结果
        """
        return cls.eval_sec(value)

    """ 挂载相关 ftp/sftp/smb/nfs """

    @staticmethod
    def is_mount(path: str) -> bool:
        """检查路径是否已被挂载且没有取消。
        
        Args:
            path: 路径
            
        Returns:
            已挂载返回True，否则返回False
        """
        return os.path.ismount(path)

    @staticmethod
    @Decorate.catch()
    def umount(path: str) -> int:
        """卸载/解除挂载。
        
        Args:
            path: 已挂载路径
            
        Returns:
            系统命令执行结果
        """
        print("[unmount] 卸载/解除挂载: %s" % path)
        # 卸载/解除挂载
        return os.system("umount %s" % path)

    @staticmethod
    def mount(remote: str, local_path: str) -> bool:
        """远程挂载，暂支持 smb|ftp|sftp|nfs。
        
        Args:
            remote: 远程路径，格式如 [smb|ftp|sftp|nfs]://username:password@172.168.1.209/home/
            local_path: 本地挂载路径
            
        Returns:
            挂载成功返回True，否则返回False
        """
        # 结果
        ret = False
        # 挂载协议/方式
        mount_type: str = remote.split("://", 1)[0]
        # 账号密码和远程地址信息
        user, host = remote.split("://", 1)[-1].rsplit("@", 1)
        # 账号、密码
        username, password = user.split(":", 1)
        # ip、路径
        remote_ip, remote_path = host.split("/", 1)
        remote_path = "/" + remote_path

        if Tools.is_mount(local_path):
            logger.info("[mount] ignore, had mount: [%s] %s, %s" % (mount_type, remote_ip,
                                                                    remote_path))
            return True

        # 开始生成挂载命令
        if mount_type == 'smb':
            command = 'mount -o vers=2.0,username=' + username + ',password=' + \
                      password + ' //' + remote_ip + remote_path + ' ' + local_path
        elif mount_type == 'ftp':
            command = 'curlftpfs -o rw,allow_other ftp://' + username + ':' + \
                      password + '@' + remote_ip + '/' + remote_path + ' ' + local_path
        elif mount_type == 'sftp':
            command = 'echo ' + password + ' | sshfs -p 22 ' + username + '@' + remote_ip + ':' \
                      + remote_path + ' ' + local_path + ' -o password_stdin'
        elif mount_type == 'nfs':
            command = 'mount -t nfs ' + remote_ip + ':' + remote_path + ' ' + local_path
        else:
            logger.error('[mount] fail, remote path is not in correct format!')
            return ret

        # 提前创建目录
        Tools.makedirs(local_path)

        # 尝试挂载
        try:
            logger.debug(
                '[mount] remote filepath mount is in progress: %s, %s' % (mount_type, remote_ip))
            print('command is %s' % command)
            result = os.system(command)
            # 检测是否挂载成功
            # if result == 0:
            if Tools.is_mount(local_path):
                logger.info('[mount] ok, remote path mount successfully, ret: %s, [%s] %s'
                            % (result, mount_type, remote_ip))
                ret = True
            else:
                logger.warning('[mount] Warn, remote path mount fail, ret: %s, [%s] %s'
                               % (result, mount_type, remote_ip))
        except BaseException as e:
            logger.error('[mount] Error, mount %s remote path faild! %s: %s' % (mount_type,
                                                                                remote_ip, e))
        return ret

    """ 九、http及网络爬虫相关，如：指纹验证(ja3) """

    # TODO url相关

    @staticmethod
    def url_quote(url: str) -> str:
        """URL编码。
        
        Args:
            url: 需要编码的URL
            
        Returns:
            编码后的URL字符串
        """
        import urllib.parse
        return urllib.parse.quote(url)

    @staticmethod
    def url_unquote(url: str) -> str:
        """URL解码。
        
        Args:
            url: 需要解码的URL
            
        Returns:
            解码后的URL字符串
        """
        import urllib.parse
        return urllib.parse.unquote(url)

    @staticmethod
    def url_parse(url: str):
        """解析URL。
        
        URL拆解结果包含以下属性：
            - scheme (协议): https
            - hostname (域名/主机名): hostname
            - netloc (网络位置): www.example.com:8080
            - path (路径): /path/to/resource
            - params (参数): 通常为空字符串
            - query (查询参数): param1=value1&param2=value2
            - fragment (片段标识): section
            - username (用户名): 通常为空字符串
            - password (密码): 通常为空字符串
            - port (端口号): 8080
            
        Args:
            url: 要解析的链接
            
        Returns:
            解析后的URL对象
        """
        # 使用urlparse解析URL
        return urlparse(url)

    @staticmethod
    def url_scheme(url: str) -> str:
        """获取URL协议。
        
        Args:
            url: 链接
            
        Returns:
            URL的协议部分
        """
        return urlparse(url).scheme

    @staticmethod
    def url_domain(url: str) -> Optional[str]:
        """获取URL域名(主机名)。
        
        Args:
            url: 链接
            
        Returns:
            URL的域名部分，可能为None
        """
        return urlparse(url).hostname

    @staticmethod
    def url_netloc(url: str) -> str:
        """获取URL的Netloc (网络位置)，如：www.example.com:8080。
        
        Args:
            url: 链接
            
        Returns:
            URL的网络位置部分
        """
        return urlparse(url).netloc

    @staticmethod
    def url_root(url: str) -> str:
        """获取URL根路径，即 协议+域名(包含主机名和端口)。
        
        Args:
            url: 链接
            
        Returns:
            URL的根路径
        """
        return urlparse(url).scheme + "://" + urlparse(url).netloc

    @staticmethod
    def url_path(url: str) -> str:
        """获取URL路径。
        
        Args:
            url: 链接
            
        Returns:
            URL的路径部分
        """
        return urlparse(url).path

    @staticmethod
    def url_port(url: str) -> Optional[int]:
        """获取URL端口号。
        
        Args:
            url: 链接
            
        Returns:
            URL的端口号，可能为None
        """
        return urlparse(url).port

    @staticmethod
    def gen_ssl_ciphers() -> str:
        """生成SSL密码套件。
        
        Returns:
            SSL密码套件字符串
        """
        return SSLFactory.gen_ciphers()

    @staticmethod
    def gen_ssl_context():
        """生成SSL上下文，随机生成指纹(ja3)。
        
        注：应对反爬，如百度安全校验
        
        Returns:
            SSL上下文对象
        """
        return SSLFactory()()

    @classmethod
    def gen_ssl_ja3(cls):
        """生成SSL JA3指纹。
        
        Returns:
            SSL上下文对象
        """
        return cls.gen_ssl_context()


Tools.get_system_win = Tools.is_windows

# 检查是否为windows系统
Tools.check_system_win()


class SSLFactory:
    ORIGIN_CIPHERS = (
        "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:"
        "DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES"
    )
    _CIPHERS = ORIGIN_CIPHERS.split(":")

    def __init__(self):
        # self._ciphers = self.ORIGIN_CIPHERS.split(":")
        pass

    @classmethod
    def gen_ciphers(cls) -> str:
        """生成密码套件。
        
        Returns:
            随机排序的密码套件字符串
        """
        random.shuffle(cls._CIPHERS)
        ciphers = ":".join(cls._CIPHERS)
        ciphers = ciphers + ":!aNULL:!eNULL:!MD5"
        return ciphers

    def __call__(self):
        """返回SSL上下文。
        
        Returns:
            ssl.SSLContext: SSL上下文对象
        """
        ciphers = self.gen_ciphers()
        # print("ciphers:", ciphers)

        import ssl
        context = ssl.create_default_context()
        context.set_ciphers(ciphers)
        return context


# 查看运行所需内存
# import psutil
# print('内存使用：{}MB'.format(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))

def main():
    """主函数，用于测试工具类功能。"""
    # list
    a = [{"a": 1}]
    # tuple
    # b = ({"b": 1},)
    # print(json.dumps(a, ensure_ascii=False))
    print(Tools.to_jsonstr(a))
    print(isinstance(a, Iterable))
    print('dict isinstance', isinstance(dict(), Iterable))
    print('"" isinstance', isinstance("", Iterable))
    print('"" is', type("") is Iterable)
    print('2 isinstance', isinstance(2, Iterable))
    print('2 is', type(2) is Iterable)

    print(Tools.check_disk_space())
    print(Tools.get_file_name("/home/test"))

    Tools.exit()


if __name__ == '__main__':
    main()
