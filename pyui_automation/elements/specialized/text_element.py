"""
TextElement - specialized element for text interactions.

This element implements only the interfaces needed for text operations,
following the Interface Segregation Principle.
"""

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.session import AutomationSession

from ..base_element import BaseElement


class TextElement(BaseElement):
    """
    Specialized element for text interactions.
    
    Implements only the interfaces needed for text operations:
    - IElementProperties - for text identification and content
    - IElementGeometry - for text positioning
    - IElementState - for text visibility and selection
    - IElementScreenshot - for text screenshots
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """Initialize TextElement"""
        super().__init__(native_element, session)
    
    # Text-specific methods
    def get_text_content(self) -> str:
        """Get text content"""
        return self.text
    
    def is_text_visible(self) -> bool:
        """Check if text is visible"""
        return self.visible and self.is_displayed()
    
    def get_text_length(self) -> int:
        """Get text length"""
        return len(self.text)
    
    def is_text_empty(self) -> bool:
        """Check if text is empty"""
        return len(self.text.strip()) == 0
    
    def get_text_bounds(self) -> Dict[str, int]:
        """Get text bounds"""
        return self.rect
    
    def get_text_state(self) -> Dict[str, Any]:
        """Get text state summary"""
        return {
            'content': self.text,
            'length': len(self.text),
            'empty': self.is_text_empty(),
            'visible': self.is_text_visible(),
            'location': self.location,
            'size': self.size
        } 