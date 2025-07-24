"""
CheckboxElement - specialized element for checkbox interactions.

This element implements only the interfaces needed for checkbox operations,
following the Interface Segregation Principle.
"""

from typing import Optional, Any, Dict, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ...core.session import AutomationSession

from ...core.interfaces import IElementProperties, IElementGeometry, IElementState, IElementInteraction, IElementWait, IElementScreenshot
from ..base_element import BaseElement


class CheckboxElement(BaseElement):
    """
    Specialized element for checkbox interactions.
    
    Implements only the interfaces needed for checkbox operations:
    - IElementProperties - for checkbox identification
    - IElementGeometry - for checkbox positioning
    - IElementState - for checkbox checked state
    - IElementInteraction - for checkbox clicking
    - IElementWait - for waiting for checkbox state changes
    - IElementScreenshot - for checkbox screenshots
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """Initialize CheckboxElement"""
        super().__init__(native_element, session)
    
    # Checkbox-specific methods
    def check(self) -> None:
        """Check the checkbox"""
        if not self.is_checked:
            self.click()
    
    def uncheck(self) -> None:
        """Uncheck the checkbox"""
        if self.is_checked:
            self.click()
    
    def toggle(self) -> None:
        """Toggle checkbox state"""
        self.click()
    
    def get_checkbox_state(self) -> bool:
        """Check if checkbox is checked"""
        return self.get_property("IsChecked") or False
    
    def wait_until_checked(self, timeout: float = 10) -> bool:
        """Wait until checkbox is checked"""
        return self.wait_until_checked(timeout)
    
    def wait_until_unchecked(self, timeout: float = 10) -> bool:
        """Wait until checkbox is unchecked"""
        return self.wait_until_unchecked(timeout)
    
    def get_checkbox_state(self) -> Dict[str, Any]:
        """Get checkbox state summary"""
        return {
            'checked': self.is_checked,
            'enabled': self.is_enabled(),
            'visible': self.visible,
            'location': self.location,
            'size': self.size
        } 