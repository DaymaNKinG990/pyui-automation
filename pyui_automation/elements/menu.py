from typing import Optional, Any, List
from .base import UIElement


class MenuItem(UIElement):
    """Represents a menu item element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text of the menu item.

        Returns:
            str: Menu item text
        """
        return self._element.get_property("text")

    @property
    def is_enabled(self) -> bool:
        """
        Check if the menu item is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        return self._element.get_property("enabled")

    @property
    def has_submenu(self) -> bool:
        """
        Check if the menu item has a submenu.

        Returns:
            bool: True if has submenu, False otherwise
        """
        return self._element.get_property("has_submenu")

    def expand(self) -> None:
        """Expand the submenu if it exists"""
        if self.has_submenu:
            self.hover()

    def select(self) -> None:
        """Select/click the menu item"""
        self.click()


class Menu(UIElement):
    """Represents a menu control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_open(self) -> bool:
        """
        Check if the menu is open.

        Returns:
            bool: True if open, False otherwise
        """
        return self._element.get_property("expanded")

    @property
    def items(self) -> List[MenuItem]:
        """
        Get all menu items.

        Returns:
            List[MenuItem]: List of menu items
        """
        items = self._element.find_elements(by="type", value="menuitem")
        return [MenuItem(item, self._session) for item in items]

    def open(self) -> None:
        """Open the menu if it's not already open"""
        if not self.is_open:
            self.click()

    def close(self) -> None:
        """Close the menu if it's open"""
        if self.is_open:
            # Send escape key to close menu
            self._session.keyboard.press_key("escape")

    def get_item(self, text: str) -> Optional[MenuItem]:
        """
        Get a menu item by its text.

        Args:
            text (str): The text of the menu item to find

        Returns:
            Optional[MenuItem]: The found menu item or None if not found
        """
        for item in self.items:
            if item.text == text:
                return item
        return None

    def select_item(self, text: str) -> None:
        """
        Select a menu item by its text.

        Args:
            text (str): The text of the menu item to select

        Raises:
            ValueError: If menu item not found
        """
        item = self.get_item(text)
        if item:
            item.select()
        else:
            raise ValueError(f"Menu item '{text}' not found")

    def wait_until_open(self, timeout: float = 10) -> bool:
        """
        Wait until the menu becomes open.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if menu became open within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_open,
            timeout=timeout,
            error_message="Menu did not become open"
        )

    def wait_until_closed(self, timeout: float = 10) -> bool:
        """
        Wait until the menu becomes closed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if menu became closed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_open,
            timeout=timeout,
            error_message="Menu did not become closed"
        )
