"""
IElementProperties interface - defines contract for element properties.

Responsible for:
- Element attributes
- Element properties
- Element identification
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IElementProperties(ABC):
    """Interface for element properties"""
    
    @abstractmethod
    def get_attribute(self, name: str) -> Optional[str]:
        """Get element attribute"""
        pass
    
    @abstractmethod
    def get_property(self, name: str) -> Any:
        """Get element property"""
        pass
    
    @abstractmethod
    def get_attributes(self) -> Dict[str, str]:
        """Get all element attributes"""
        pass
    
    @abstractmethod
    def get_properties(self) -> Dict[str, Any]:
        """Get all element properties"""
        pass
    
    @property
    @abstractmethod
    def text(self) -> str:
        """Get element text"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get element name"""
        pass
    
    @property
    @abstractmethod
    def automation_id(self) -> str:
        """Get element automation ID"""
        pass
    
    @property
    @abstractmethod
    def class_name(self) -> str:
        """Get element class name"""
        pass
    
    @property
    @abstractmethod
    def control_type(self) -> str:
        """Get element control type"""
        pass 