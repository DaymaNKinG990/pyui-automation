from typing import Optional, Any, List, TYPE_CHECKING
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class BreadcrumbItem(UIElement):
    """Represents a breadcrumb item element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the item text.

        Returns:
            str: Item text
        """
        return self._element.get_property("text")

    @property
    def is_current(self) -> bool:
        """
        Check if this is the current/active item.

        Returns:
            bool: True if current, False otherwise
        """
        return self._element.get_property("current")

    @property
    def url(self) -> Optional[str]:
        """
        Get the item URL if it's a link.

        Returns:
            Optional[str]: URL or None if not a link
        """
        return self._element.get_property("url")

    def click(self) -> None:
        """Click the breadcrumb item if it's a link"""
        url = self.url
        if url is not None and url != "":
            self._element.click()


class Breadcrumb(UIElement):
    """Represents a breadcrumb navigation element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def items(self) -> List[BreadcrumbItem]:
        """
        Get all breadcrumb items.

        Returns:
            List[BreadcrumbItem]: List of breadcrumb items
        """
        items = self._element.find_elements(by="type", value="breadcrumbitem")
        return [BreadcrumbItem(item, self._session) for item in items]

    @property
    def current_item(self) -> Optional['BreadcrumbItem']:
        item = self._element.find_element(by="state", value="current")
        if item is None:
            return None
        return BreadcrumbItem(item, self._session)

    @property
    def path(self) -> List[str]:
        """
        Get the full breadcrumb path as text.

        Returns:
            List[str]: List of item texts in order
        """
        return [item.text for item in self.items]

    def get_item(self, text: str) -> Optional[BreadcrumbItem]:
        """
        Get a breadcrumb item by its text.

        Args:
            text (str): Text of the item to find

        Returns:
            Optional[BreadcrumbItem]: Found item or None if not found
        """
        for item in self.items:
            if item.text == text:
                return item
        return None

    def navigate_to(self, text: str) -> None:
        """
        Navigate to a specific breadcrumb item by its text.

        Args:
            text (str): Text of the item to navigate to

        Raises:
            ValueError: If item not found
        """
        item = self.get_item(text)
        if item:
            item.click()
        else:
            raise ValueError(f"Breadcrumb item '{text}' not found")

    def wait_until_item_current(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until a specific item becomes current.

        Args:
            text (str): Text of the item to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item became current within timeout, False otherwise
        """
        def check_current():
            item = self.get_item(text)
            return item and item.is_current

        return self._session.wait_for_condition(
            check_current,
            timeout=timeout,
            error_message=f"Breadcrumb item '{text}' did not become current"
        )

    def wait_until_path(self, path: List[str], timeout: float = 10) -> bool:
        """
        Wait until the breadcrumb path matches expected value.

        Args:
            path (List[str]): Expected path as list of texts
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if path matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.path == path,
            timeout=timeout,
            error_message=f"Breadcrumb path did not become {path}"
        )
