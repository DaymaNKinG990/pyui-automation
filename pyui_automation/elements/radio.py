from typing import Any, TYPE_CHECKING, List
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class RadioButton(UIElement):
    """Represents a radio button control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_selected(self) -> bool:
        """
        Check if the radio button is selected.

        Returns:
            bool: True if selected, False otherwise
        """
        return self._element.get_property("selected")

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        """Set selected state"""
        if value and not self.is_selected:
            self.click()

    @is_selected.deleter
    def is_selected(self):
        self._is_selected = False

    @property
    def group_name(self) -> str:
        """
        Get the name of the radio button group.

        Returns:
            str: Group name
        """
        return self._element.get_property("group_name")

    def select(self) -> None:
        """Select the radio button if not already selected"""
        if not self.is_selected:
            self.click()

    def get_group_buttons(self) -> List['RadioButton']:
        """
        Get all radio buttons in the same group.

        Returns:
            List[RadioButton]: List of radio buttons in the same group
        """
        buttons = self._element.find_elements(
            by="group",
            value=self.group_name
        )
        return [RadioButton(button, self._session) for button in buttons]

    def wait_until_selected(self, timeout: float = 10) -> bool:
        """
        Wait until the radio button becomes selected.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if radio button became selected within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_selected,
            timeout=timeout,
            error_message="Radio button did not become selected"
        )

    def wait_until_not_selected(self, timeout: float = 10) -> bool:
        """
        Wait until the radio button becomes not selected.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if radio button became not selected within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_selected,
            timeout=timeout,
            error_message="Radio button did not become unselected"
        )
