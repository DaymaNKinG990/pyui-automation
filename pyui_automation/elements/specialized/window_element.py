"""
WindowElement - specialized element for window interactions.

This element implements only the interfaces needed for window operations,
following the Interface Segregation Principle.
"""

from typing import Optional, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.session import AutomationSession

from ..base_element import BaseElement


class WindowElement(BaseElement):
    """
    Specialized element for window interactions.
    
    Implements only the interfaces needed for window operations:
    - IElementProperties - for window identification
    - IElementGeometry - for window positioning and size
    - IElementState - for window state (visible, active)
    - IElementInteraction - for window clicking and focus
    - IElementSearch - for finding window elements
    - IElementScreenshot - for window screenshots
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """Initialize WindowElement"""
        super().__init__(native_element, session)
    
    # Window-specific methods
    def get_window_title(self) -> str:
        """Get window title"""
        return self.text
    
    def get_window_bounds(self) -> Dict[str, int]:
        """Get window bounds"""
        return self.rect
    
    def get_window_size(self) -> Dict[str, int]:
        """Get window size"""
        return self.size
    
    def get_window_position(self) -> Dict[str, int]:
        """Get window position"""
        return self.location
    
    def is_window_active(self) -> bool:
        """Check if window is active"""
        return self.get_property("IsKeyboardFocusable") or False
    
    def is_window_maximized(self) -> bool:
        """Check if window is maximized"""
        return self.get_property("IsMaximized") or False
    
    def is_window_minimized(self) -> bool:
        """Check if window is minimized"""
        return self.get_property("IsMinimized") or False
    
    def activate_window(self) -> None:
        """Activate window (bring to front)"""
        self.focus()
    
    def close_window(self) -> None:
        """Close window"""
        # Find close button and click it
        close_button = self.find_child_by_name("Close") or self.find_child_by_name("X")
        if close_button:
            close_button.click()
        else:
            # Fallback: send Alt+F4
            self.session.input_service.hotkey("alt", "f4")
    
    def maximize_window(self) -> None:
        """Maximize window"""
        if not self.is_window_maximized():
            maximize_button = self.find_child_by_name("Maximize")
            if maximize_button:
                maximize_button.click()
    
    def minimize_window(self) -> None:
        """Minimize window"""
        if not self.is_window_minimized():
            minimize_button = self.find_child_by_name("Minimize")
            if minimize_button:
                minimize_button.click()
    
    def resize_window(self, width: int, height: int) -> None:
        """Resize window"""
        # This would require platform-specific implementation
        # For now, just log the intention
        # Log resize intention (logger not available in this context)
        pass
    
    def move_window(self, x: int, y: int) -> None:
        """Move window to position"""
        # This would require platform-specific implementation
        # For now, just log the intention
        # Log move intention (logger not available in this context)
        pass
    
    def get_window_elements(self) -> list:
        """Get all elements in window"""
        return self.get_children()
    
    def find_element_in_window(self, element_name: str) -> Optional['BaseElement']:
        """Find element by name in window"""
        element = self.find_child_by_name(element_name)
        if element is not None and isinstance(element, BaseElement):
            return element
        return None
    
    def get_window_state(self) -> Dict[str, Any]:
        """Get window state summary"""
        return {
            'title': self.get_window_title(),
            'active': self.is_window_active(),
            'maximized': self.is_window_maximized(),
            'minimized': self.is_window_minimized(),
            'visible': self.visible,
            'enabled': self.is_enabled(),
            'bounds': self.get_window_bounds(),
            'size': self.get_window_size(),
            'position': self.get_window_position()
        } 