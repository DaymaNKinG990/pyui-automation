"""
IElementState interface - defines contract for element state.

Responsible for:
- Element visibility
- Element enabled state
- Element checked state
- Element expanded state
- Element selected state
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IElementState(ABC):
    """Interface for element state"""
    
    @property
    @abstractmethod
    def visible(self) -> bool:
        """Get element visibility"""
        pass
    
    @abstractmethod
    def is_displayed(self) -> bool:
        """Check if element is displayed"""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if element is enabled"""
        pass
    
    @property
    @abstractmethod
    def is_checked(self) -> bool:
        """Get element checked state"""
        pass
    
    @is_checked.setter
    @abstractmethod
    def is_checked(self, value: bool) -> None:
        """Set element checked state"""
        pass
    
    @property
    @abstractmethod
    def is_expanded(self) -> bool:
        """Get element expanded state"""
        pass
    
    @is_expanded.setter
    @abstractmethod
    def is_expanded(self, value: bool) -> None:
        """Set element expanded state"""
        pass
    
    @property
    @abstractmethod
    def selected_item(self) -> Optional[str]:
        """Get selected item"""
        pass
    
    @selected_item.setter
    @abstractmethod
    def selected_item(self, value: str) -> None:
        """Set selected item"""
        pass
    
    @property
    @abstractmethod
    def value(self) -> Optional[str]:
        """Get element value"""
        pass
    
    @value.setter
    @abstractmethod
    def value(self, new_value: str) -> None:
        """Set element value"""
        pass
    
    @abstractmethod
    def is_pressed(self) -> bool:
        """Check if element is pressed"""
        pass
    
    @abstractmethod
    def is_selected(self) -> bool:
        """Check if element is selected"""
        pass
    
    @abstractmethod
    def get_state_summary(self) -> Dict[str, Any]:
        """Get element state summary"""
        pass 