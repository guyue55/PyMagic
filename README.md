# PyMagic

高效的 Python 工具库，提供日志、装饰器、常用工具等模块，助力开发者快速构建高质量项目。

## 目录
- [简介](#简介)
- [安装](#安装)
- [用法](#用法)
- [模块说明](#模块说明)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 简介
PyMagic 是一个专为 Python 开发者设计的工具库，涵盖日志管理、装饰器、常用工具函数等，旨在提升开发效率和代码质量。

## 安装
1. 克隆仓库：
   ```bash
   git clone https://github.com/yourname/PyMagic.git
   ```
2. 进入目录并安装依赖：
   ```bash
   cd PyMagic
   pip install -r requirements.txt
   ```

## 用法
以日志工具为例：
```python
from pymagic.logger_utils import LoggerUtils
log = LoggerUtils.get_log()
log.info("Hello, PyMagic!")
```
更多用法请参考 `tests/` 目录下的测试用例。

## 模块说明
- `pymagic/logger_utils.py`：日志工具，基于 loguru 封装，支持多实例和多格式输出。
- `pymagic/decorator_utils.py`：常用装饰器，如异常捕获、性能计时、单例等。
- `pymagic/tools_utils.py`：常用工具函数，涵盖字符串、时间、系统等操作。

## 贡献指南
欢迎提交 issue 和 PR，建议遵循 Google Python Style Guide，文件命名使用小写字母、数字和下划线，缩进为4空格，异常需妥善处理。

## 许可证
MIT License