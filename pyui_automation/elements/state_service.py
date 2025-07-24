"""
Element State Service - handles element state operations.

Responsible for:
- Getting element state
- Checking element properties
- Managing element state
"""
# Python imports
from typing import Optional, Dict, Any, TYPE_CHECKING
from logging import getLogger

# Local imports
if TYPE_CHECKING:
    from .base_element import BaseElement


class ElementStateService:
    """Service for element state operations"""
    
    def __init__(self, session: Any) -> None:
        """
        Initialize the ElementStateService.

        Args:
            session (Any): The session to use for the state service.
        """
        self._session = session
        self._logger = getLogger(__name__)
    
    def check(self, element: "BaseElement") -> None:
        """
        Check checkbox/radio button.

        Args:
            element (BaseElement): The element to check.
        """
        try:
            if not element.is_checked:
                element.click()
                self._logger.debug("Checked element")
            else:
                self._logger.debug("Element already checked")
        except Exception as e:
            self._logger.error(f"Failed to check element: {e}")
            raise
    
    def uncheck(self, element: "BaseElement") -> None:
        """
        Uncheck checkbox/radio button.

        Args:
            element (BaseElement): The element to uncheck.
        """
        try:
            if element.is_checked:
                element.click()
                self._logger.debug("Unchecked element")
            else:
                self._logger.debug("Element already unchecked")
        except Exception as e:
            self._logger.error(f"Failed to uncheck element: {e}")
            raise
    
    def toggle(self, element: "BaseElement") -> None:
        """
        Toggle checkbox/radio button state.

        Args:
            element (BaseElement): The element to toggle.
        """
        try:
            element.click()
            self._logger.debug("Toggled element state")
        except Exception as e:
            self._logger.error(f"Failed to toggle element: {e}")
            raise
    
    def expand(self, element: "BaseElement") -> None:
        """
        Expand expandable element.

        Args:
            element (BaseElement): The element to expand.
        """
        try:
            if not element.is_expanded:
                element.click()
                self._logger.debug("Expanded element")
            else:
                self._logger.debug("Element already expanded")
        except Exception as e:
            self._logger.error(f"Failed to expand element: {e}")
            raise
    
    def collapse(self, element: "BaseElement") -> None:
        """
        Collapse expandable element.

        Args:
            element (BaseElement): The element to collapse.
        """
        try:
            if element.is_expanded:
                element.click()
                self._logger.debug("Collapsed element")
            else:
                self._logger.debug("Element already collapsed")
        except Exception as e:
            self._logger.error(f"Failed to collapse element: {e}")
            raise
    
    def select_item(self, element: "BaseElement", item_text: str) -> None:
        """
        Select item from dropdown/list.

        Args:
            element (BaseElement): The element to select from.
            item_text (str): The text of the item to select.
        """
        try:
            # Find and click the item
            children = element.get_children()
            for child in children:
                if child.text == item_text:
                    child.click()
                    self._logger.debug(f"Selected item: {item_text}")
                    return
            
            self._logger.warning(f"Item not found: {item_text}")
        except Exception as e:
            self._logger.error(f"Failed to select item: {e}")
            raise
    
    def set_value(self, element: "BaseElement", value: str) -> None:
        """
        Set value of input element.

        Args:
            element (BaseElement): The element to set the value of.
            value (str): The value to set.
        """
        try:
            element.clear()
            element.send_keys(value)
            self._logger.debug(f"Set value: {value}")
        except Exception as e:
            self._logger.error(f"Failed to set value: {e}")
            raise
    
    def append_value(self, element: "BaseElement", value: str) -> None:
        """
        Append value to input element.

        Args:
            element (BaseElement): The element to append the value to.
            value (str): The value to append.
        """
        try:
            element.send_keys(value)
            self._logger.debug(f"Appended value: {value}")
        except Exception as e:
            self._logger.error(f"Failed to append value: {e}")
            raise
    
    def is_pressed(self, element: "BaseElement") -> bool:
        """
        Check if button is pressed.

        Args:
            element (BaseElement): The element to check.

        Returns:
            bool: True if element is pressed, False otherwise.
        """
        try:
            # Check for pressed state in properties
            pressed = element.get_property("IsPressed")
            if pressed is not None:
                return bool(pressed)
            
            # Fallback to checking if element is enabled and visible
            return element.is_enabled() and element.is_displayed()
        except Exception as e:
            self._logger.error(f"Failed to check if element is pressed: {e}")
            return False
    
    def is_selected(self, element: "BaseElement") -> bool:
        """
        Check if element is selected.

        Args:
            element (BaseElement): The element to check.

        Returns:
            bool: True if element is selected, False otherwise.
        """
        try:
            # Check for selected state in properties
            selected = element.get_property("IsSelected")
            if selected is not None:
                return bool(selected)
            
            # Fallback to checking if element is enabled and visible
            return element.is_enabled() and element.is_displayed()
        except Exception as e:
            self._logger.error(f"Failed to check if element is selected: {e}")
            return False
    
    def get_state_summary(self, element: "BaseElement") -> Dict[str, Any]:
        """
        Get summary of element state.

        Args:
            element (BaseElement): The element to get the state of.

        Returns:
            Dict[str, Any]: Summary of element state.
        """
        try:
            return {
                "enabled": element.is_enabled(),
                "visible": element.is_displayed(),
                "checked": element.is_checked,
                "expanded": element.is_expanded,
                "text": element.text,
                "value": element.value,
                "name": element.name,
                "control_type": element.control_type,
                "automation_id": element.automation_id,
                "class_name": element.class_name
            }
        except Exception as e:
            self._logger.error(f"Failed to get element state summary: {e}")
            return {} 