"""
Base class for code formatters
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class Formatter(ABC):
    """
    Base class for all code formatters
    """
    
    # Class attributes to be overridden by subclasses
    id: str = "base-formatter"
    name: str = "Base Formatter"
    description: str = "Base class for all formatters"
    languages: List[str] = []
    file_patterns: List[str] = ["**/*"]
    priority: int = 50  # Higher priority formatters run first (0-100)
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize a formatter
        
        Args:
            config: Configuration options for this formatter
        """
        self.config = config or {}
        
    def __str__(self) -> str:
        """String representation"""
        return f"{self.id} ({self.name})"
        
    def applies_to_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this formatter applies to a given file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the formatter applies, False otherwise
        """
        from llamalint.rules.base import Rule
        
        # Create a temporary Rule instance to use its applies_to_file method
        # This avoids code duplication with the Rule class
        rule = type("TempRule", (Rule,), {"file_patterns": self.file_patterns})({})
        return rule.applies_to_file(file_path)
        
    def get_option(self, name: str, default: Any = None) -> Any:
        """
        Get the value of an option
        
        Args:
            name: Name of the option
            default: Default value if not specified
            
        Returns:
            Value of the option, or default if not set
        """
        return self.config.get(name, default)
        
    @abstractmethod
    def format(self, file_path: Path, content: str) -> str:
        """
        Format file content
        
        Args:
            file_path: Path to the file
            content: File content as a string
            
        Returns:
            Formatted content
        """
        pass 