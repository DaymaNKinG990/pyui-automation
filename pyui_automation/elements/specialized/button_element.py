"""
ButtonElement - specialized element for button interactions.

This element implements only the interfaces needed for button operations,
following the Interface Segregation Principle.
"""

from typing import Optional, Any, Dict, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ...core.session import AutomationSession

from ...core.interfaces import IElementProperties, IElementGeometry, IElementState, IElementInteraction, IElementScreenshot
from ..base_element import BaseElement


class ButtonElement(BaseElement):
    """
    Specialized element for button interactions.
    
    Implements only the interfaces needed for button operations:
    - IElementProperties - for button identification
    - IElementGeometry - for button positioning
    - IElementState - for button state (pressed, enabled)
    - IElementInteraction - for button clicking
    - IElementScreenshot - for button screenshots
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """Initialize ButtonElement"""
        super().__init__(native_element, session)
    
    # Button-specific methods
    def is_pressed(self) -> bool:
        """Check if button is pressed"""
        return self.get_property("IsPressed") or False
    
    def click_and_wait(self, timeout: Optional[float] = None) -> bool:
        """Click button and wait for action to complete"""
        self.click()
        return self.wait_until_enabled(timeout)
    
    def double_click_and_wait(self, timeout: Optional[float] = None) -> bool:
        """Double click button and wait for action to complete"""
        self.double_click()
        return self.wait_until_enabled(timeout)
    
    def get_button_text(self) -> str:
        """Get button text"""
        return self.text
    
    def is_button_enabled(self) -> bool:
        """Check if button is enabled"""
        return self.is_enabled()
    
    def get_button_state(self) -> Dict[str, Any]:
        """Get button state summary"""
        return {
            'text': self.text,
            'enabled': self.is_enabled(),
            'visible': self.visible,
            'pressed': self.is_pressed(),
            'location': self.location,
            'size': self.size
        } 