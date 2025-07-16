from typing import Optional, Any, List, TYPE_CHECKING
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class Dialog(UIElement):
    """Represents a dialog/modal window element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def title(self) -> str:
        """
        Get the dialog title.

        Returns:
            str: Dialog title
        """
        return self._element.get_property("title")

    @property
    def is_modal(self) -> bool:
        """
        Check if the dialog is modal.

        Returns:
            bool: True if modal, False otherwise
        """
        return self._element.get_property("modal")

    @property
    def is_visible(self) -> bool:
        """
        Check if the dialog is visible.

        Returns:
            bool: True if visible, False otherwise
        """
        return self._element.get_property("visible")

    @is_visible.deleter
    def is_visible(self):
        self._is_visible = False

    @property
    def buttons(self) -> List[str]:
        """
        Get the text of all buttons in the dialog.

        Returns:
            List[str]: List of button texts
        """
        buttons = self._element.find_elements(by="type", value="button")
        return [button.get_property("text") for button in buttons]

    def click_button(self, text: str) -> None:
        """
        Click a button by its text.

        Args:
            text (str): Text of the button to click

        Raises:
            ValueError: If button not found
        """
        button = self._element.find_element(by="name", value=text)
        if button:
            button.click()
        else:
            raise ValueError(f"Button '{text}' not found")

    def close(self) -> None:
        """Close the dialog using the close button or X icon"""
        close_button = self._element.find_element_by_object_name("Close")
        if close_button:
            close_button.click()

    def get_content_text(self) -> str:
        """
        Get the text content of the dialog.

        Returns:
            str: Dialog content text
        """
        content = self._element.find_element_by_widget_type("content")
        return content.get_property("text") if content else ""

    def get_message(self) -> Optional[str]:
        """
        Get the message text if this is a message dialog.

        Returns:
            Optional[str]: Message text or None if not a message dialog
        """
        message = self._element.find_element_by_widget_type("message")
        return message.get_property("text") if message else None

    def wait_until_open(self, timeout: float = 10) -> bool:
        """
        Wait until the dialog becomes visible.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if dialog became visible within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_visible,
            timeout=timeout,
            error_message="Dialog did not open"
        )

    def wait_until_closed(self, timeout: float = 10) -> bool:
        """
        Wait until the dialog becomes hidden.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if dialog became hidden within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_visible,
            timeout=timeout,
            error_message="Dialog did not close"
        )

    def wait_until_button_enabled(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until a specific button becomes enabled.

        Args:
            text (str): Text of the button to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if button became enabled within timeout, False otherwise
        """
        def check_button():
            button = self._element.find_element(by="name", value=text)
            return button and button.get_property("enabled")

        return self._session.wait_for_condition(
            check_button,
            timeout=timeout,
            error_message=f"Button '{text}' did not become enabled"
        )
