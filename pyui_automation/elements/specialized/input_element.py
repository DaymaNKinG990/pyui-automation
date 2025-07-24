"""
InputElement - specialized element for input field interactions.

This element implements only the interfaces needed for input operations,
following the Interface Segregation Principle.
"""

from typing import Optional, Any, Dict, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ...core.session import AutomationSession

from ...core.interfaces import IElementProperties, IElementGeometry, IElementState, IElementInteraction, IElementWait, IElementScreenshot
from ..base_element import BaseElement


class InputElement(BaseElement):
    """
    Specialized element for input field interactions.
    
    Implements only the interfaces needed for input operations:
    - IElementProperties - for input identification and value
    - IElementGeometry - for input positioning
    - IElementState - for input state (enabled, focused)
    - IElementInteraction - for input typing and clearing
    - IElementWait - for waiting for input state changes
    - IElementScreenshot - for input screenshots
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """Initialize InputElement"""
        super().__init__(native_element, session)
    
    # Input-specific methods
    def type_text(self, text: str, clear_first: bool = True) -> None:
        """Type text into input field"""
        if clear_first:
            self.clear()
        self.send_keys(text)
    
    def clear_and_type(self, text: str) -> None:
        """Clear input and type new text"""
        self.clear()
        self.send_keys(text)
    
    def append_text(self, text: str) -> None:
        """Append text to existing content"""
        self.append(text)
    
    def get_input_value(self) -> str:
        """Get input field value"""
        return self.value or ""
    
    def set_input_value(self, value: str) -> None:
        """Set input field value"""
        self.value = value
    
    def is_input_empty(self) -> bool:
        """Check if input field is empty"""
        return len(self.get_input_value().strip()) == 0
    
    def is_input_focused(self) -> bool:
        """Check if input field is focused"""
        return self.get_property("HasKeyboardFocus") or False
    
    def focus_input(self) -> None:
        """Focus on input field"""
        self.focus()
    
    def select_all_text(self) -> None:
        """Select all text in input field"""
        self.select_all()
    
    def copy_input_text(self) -> None:
        """Copy text from input field"""
        self.copy()
    
    def paste_to_input(self) -> None:
        """Paste text to input field"""
        self.paste()
    
    def wait_for_input_value(self, expected_value: str, timeout: Optional[float] = None) -> bool:
        """Wait for input value to match expected value"""
        return self.wait_until_value_is(expected_value, timeout)
    
    def get_input_state(self) -> Dict[str, Any]:
        """Get input field state summary"""
        return {
            'value': self.get_input_value(),
            'empty': self.is_input_empty(),
            'focused': self.is_input_focused(),
            'enabled': self.is_enabled(),
            'visible': self.visible,
            'location': self.location,
            'size': self.size
        } 