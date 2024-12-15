from typing import Optional, Any, Tuple
from .base import UIElement


class Tooltip(UIElement):
    """Represents a tooltip element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the tooltip text.

        Returns:
            str: Tooltip text
        """
        return self._element.get_property("text")

    @property
    def is_visible(self) -> bool:
        """
        Check if the tooltip is visible.

        Returns:
            bool: True if visible, False otherwise
        """
        return self._element.get_property("visible")

    @property
    def position(self) -> Tuple[int, int]:
        """
        Get the tooltip position.

        Returns:
            Tuple[int, int]: X and Y coordinates
        """
        return (
            self._element.get_property("x"),
            self._element.get_property("y")
        )

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get the tooltip size.

        Returns:
            Tuple[int, int]: Width and height
        """
        return (
            self._element.get_property("width"),
            self._element.get_property("height")
        )

    def wait_until_visible(self, timeout: float = 10) -> bool:
        """
        Wait until the tooltip becomes visible.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if tooltip became visible within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_visible,
            timeout=timeout,
            error_message="Tooltip did not become visible"
        )

    def wait_until_hidden(self, timeout: float = 10) -> bool:
        """
        Wait until the tooltip becomes hidden.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if tooltip became hidden within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_visible,
            timeout=timeout,
            error_message="Tooltip did not become hidden"
        )

    def wait_until_text(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until the tooltip text matches expected value.

        Args:
            text (str): Text to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if text matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.text == text,
            timeout=timeout,
            error_message=f"Tooltip text did not become '{text}'"
        )
