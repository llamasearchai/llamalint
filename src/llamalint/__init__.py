"""
LlamaLint - Code linting and formatting tools for LlamaSearch.ai projects
"""

__version__ = "0.1.0"
__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__license__ = "MIT"

from llamalint.config import Config
from llamalint.formatters import Formatter
from llamalint.linter import LlamaLint
from llamalint.rules import Rule

__all__ = [
    "LlamaLint",
    "Rule",
    "Formatter",
    "Config",
] 