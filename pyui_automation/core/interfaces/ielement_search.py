"""
IElementSearch interface - defines contract for element search.

Responsible for:
- Finding child elements
- Finding parent elements
- Element hierarchy navigation
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .ielement import IElement


class IElementSearch(ABC):
    """Interface for element search"""
    
    @abstractmethod
    def get_parent(self) -> Optional['IElement']:
        """Get parent element"""
        pass
    
    @abstractmethod
    def get_children(self) -> List['IElement']:
        """Get child elements"""
        pass
    
    @abstractmethod
    def find_child_by_property(self, property_name: str, expected_value: Any) -> Optional['IElement']:
        """Find child element by property"""
        pass
    
    @abstractmethod
    def find_children_by_property(self, property_name: str, expected_value: Any) -> List['IElement']:
        """Find child elements by property"""
        pass
    
    @abstractmethod
    def find_child_by_text(self, text: str, exact_match: bool = True) -> Optional['IElement']:
        """Find child element by text"""
        pass
    
    @abstractmethod
    def find_children_by_text(self, text: str, exact_match: bool = True) -> List['IElement']:
        """Find child elements by text"""
        pass
    
    @abstractmethod
    def find_child_by_name(self, name: str, exact_match: bool = True) -> Optional['IElement']:
        """Find child element by name"""
        pass
    
    @abstractmethod
    def find_children_by_name(self, name: str, exact_match: bool = True) -> List['IElement']:
        """Find child elements by name"""
        pass
    
    @abstractmethod
    def find_child_by_control_type(self, control_type: str) -> Optional['IElement']:
        """Find child element by control type"""
        pass
    
    @abstractmethod
    def find_children_by_control_type(self, control_type: str) -> List['IElement']:
        """Find child elements by control type"""
        pass
    
    @abstractmethod
    def find_child_by_automation_id(self, automation_id: str) -> Optional['IElement']:
        """Find child element by automation ID"""
        pass
    
    @abstractmethod
    def find_children_by_automation_id(self, automation_id: str) -> List['IElement']:
        """Find child elements by automation ID"""
        pass
    
    @abstractmethod
    def find_visible_children(self) -> List['IElement']:
        """Find visible child elements"""
        pass
    
    @abstractmethod
    def find_enabled_children(self) -> List['IElement']:
        """Find enabled child elements"""
        pass
    
    @abstractmethod
    def find_child_by_predicate(self, predicate: Callable) -> Optional['IElement']:
        """Find child element by predicate"""
        pass
    
    @abstractmethod
    def find_children_by_predicate(self, predicate: Callable) -> List['IElement']:
        """Find child elements by predicate"""
        pass 