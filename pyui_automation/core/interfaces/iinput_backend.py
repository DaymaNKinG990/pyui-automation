"""
Input Backend Interface for SOLID compliance.

This module defines interfaces for input backends to ensure
Dependency Inversion Principle compliance.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any


class IInputBackend(ABC):
    """Interface for input backend functionality"""
    
    # Keyboard methods
    @abstractmethod
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """Type text with optional interval between keystrokes"""
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> bool:
        """Press a single key"""
        pass
    
    @abstractmethod
    def release_key(self, key: str) -> bool:
        """Release a single key"""
        pass
    
    @abstractmethod
    def press_keys(self, *keys: str) -> bool:
        """Press multiple keys simultaneously"""
        pass
    
    @abstractmethod
    def release_keys(self, *keys: str) -> bool:
        """Release multiple keys simultaneously"""
        pass
    
    @abstractmethod
    def send_keys(self, keys: str) -> bool:
        """Send a sequence of keys with special key support"""
        pass
    
    # Mouse methods
    @abstractmethod
    def move_mouse(self, x: int, y: int) -> bool:
        """Move mouse cursor to absolute coordinates"""
        pass
    
    @abstractmethod
    def click_mouse(self, button: str = "left") -> bool:
        """Click mouse button"""
        pass
    
    @abstractmethod
    def mouse_down(self, button: str = "left") -> bool:
        """Press mouse button down"""
        pass
    
    @abstractmethod
    def mouse_up(self, button: str = "left") -> bool:
        """Release mouse button"""
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position"""
        pass 