"""
Input Service - handles all input operations.

Responsible for:
- Keyboard input
- Mouse input
- Input coordination
"""

from typing import Optional, List, Any
from logging import getLogger
import time

from ...input import Keyboard
from ...input.mouse import Mouse
from ..interfaces.iinput_service import IInputService


class InputService(IInputService):
    """Service for input operations"""
    
    def __init__(self, session: Any):
        self._session = session
        self._logger = getLogger(__name__)
        self._keyboard: Optional[Keyboard] = None
        self._mouse: Optional[Mouse] = None
    
    @property
    def keyboard(self) -> Keyboard:
        """Get keyboard instance"""
        if self._keyboard is None:
            # Get backend from session
            backend = self._session.backend if hasattr(self._session, 'backend') else None
            if backend is None:
                raise RuntimeError("Session backend is not available for keyboard input")
            self._keyboard = Keyboard(backend)
        return self._keyboard
    
    @property
    def mouse(self) -> Mouse:
        """Get mouse instance"""
        if self._mouse is None:
            # Get backend from session
            backend = self._session.backend if hasattr(self._session, 'backend') else None
            if backend is None:
                raise RuntimeError("Session backend is not available for mouse input")
            self._mouse = Mouse(backend)
        return self._mouse
    
    def press_key(self, key: str) -> None:
        """Press a key"""
        try:
            self.keyboard.press_key(key)
            self._logger.debug(f"Pressed key: {key}")
        except Exception as e:
            self._logger.error(f"Failed to press key {key}: {e}")
            raise
    
    def press_keys(self, *keys: str) -> None:
        """Press multiple keys"""
        try:
            self.keyboard.press_keys(*keys)
            self._logger.debug(f"Pressed keys: {keys}")
        except Exception as e:
            self._logger.error(f"Failed to press keys {keys}: {e}")
            raise
    
    def type_text(self, text: str, interval: Optional[float] = None) -> None:
        """Type text with optional interval between characters"""
        try:
            self.keyboard.type_text(text, interval or 0.0)
            self._logger.debug(f"Typed text: {text}")
        except Exception as e:
            self._logger.error(f"Failed to type text: {e}")
            raise
    
    def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        try:
            self.mouse.move(x, y)
            self._logger.debug(f"Mouse moved to ({x}, {y})")
        except Exception as e:
            self._logger.error(f"Failed to move mouse to ({x}, {y}): {e}")
            raise
    
    def mouse_click(self, x: int, y: int, button: str = "left") -> None:
        """Click mouse at coordinates"""
        try:
            self.mouse.click(x, y, button)
            self._logger.debug(f"Mouse clicked at ({x}, {y}) with {button} button")
        except Exception as e:
            self._logger.error(f"Failed to click mouse at ({x}, {y}): {e}")
            raise
    
    def mouse_double_click(self, x: int, y: int) -> None:
        """Double click mouse at coordinates"""
        try:
            self.mouse.double_click(x, y)
            self._logger.debug(f"Mouse double clicked at ({x}, {y})")
        except Exception as e:
            self._logger.error(f"Failed to double click mouse at ({x}, {y}): {e}")
            raise
    
    def mouse_right_click(self, x: int, y: int) -> None:
        """Right click mouse at coordinates"""
        try:
            self.mouse.right_click(x, y)
            self._logger.debug(f"Mouse right clicked at ({x}, {y})")
        except Exception as e:
            self._logger.error(f"Failed to right click mouse at ({x}, {y}): {e}")
            raise
    
    def mouse_drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Drag and drop from start to end coordinates"""
        try:
            self.mouse.drag(start_x, start_y, end_x, end_y)
            self._logger.debug(f"Mouse dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        except Exception as e:
            self._logger.error(f"Failed to drag and drop: {e}")
            raise
    
    def mouse_scroll(self, x: int, y: int, direction: str = "down", amount: int = 1) -> None:
        """Scroll mouse at coordinates"""
        try:
            self.mouse.scroll(x, y, direction, amount)
            self._logger.debug(f"Mouse scrolled at ({x}, {y}) {direction} {amount} times")
        except Exception as e:
            self._logger.error(f"Failed to scroll mouse: {e}")
            raise
    
    def hotkey(self, *keys: str) -> None:
        """Press hotkey combination"""
        try:
            self.keyboard.hotkey(*keys)
            self._logger.debug(f"Pressed hotkey: {'+'.join(keys)}")
        except Exception as e:
            self._logger.error(f"Failed to press hotkey {'+'.join(keys)}: {e}")
            raise
    
    def copy(self) -> None:
        """Copy selected text"""
        try:
            self.hotkey('ctrl', 'c')
            self._logger.debug("Copied text")
        except Exception as e:
            self._logger.error(f"Failed to copy: {e}")
            raise
    
    def paste(self) -> None:
        """Paste text"""
        try:
            self.hotkey('ctrl', 'v')
            self._logger.debug("Pasted text")
        except Exception as e:
            self._logger.error(f"Failed to paste: {e}")
            raise
    
    def select_all(self) -> None:
        """Select all text"""
        try:
            self.hotkey('ctrl', 'a')
            self._logger.debug("Selected all text")
        except Exception as e:
            self._logger.error(f"Failed to select all: {e}")
            raise
    
    def undo(self) -> None:
        """Undo last action"""
        try:
            self.hotkey('ctrl', 'z')
            self._logger.debug("Undid last action")
        except Exception as e:
            self._logger.error(f"Failed to undo: {e}")
            raise
    
    def redo(self) -> None:
        """Redo last action"""
        try:
            self.hotkey('ctrl', 'y')
            self._logger.debug("Redid last action")
        except Exception as e:
            self._logger.error(f"Failed to redo: {e}")
            raise
    
    def save(self) -> None:
        """Save (Ctrl+S)"""
        try:
            self.hotkey('ctrl', 's')
            self._logger.debug("Saved")
        except Exception as e:
            self._logger.error(f"Failed to save: {e}")
            raise
    
    def open(self) -> None:
        """Open (Ctrl+O)"""
        try:
            self.hotkey('ctrl', 'o')
            self._logger.debug("Opened")
        except Exception as e:
            self._logger.error(f"Failed to open: {e}")
            raise
    
    def new(self) -> None:
        """New (Ctrl+N)"""
        try:
            self.hotkey('ctrl', 'n')
            self._logger.debug("Created new")
        except Exception as e:
            self._logger.error(f"Failed to create new: {e}")
            raise
    
    def close(self) -> None:
        """Close (Ctrl+W or Alt+F4)"""
        try:
            self.hotkey('ctrl', 'w')
            self._logger.debug("Closed")
        except Exception as e:
            self._logger.error(f"Failed to close: {e}")
            raise
    
    def quit(self) -> None:
        """Quit (Alt+F4)"""
        try:
            self.hotkey('alt', 'f4')
            self._logger.debug("Quit")
        except Exception as e:
            self._logger.error(f"Failed to quit: {e}")
            raise 