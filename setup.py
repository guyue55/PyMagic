# -*- coding: utf-8 -*-
"""PyMagic包的安装配置.

此模块包含PyMagic包的安装配置，
PyMagic是一个Python开发实用工具库，提供日志记录、装饰器
和通用工具。

作者: Guyue
邮箱: guyuecw@qq.com
许可证: MIT
"""

from setuptools import setup, find_packages

# Package metadata
PACKAGE_NAME = "pymagic-guyue"
VERSION = "0.0.1"
AUTHOR = "Guyue"
AUTHOR_EMAIL = "guyuecw@qq.com"
DESCRIPTION = "A utility library for Python development"
URL = "https://github.com/guyue55/pymagic"

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

# Package dependencies
INSTALL_REQUIRES = [
    "loguru>=0.5.0",  # Logging library with better formatting and features
]

# Package classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=["tests*"]),
    install_requires=INSTALL_REQUIRES,
    classifiers=CLASSIFIERS,
    python_requires=">=3.6",
    keywords="python utility tools logging decorators",
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}#readme",
    },
    zip_safe=False,
)
