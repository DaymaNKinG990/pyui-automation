from typing import Optional, Any, List
from .base import UIElement


class Notification(UIElement):
    """Represents a notification/toast element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the notification text.

        Returns:
            str: Notification text
        """
        return self._element.get_property("text")

    @text.deleter
    def text(self):
        self._text = ""

    @property
    def type(self) -> str:
        """
        Get the notification type.

        Returns:
            str: Type (e.g., 'info', 'success', 'warning', 'error')
        """
        return self._element.get_property("type")

    @property
    def is_visible(self) -> bool:
        """
        Check if the notification is visible.

        Returns:
            bool: True if visible, False otherwise
        """
        return self._element.get_property("visible")
    
    @is_visible.deleter
    def is_visible(self):
        self._is_visible = False

    @property
    def auto_close(self) -> bool:
        """
        Check if the notification auto-closes.

        Returns:
            bool: True if auto-closes, False otherwise
        """
        return self._element.get_property("auto_close")

    @property
    def duration(self) -> Optional[float]:
        """
        Get the auto-close duration in seconds.

        Returns:
            Optional[float]: Duration in seconds or None if doesn't auto-close
        """
        return self._element.get_property("duration") if self.auto_close else None

    def close(self) -> None:
        """Close the notification manually"""
        close_button = self._element.find_element(by="name", value="Close")
        if close_button:
            close_button.click()

    def get_action_buttons(self) -> List[str]:
        """
        Get the text of all action buttons in the notification.

        Returns:
            List[str]: List of button texts
        """
        buttons = self._element.find_elements(by="type", value="button")
        return [button.get_property("text") for button in buttons]

    def click_action(self, text: str) -> None:
        """
        Click an action button by its text.

        Args:
            text (str): Text of the button to click

        Raises:
            ValueError: If button not found
        """
        button = self._element.find_element(by="name", value=text)
        if button:
            button.click()
        else:
            raise ValueError(f"Action button '{text}' not found")

    def wait_until_visible(self, timeout: float = 10) -> bool:
        """
        Wait until the notification becomes visible.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if notification became visible within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_visible,
            timeout=timeout,
            error_message="Notification did not become visible"
        )

    def wait_until_hidden(self, timeout: float = 10) -> bool:
        """
        Wait until the notification becomes hidden.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if notification became hidden within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_visible,
            timeout=timeout,
            error_message="Notification did not become hidden"
        )

    def wait_until_text(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until the notification text matches expected value.

        Args:
            text (str): Text to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if text matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.text == text,
            timeout=timeout,
            error_message=f"Notification text did not become '{text}'"
        )
