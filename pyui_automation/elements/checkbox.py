from typing import Any, TYPE_CHECKING
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class CheckBox(UIElement):
    """Represents a checkbox control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_checked(self) -> bool:
        """
        Check if the checkbox is checked.

        Returns:
            bool: True if checked, False otherwise
        """
        return self._element.get_property("checked")

    @is_checked.setter
    def is_checked(self, value: bool) -> None:
        """Set the checked state of the checkbox"""
        if value != self.is_checked:
            self.click()

    @is_checked.deleter
    def is_checked(self) -> None:
        """Delete is not supported for this property"""
        raise AttributeError("Cannot delete is_checked property")

    def check(self) -> None:
        """Check the checkbox if it's not already checked"""
        if not self.is_checked:
            self.click()

    def uncheck(self) -> None:
        """Uncheck the checkbox if it's checked"""
        if self.is_checked:
            self.click()

    def toggle(self) -> None:
        """Toggle the checkbox state"""
        self.click()

    def wait_until_checked(self, timeout: float = 10) -> bool:
        """
        Wait until the checkbox becomes checked.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if checkbox became checked within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_checked,
            timeout=timeout,
            error_message="Checkbox did not become checked"
        )

    def wait_until_unchecked(self, timeout: float = 10) -> bool:
        """
        Wait until the checkbox becomes unchecked.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if checkbox became unchecked within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_checked,
            timeout=timeout,
            error_message="Checkbox did not become unchecked"
        )
