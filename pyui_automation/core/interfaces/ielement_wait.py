"""
IElementWait interface - defines contract for element waiting.

Responsible for:
- Waiting for element states
- Waiting for element values
- Waiting for element conditions
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable


class IElementWait(ABC):
    """Interface for element waiting"""
    
    @abstractmethod
    def wait_until_enabled(self, timeout: Optional[float] = None) -> bool:
        """Wait until element is enabled"""
        pass
    
    @abstractmethod
    def wait_until_clickable(self, timeout: Optional[float] = None) -> bool:
        """Wait until element is clickable"""
        pass
    
    @abstractmethod
    def wait_until_checked(self, timeout: float = 10) -> bool:
        """Wait until element is checked"""
        pass
    
    @abstractmethod
    def wait_until_unchecked(self, timeout: float = 10) -> bool:
        """Wait until element is unchecked"""
        pass
    
    @abstractmethod
    def wait_until_expanded(self, timeout: float = 10) -> bool:
        """Wait until element is expanded"""
        pass
    
    @abstractmethod
    def wait_until_collapsed(self, timeout: float = 10) -> bool:
        """Wait until element is collapsed"""
        pass
    
    @abstractmethod
    def wait_until_value_is(self, expected_value: str, timeout: Optional[float] = None) -> bool:
        """Wait until element value matches expected value"""
        pass
    
    @abstractmethod
    def wait_for_enabled(self, timeout: Optional[float] = None) -> bool:
        """Wait for element to be enabled"""
        pass
    
    @abstractmethod
    def wait_for_visible(self, timeout: Optional[float] = None) -> bool:
        """Wait for element to be visible"""
        pass
    
    @abstractmethod
    def wait_for_condition(self, condition: Callable, timeout: Optional[float] = None) -> bool:
        """Wait for custom condition"""
        pass 