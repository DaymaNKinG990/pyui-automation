"""
IBackendWindow interface - defines contract for window operations.

Responsible for:
- Window discovery
- Window management
- Window properties
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Tuple


class IBackendWindow(ABC):
    """Interface for window operations"""
    
    @abstractmethod
    def get_active_window(self) -> Optional[Any]:
        """Get currently active window"""
        pass
    
    @abstractmethod
    def get_window_handles(self) -> List[Any]:
        """Get all window handles"""
        pass
    
    @abstractmethod
    def find_window(self, title: str) -> Optional[Any]:
        """Find window by title"""
        pass
    
    @abstractmethod
    def get_window_title(self, window: Any) -> str:
        """Get window title"""
        pass
    
    @abstractmethod
    def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
        """Get window position and size"""
        pass
    
    @abstractmethod
    def maximize_window(self, window: Any) -> None:
        """Maximize window"""
        pass
    
    @abstractmethod
    def minimize_window(self, window: Any) -> None:
        """Minimize window"""
        pass
    
    @abstractmethod
    def resize_window(self, window: Any, width: int, height: int) -> None:
        """Resize window"""
        pass
    
    @abstractmethod
    def set_window_position(self, window: Any, x: int, y: int) -> None:
        """Set window position"""
        pass
    
    @abstractmethod
    def close_window(self, window: Any) -> None:
        """Close window"""
        pass 