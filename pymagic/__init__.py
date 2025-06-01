# coding: utf-8
"""
PyMagic - A utility library for Python development

This package provides various utilities for logging, debugging, and common operations.
"""

__version__ = "0.0.1"
__author__ = "Guyue"

# Import main components for easier access
from ._base import Base
from .logger_utils import logger
from .tools_utils import Tools
from .decorator_utils import Decorate