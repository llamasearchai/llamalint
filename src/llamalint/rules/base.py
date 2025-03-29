"""
Base class and utilities for linting rules
"""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple, Union


@dataclass
class RuleOption:
    """
    Configuration option for a rule
    """
    name: str
    description: str
    default: Any
    choices: Optional[List[Any]] = None
    

@dataclass
class RuleResult:
    """
    Result of a rule check
    """
    rule_id: str
    file_path: str
    line: int
    column: int
    message: str
    severity: str = "error"  # error, warning, info
    source: Optional[str] = None
    fix: Optional[str] = None
    fix_type: Optional[str] = None  # replace_line, replace_range
    fix_range: Optional[Tuple[int, int]] = None  # start, end column for range fixes
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary with result data
        """
        return {
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "severity": self.severity,
            "source": self.source,
            "fixable": self.fix is not None,
        }


class Rule(ABC):
    """
    Base class for all linting rules
    """
    
    # Class attributes to be overridden by subclasses
    id: str = "base-rule"
    name: str = "Base Rule"
    description: str = "Base class for all rules"
    languages: List[str] = []
    file_patterns: List[str] = ["**/*"]
    options: Dict[str, RuleOption] = {}
    default_severity: str = "error"
    examples: List[Dict[str, str]] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize a rule
        
        Args:
            config: Configuration options for this rule
        """
        self.config = config or {}
        self.severity = self.default_severity
        self._file_pattern_regexes = [self._glob_to_regex(pattern) for pattern in self.file_patterns]
        
    def __str__(self) -> str:
        """String representation"""
        return f"{self.id} ({self.name})"
        
    def _glob_to_regex(self, pattern: str) -> Pattern:
        """
        Convert a glob pattern to a regex pattern
        
        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            
        Returns:
            Compiled regex pattern
        """
        # Convert ** to a special marker
        pattern = pattern.replace("**", "__DOUBLE_STAR__")
        
        # Convert * to match anything except directory separator
        pattern = pattern.replace("*", "[^/]*")
        
        # Convert back ** to match anything including directory separators
        pattern = pattern.replace("__DOUBLE_STAR__", ".*")
        
        # Convert ? to match any character except directory separator
        pattern = pattern.replace("?", "[^/]")
        
        # Convert . to escape it in regex
        pattern = pattern.replace(".", "\\.")
        
        # Ensure the pattern matches the entire string
        pattern = f"^{pattern}$"
        
        return re.compile(pattern)
        
    def applies_to_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this rule applies to a given file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the rule applies, False otherwise
        """
        file_path_str = str(file_path).replace("\\", "/")
        
        # Check if any pattern matches
        return any(pattern.search(file_path_str) for pattern in self._file_pattern_regexes)
        
    def get_option(self, name: str) -> Any:
        """
        Get the value of an option
        
        Args:
            name: Name of the option
            
        Returns:
            Value of the option, or default if not set
        """
        if name in self.options:
            return self.config.get(name, self.options[name].default)
        return None
        
    @abstractmethod
    def check(self, file_path: Path, content: str) -> List[RuleResult]:
        """
        Check a file for issues
        
        Args:
            file_path: Path to the file
            content: File content as a string
            
        Returns:
            List of rule results
        """
        pass 