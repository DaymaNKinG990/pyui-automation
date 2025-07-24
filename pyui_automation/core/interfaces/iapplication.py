"""
Application Interface for SOLID compliance.

This module defines interfaces for applications to ensure
Dependency Inversion Principle compliance.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class IApplication(ABC):
    """Interface for application functionality"""
    
    @abstractmethod
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        pass
    
    @abstractmethod
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        pass
    
    @property
    @abstractmethod
    def process(self) -> Optional[Any]:
        """Get process object if available"""
        pass
        
    @abstractmethod
    def memory_info(self) -> Any:
        """Get memory information"""
        pass
        
    @abstractmethod
    def cpu_percent(self) -> float:
        """Get CPU usage percentage"""
        pass 