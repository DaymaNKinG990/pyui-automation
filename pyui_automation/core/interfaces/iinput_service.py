"""
IInputService interface - defines contract for input service.

Responsible for:
- Keyboard input
- Mouse input
- Input coordination
"""

from abc import ABC, abstractmethod
from typing import Optional


class IInputService(ABC):
    """Interface for input service"""
    
    @abstractmethod
    def press_key(self, key: str) -> None:
        """Press a key"""
        pass
    
    @abstractmethod
    def press_keys(self, *keys: str) -> None:
        """Press multiple keys"""
        pass
    
    @abstractmethod
    def type_text(self, text: str, interval: Optional[float] = None) -> None:
        """Type text with optional interval between characters"""
        pass
    
    @abstractmethod
    def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        pass
    
    @abstractmethod
    def mouse_click(self, x: int, y: int, button: str = "left") -> None:
        """Click mouse at coordinates"""
        pass
    
    @abstractmethod
    def mouse_double_click(self, x: int, y: int) -> None:
        """Double click mouse at coordinates"""
        pass
    
    @abstractmethod
    def mouse_right_click(self, x: int, y: int) -> None:
        """Right click mouse at coordinates"""
        pass
    
    @abstractmethod
    def mouse_drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Drag and drop from start to end coordinates"""
        pass
    
    @abstractmethod
    def mouse_scroll(self, x: int, y: int, direction: str = "down", amount: int = 1) -> None:
        """Scroll mouse at coordinates"""
        pass
    
    @abstractmethod
    def hotkey(self, *keys: str) -> None:
        """Press hotkey combination"""
        pass
    
    @abstractmethod
    def copy(self) -> None:
        """Copy selected text"""
        pass
    
    @abstractmethod
    def paste(self) -> None:
        """Paste text"""
        pass
    
    @abstractmethod
    def select_all(self) -> None:
        """Select all text"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo last action"""
        pass
    
    @abstractmethod
    def redo(self) -> None:
        """Redo last action"""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Save (Ctrl+S)"""
        pass
    
    @abstractmethod
    def open(self) -> None:
        """Open (Ctrl+O)"""
        pass
    
    @abstractmethod
    def new(self) -> None:
        """New (Ctrl+N)"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close (Ctrl+W)"""
        pass
    
    @abstractmethod
    def quit(self) -> None:
        """Quit (Alt+F4)"""
        pass 