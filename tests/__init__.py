# -*- coding: utf-8 -*-
"""PyMagic的测试包.

此包包含所有PyMagic模块和类的单元测试。
测试按模块组织，提供库功能的全面覆盖。

测试模块:
    test_base: Base类的测试
    test_decorator_utils: 装饰器工具的测试
    test_logger_utils: 日志工具的测试
    test_tools_utils: 实用函数的测试

使用方法:
    运行所有测试:
        python -m pytest tests/
    
    运行特定测试模块:
        python -m pytest tests/test_base.py
    
    运行并生成覆盖率报告:
        python -m pytest tests/ --cov=pymagic

作者: Guyue
许可证: MIT
"""