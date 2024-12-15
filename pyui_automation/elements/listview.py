from typing import Optional, Any, List
from .base import UIElement


class ListViewItem(UIElement):
    """Represents a list view item element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text of the item.

        Returns:
            str: Item text
        """
        return self._element.get_property("text")

    @property
    def is_selected(self) -> bool:
        """
        Check if the item is selected.

        Returns:
            bool: True if selected, False otherwise
        """
        return self._element.get_property("selected")

    @property
    def index(self) -> int:
        """
        Get the index of the item in the list.

        Returns:
            int: Item index
        """
        return self._element.get_property("index")

    def select(self) -> None:
        """Select the item if not already selected"""
        if not self.is_selected:
            self.click()

    def wait_until_selected(self, timeout: float = 10) -> bool:
        """
        Wait until the item becomes selected.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item became selected within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_selected,
            timeout=timeout,
            error_message="Item did not become selected"
        )


class ListView(UIElement):
    """Represents a list view control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def items(self) -> List[ListViewItem]:
        """
        Get all items in the list view.

        Returns:
            List[ListViewItem]: List of items
        """
        items = self._element.find_elements(by="type", value="listitem")
        return [ListViewItem(item, self._session) for item in items]

    @property
    def selected_items(self) -> List[ListViewItem]:
        """
        Get all selected items.

        Returns:
            List[ListViewItem]: List of selected items
        """
        items = self._element.find_elements(by="state", value="selected")
        return [ListViewItem(item, self._session) for item in items]

    @property
    def item_count(self) -> int:
        """
        Get the number of items in the list.

        Returns:
            int: Number of items
        """
        return len(self.items)

    def get_item(self, text: str) -> Optional[ListViewItem]:
        """
        Get an item by its text.

        Args:
            text (str): The text of the item to find

        Returns:
            Optional[ListViewItem]: Found item or None if not found
        """
        for item in self.items:
            if item.text == text:
                return item
        return None

    def get_item_by_index(self, index: int) -> Optional[ListViewItem]:
        """
        Get an item by its index.

        Args:
            index (int): The index of the item to find

        Returns:
            Optional[ListViewItem]: Found item or None if not found
        """
        if 0 <= index < self.item_count:
            items = self.items
            return items[index] if items else None
        return None

    def select_item(self, text: str) -> None:
        """
        Select an item by its text.

        Args:
            text (str): The text of the item to select

        Raises:
            ValueError: If item not found
        """
        item = self.get_item(text)
        if item:
            item.select()
        else:
            raise ValueError(f"Item '{text}' not found")

    def select_item_by_index(self, index: int) -> None:
        """
        Select an item by its index.

        Args:
            index (int): The index of the item to select

        Raises:
            ValueError: If index out of range
        """
        item = self.get_item_by_index(index)
        if item:
            item.select()
        else:
            raise ValueError(f"Item at index {index} not found")

    def select_multiple_items(self, texts: List[str]) -> None:
        """
        Select multiple items by their texts.

        Args:
            texts (List[str]): List of item texts to select
        """
        for text in texts:
            item = self.get_item(text)
            if item:
                # Hold Ctrl key for multiple selection
                with self._session.keyboard.hold_key("ctrl"):
                    item.select()

    def clear_selection(self) -> None:
        """Clear all selected items"""
        # Click on empty space in the list view
        self.click()

    def wait_until_item_count(self, count: int, timeout: float = 10) -> bool:
        """
        Wait until the list has a specific number of items.

        Args:
            count (int): Expected number of items
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item count matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.item_count == count,
            timeout=timeout,
            error_message=f"List did not have {count} items"
        )
