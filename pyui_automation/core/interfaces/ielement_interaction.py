"""
IElementInteraction interface - defines contract for element interactions.

Responsible for:
- Element clicking
- Element text input
- Element focus
- Element drag and drop
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .ielement import IElement


class IElementInteraction(ABC):
    """Interface for element interactions"""
    
    @abstractmethod
    def click(self) -> None:
        """Click on element"""
        pass
    
    @abstractmethod
    def double_click(self) -> None:
        """Double click on element"""
        pass
    
    @abstractmethod
    def right_click(self) -> None:
        """Right click on element"""
        pass
    
    @abstractmethod
    def hover(self) -> None:
        """Hover over element"""
        pass
    
    @abstractmethod
    def send_keys(self, *keys: str, interval: Optional[float] = None) -> None:
        """Send keys to element"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear element text"""
        pass
    
    @abstractmethod
    def append(self, text: str) -> None:
        """Append text to element"""
        pass
    
    @abstractmethod
    def focus(self) -> None:
        """Focus on element"""
        pass
    
    @abstractmethod
    def select_all(self) -> None:
        """Select all text in element"""
        pass
    
    @abstractmethod
    def copy(self) -> None:
        """Copy element text"""
        pass
    
    @abstractmethod
    def paste(self) -> None:
        """Paste text to element"""
        pass
    
    @abstractmethod
    def drag_and_drop(self, target: 'IElement') -> None:
        """Drag and drop element to target"""
        pass
    
    @abstractmethod
    def scroll_into_view(self) -> None:
        """Scroll element into view"""
        pass
    
    @abstractmethod
    def safe_click(self, timeout: Optional[float] = None) -> bool:
        """Safely click element with timeout"""
        pass 