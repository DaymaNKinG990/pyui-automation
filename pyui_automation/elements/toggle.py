from typing import Optional, Any
from .base import UIElement


class Toggle(UIElement):
    """Represents a toggle switch control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)
        self._is_on = self._element.get_property("toggled")
        self._is_enabled = self._element.get_property("enabled")

    @property
    def is_on(self):
        return self._is_on

    @is_on.setter
    def is_on(self, value):
        self._is_on = value

    @is_on.deleter
    def is_on(self):
        self._is_on = False

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        self._is_enabled = value

    @is_enabled.deleter
    def is_enabled(self):
        self._is_enabled = False

    @property
    def label(self) -> str:
        """
        Get the label text of the toggle.

        Returns:
            str: Label text
        """
        return self._element.get_property("label")

    def toggle(self) -> None:
        """Toggle the switch state between ON and OFF"""
        if self.is_enabled:
            self.click()

    def turn_on(self) -> None:
        """Turn the toggle ON if it's not already ON"""
        if self.is_enabled and not self.is_on:
            self.click()

    def turn_off(self) -> None:
        """Turn the toggle OFF if it's not already OFF"""
        if self.is_enabled and self.is_on:
            self.click()

    def wait_until_on(self, timeout: float = 10) -> bool:
        """
        Wait until the toggle is in the ON state.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if toggle became ON within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_on,
            timeout=timeout,
            error_message="Toggle did not turn ON"
        )

    def wait_until_off(self, timeout: float = 10) -> bool:
        """
        Wait until the toggle is in the OFF state.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if toggle became OFF within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_on,
            timeout=timeout,
            error_message="Toggle did not turn OFF"
        )

    def wait_until_enabled(self, timeout: float = 10) -> bool:
        """
        Wait until the toggle becomes enabled.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if toggle became enabled within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_enabled,
            timeout=timeout,
            error_message="Toggle did not become enabled"
        )
