"""
IElementDiscoveryService interface - defines contract for element discovery service.

Responsible for:
- Finding elements by various strategies
- Element discovery with timeouts
- Element search operations
"""

from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...elements.base_element import BaseElement
from ...locators import LocatorStrategy


class IElementDiscoveryService(ABC):
    """Interface for element discovery service"""
    
    @abstractmethod
    def find_element(self, strategy: LocatorStrategy) -> Optional["BaseElement"]:
        """Find element using locator strategy"""
        pass
    
    @abstractmethod
    def find_elements(self, strategy: LocatorStrategy) -> List["BaseElement"]:
        """Find elements using locator strategy"""
        pass
    
    @abstractmethod
    def find_element_with_timeout(self, strategy: LocatorStrategy, timeout: float = 10.0) -> Optional["BaseElement"]:
        """Find element with timeout"""
        pass
    
    @abstractmethod
    def find_element_by_object_name(self, object_name: str, timeout: float = 0) -> Optional["BaseElement"]:
        """Find element by object name"""
        pass
    
    @abstractmethod
    def find_elements_by_object_name(self, object_name: str) -> List["BaseElement"]:
        """Find elements by object name"""
        pass
    
    @abstractmethod
    def find_element_by_widget_type(self, widget_type: str, timeout: float = 0) -> Optional["BaseElement"]:
        """Find element by widget type"""
        pass
    
    @abstractmethod
    def find_elements_by_widget_type(self, widget_type: str) -> List["BaseElement"]:
        """Find elements by widget type"""
        pass
    
    @abstractmethod
    def find_element_by_text(self, text: str, timeout: float = 0) -> Optional["BaseElement"]:
        """Find element by text"""
        pass
    
    @abstractmethod
    def find_elements_by_text(self, text: str) -> List["BaseElement"]:
        """Find elements by text"""
        pass
    
    @abstractmethod
    def find_element_by_property(self, property_name: str, value: str, timeout: float = 0) -> Optional["BaseElement"]:
        """Find element by property"""
        pass
    
    @abstractmethod
    def find_elements_by_property(self, property_name: str, value: str) -> List["BaseElement"]:
        """Find elements by property"""
        pass
    
    @abstractmethod
    def get_active_window(self) -> Optional["BaseElement"]:
        """Get active window as element"""
        pass 