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

    @text.setter
    def text(self, value: str) -> None:
        """Set tooltip text"""
        self._element.set_property("text", value)

    @property
    def is_visible(self) -> bool:
        """
        Check if the tooltip is visible.

        Returns:
            bool: True if visible, False otherwise
        """
        return self._element.get_property("visible")

    @is_visible.setter
    def is_visible(self, value: bool) -> None:
        """Set tooltip visibility"""
        if value != self.is_visible:
            if value:
                self.show()
            else:
                self.hide()

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

    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        """Set tooltip position"""
        self._element.set_property("x", value[0])
        self._element.set_property("y", value[1])

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

    @size.setter
    def size(self, value: Tuple[int, int]) -> None:
        """Set tooltip size"""
        self._element.set_property("width", value[0])
        self._element.set_property("height", value[1])

    def show(self) -> None:
        """Show the tooltip"""
        if not self.is_visible:
            self._element.set_property("visible", True)

    def hide(self) -> None:
        """Hide the tooltip"""
        if self.is_visible:
            self._element.set_property("visible", False)

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
