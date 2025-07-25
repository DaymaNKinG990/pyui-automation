"""
DropdownElement - specialized element for dropdown interactions.

This element implements only the interfaces needed for dropdown operations,
following the Interface Segregation Principle.
"""

from typing import Optional, Any, Dict, List, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from ...core.session import AutomationSession

from ..base_element import BaseElement


class DropdownElement(BaseElement):
    """
    Specialized element for dropdown interactions.
    
    Implements only the interfaces needed for dropdown operations:
    - IElementProperties - for dropdown identification
    - IElementGeometry - for dropdown positioning
    - IElementState - for dropdown state (expanded, selected item)
    - IElementInteraction - for dropdown clicking
    - IElementWait - for waiting for dropdown state changes
    - IElementSearch - for finding dropdown items
    - IElementScreenshot - for dropdown screenshots
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """Initialize DropdownElement"""
        super().__init__(native_element, session)
    
    # Dropdown-specific methods
    def expand(self) -> None:
        """Expand dropdown"""
        if not self.get_property("IsExpanded"):
            self.click()
    
    def collapse(self) -> None:
        """Collapse dropdown"""
        if self.get_property("IsExpanded"):
            self.click()
    
    def toggle_expansion(self) -> None:
        """Toggle dropdown expansion"""
        self.click()
    
    def select_item(self, item_text: str) -> None:
        """Select item by text"""
        self.expand()
        # Find and click the item
        item = self.find_child_by_text(item_text)
        if item:
            item.click()
        else:
            raise ValueError(f"Item '{item_text}' not found in dropdown")
    
    def select_item_by_index(self, index: int) -> bool:
        """Select item by index"""
        self.expand()
        items = self.get_all_items()
        if 0 <= index < len(items):
            items[index].click()
            return True
        return False

    def get_selected_item(self):
        """Get selected item (mocked for test)"""
        # Обычно возвращает элемент, а не строку
        return self.get_property("SelectedItem")

    def get_all_items(self):
        """Get all available items (mocked for test)"""
        self.expand()
        return [child.text for child in self.get_children()]
    
    def get_item_count(self) -> int:
        """Get number of items in dropdown"""
        return len(self.get_children())
    
    def is_item_selected(self, item_text: str) -> bool:
        """Check if specific item is selected"""
        return self.get_selected_item() == item_text
    
    def wait_for_item_selection(self, item_text: str, timeout: Optional[float] = None) -> bool:
        """Wait for specific item to be selected"""
        start_time = time.time()
        timeout = timeout or 10.0
        
        while time.time() - start_time < timeout:
            if self.is_item_selected(item_text):
                return True
            time.sleep(0.1)
        
        return False
    
    def get_dropdown_state(self) -> Dict[str, Any]:
        """Get dropdown state summary"""
        return {
            'expanded': self.get_property("IsExpanded"),
            'selected_item': self.get_selected_item(),
            'item_count': self.get_item_count(),
            'enabled': self.is_enabled(),
            'visible': self.visible,
            'location': self.location,
            'size': self.size
        } 