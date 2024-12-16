from typing import Optional, Any, List
from .base import UIElement


class DropDown(UIElement):
    """Represents a dropdown/combobox control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_expanded(self) -> bool:
        """
        Check if the dropdown is expanded/opened.

        Returns:
            bool: True if expanded, False otherwise
        """
        return self._element.get_property("expanded")

    @is_expanded.setter
    def is_expanded(self, value: bool) -> None:
        """Set expanded state"""
        if value != self.is_expanded:
            self.click()

    @is_expanded.deleter
    def is_expanded(self) -> None:
        """Delete is not supported for this property"""
        raise AttributeError("Cannot delete is_expanded property")

    @property
    def selected_item(self) -> Optional[str]:
        """
        Get the currently selected item.

        Returns:
            Optional[str]: The selected item text or None if nothing is selected
        """
        return self._element.get_property("selected")

    @selected_item.setter
    def selected_item(self, value: str) -> None:
        """Select item by text"""
        self.select_item(value)

    @selected_item.deleter
    def selected_item(self) -> None:
        """Delete is not supported for this property"""
        raise AttributeError("Cannot delete selected_item property")

    @property
    def items(self) -> List[str]:
        """
        Get all items in the dropdown.

        Returns:
            List[str]: List of all item texts in the dropdown
        """
        return self._element.get_property("items")

    def expand(self) -> None:
        """Expand/open the dropdown if it's not already expanded"""
        if not self.is_expanded:
            self.click()

    def collapse(self) -> None:
        """Collapse/close the dropdown if it's expanded"""
        if self.is_expanded:
            self.click()

    def select_item(self, item_text: str) -> None:
        """
        Select an item by its text.

        Args:
            item_text (str): The text of the item to select
        """
        if not self.is_expanded:
            self.expand()
        
        item = self._session.find_element(
            by="name",
            value=item_text,
            parent=self._element
        )
        if item:
            item.click()
        else:
            raise ValueError(f"Item '{item_text}' not found in dropdown")

    def wait_until_expanded(self, timeout: float = 10) -> bool:
        """
        Wait until the dropdown becomes expanded.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if dropdown became expanded within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_expanded,
            timeout=timeout,
            error_message="Dropdown did not become expanded"
        )

    def wait_until_collapsed(self, timeout: float = 10) -> bool:
        """
        Wait until the dropdown becomes collapsed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if dropdown became collapsed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_expanded,
            timeout=timeout,
            error_message="Dropdown did not become collapsed"
        )

    def wait_until_item_selected(self, item_text: str, timeout: float = 10) -> bool:
        """
        Wait until a specific item becomes selected.

        Args:
            item_text (str): The text of the item to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item became selected within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.selected_item == item_text,
            timeout=timeout,
            error_message=f"Item '{item_text}' was not selected"
        )
