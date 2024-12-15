from typing import Optional, Any
from .base import UIElement


class Text(UIElement):
    """Represents a text element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text content.

        Returns:
            str: Text content
        """
        return self._element.get_property("text")

    @property
    def is_editable(self) -> bool:
        """
        Check if the text is editable.

        Returns:
            bool: True if editable, False otherwise
        """
        return self._element.get_property("editable")

    @property
    def font_name(self) -> str:
        """
        Get the font name.

        Returns:
            str: Font name
        """
        return self._element.get_property("font_name")

    @property
    def font_size(self) -> float:
        """
        Get the font size.

        Returns:
            float: Font size
        """
        return self._element.get_property("font_size")

    @property
    def font_weight(self) -> str:
        """
        Get the font weight.

        Returns:
            str: Font weight (e.g., 'normal', 'bold')
        """
        return self._element.get_property("font_weight")

    @property
    def text_color(self) -> str:
        """
        Get the text color.

        Returns:
            str: Text color in hex format
        """
        return self._element.get_property("color")

    def set_text(self, text: str) -> None:
        """
        Set the text content if editable.

        Args:
            text (str): New text content

        Raises:
            ValueError: If text is not editable
        """
        if not self.is_editable:
            raise ValueError("Text element is not editable")
        self._element.set_property("text", text)

    def append_text(self, text: str) -> None:
        """
        Append text to the existing content if editable.

        Args:
            text (str): Text to append

        Raises:
            ValueError: If text is not editable
        """
        if not self.is_editable:
            raise ValueError("Text element is not editable")
        current_text = self.text
        self.set_text(current_text + text)

    def clear(self) -> None:
        """
        Clear the text content if editable.

        Raises:
            ValueError: If text is not editable
        """
        if not self.is_editable:
            raise ValueError("Text element is not editable")
        self.set_text("")

    def wait_until_text(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until the text content matches the specified text.

        Args:
            text (str): Text to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if text matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.text == text,
            timeout=timeout,
            error_message=f"Text did not become '{text}'"
        )

    def wait_until_contains(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until the text content contains the specified text.

        Args:
            text (str): Text to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if text was found within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: text in self.text,
            timeout=timeout,
            error_message=f"Text did not contain '{text}'"
        )
