"""
Linting rules for various languages and coding styles
"""
from typing import Any, Dict, List, Optional, Set, Type

from llamalint.rules.base import Rule, RuleResult, RuleOption

# Import all rule classes
# These will be added as more rules are implemented
from llamalint.rules.python.imports import ImportsRule
from llamalint.rules.python.docstrings import DocstringsRule
from llamalint.rules.python.naming import NamingConventionsRule
from llamalint.rules.javascript.imports import JSImportsRule
from llamalint.rules.typescript.types import TypesRule

# Export rule base classes and results
__all__ = ["Rule", "RuleResult", "RuleOption", "get_all_rules"]

# Registry of all available rules
_RULES: List[Type[Rule]] = [
    ImportsRule,
    DocstringsRule,
    NamingConventionsRule,
    JSImportsRule,
    TypesRule,
]

def get_all_rules() -> List[Type[Rule]]:
    """
    Get all available rule classes
    
    Returns:
        List of rule classes
    """
    return _RULES.copy()

def register_rule(rule_cls: Type[Rule]) -> None:
    """
    Register a custom rule
    
    Args:
        rule_cls: Rule class to register
    """
    if rule_cls not in _RULES:
        _RULES.append(rule_cls) 