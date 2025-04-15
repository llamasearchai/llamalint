"""
Code formatters for various languages
"""

from typing import List, Type

from llamalint.formatters.base import Formatter
from llamalint.formatters.javascript import JavaScriptFormatter

# Import all formatter classes
# These will be added as more formatters are implemented
from llamalint.formatters.python import PythonFormatter
from llamalint.formatters.typescript import TypeScriptFormatter

# Export formatter base class
__all__ = ["Formatter", "get_all_formatters"]

# Registry of all available formatters
_FORMATTERS: List[Type[Formatter]] = [
    PythonFormatter,
    JavaScriptFormatter,
    TypeScriptFormatter,
]


def get_all_formatters() -> List[Type[Formatter]]:
    """
    Get all available formatter classes

    Returns:
        List of formatter classes
    """
    return _FORMATTERS.copy()


def register_formatter(formatter_cls: Type[Formatter]) -> None:
    """
    Register a custom formatter

    Args:
        formatter_cls: Formatter class to register
    """
    if formatter_cls not in _FORMATTERS:
        _FORMATTERS.append(formatter_cls)
