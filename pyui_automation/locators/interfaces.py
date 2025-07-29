"""
Locator interfaces for SOLID compliance.

This module defines interfaces for locators to ensure
Dependency Inversion Principle compliance.
"""

from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, List, Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import LocatorStrategy


class IBackendForLocator(Protocol):
    """Interface for backend functionality needed by locators"""
    
    @property
    def logger(self) -> Logger:
        """Get logger instance"""
        ...
    
    @property
    def root(self) -> Any:
        """Get root element"""
        ...
    
    def _find_element_recursive(self, element: Any, property_name: str, value: str) -> Optional[Any]:
        """Find element recursively by property"""
        ...
    
    def _find_elements_recursive(self, element: Any, property_name: str, value: str, results: List[Any]) -> None:
        """Find elements recursively by property"""
        ...
    
    def find_element_by_text(self, text: str) -> Optional[Any]:
        """Find element by text"""
        ...
    
    def find_elements_by_text(self, text: str) -> List[Any]:
        """Find elements by text"""
        ...
    
    def find_element_by_property(self, property_name: str, value: str) -> Optional[Any]:
        """Find element by property"""
        ...
    
    def find_elements_by_property(self, property_name: str, value: str) -> List[Any]:
        """Find elements by property"""
        ...
    
    def find_element_by_object_name(self, name: str) -> Optional[Any]:
        """Find element by object name"""
        ...
    
    def find_elements_by_object_name(self, name: str) -> List[Any]:
        """Find elements by object name"""
        ...
    
    def find_element_by_widget_type(self, widget_type: str) -> Optional[Any]:
        """Find element by widget type"""
        ...
    
    def find_elements_by_widget_type(self, widget_type: str) -> List[Any]:
        """Find elements by widget type"""
        ...


class ILocator(ABC):
    """Interface for element locators"""
    
    @abstractmethod
    def find_element(self, strategy: "LocatorStrategy") -> Optional[Any]:
        """Find a single element by specific strategy"""
        pass
    
    @abstractmethod
    def find_elements(self, strategy: "LocatorStrategy") -> List[Any]:
        """Find multiple elements by specific strategy"""
        pass
    
    def find_element_with_timeout(self, strategy: "LocatorStrategy", timeout: float = 10.0) -> Optional[Any]:
        """Find element with timeout"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            element = self.find_element(strategy)
            if element:
                return element
            time.sleep(0.1)
        
        return None
    
    def wait_for_element(self, strategy: "LocatorStrategy", timeout: float = 10.0) -> Optional[Any]:
        """Wait for element to appear (alias for find_element_with_timeout)"""
        return self.find_element_with_timeout(strategy, timeout)


class ILocatorStrategy(ABC):
    """Interface for locator strategies"""
    
    @property
    @abstractmethod
    def value(self) -> str:
        """Get strategy value"""
        pass
    
    @property
    @abstractmethod
    def timeout(self) -> Optional[float]:
        """Get strategy timeout"""
        pass 