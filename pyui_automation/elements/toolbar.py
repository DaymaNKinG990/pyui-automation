from typing import Optional, Any, List
from .base import UIElement


class ToolbarButton(UIElement):
    """Represents a toolbar button element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text of the button.

        Returns:
            str: Button text
        """
        return self._element.get_property("text")

    @property
    def tooltip(self) -> str:
        """
        Get the tooltip text.

        Returns:
            str: Tooltip text
        """
        return self._element.get_property("tooltip")

    @property
    def is_enabled(self) -> bool:
        """
        Check if the button is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        return self._element.get_property("enabled")

    @property
    def is_pressed(self) -> bool:
        """
        Check if the button is pressed (for toggle buttons).

        Returns:
            bool: True if pressed, False otherwise
        """
        return self._element.get_property("pressed")

    def click(self) -> None:
        """Click the button if enabled"""
        if self.is_enabled:
            super().click()

    def wait_until_enabled(self, timeout: float = 10) -> bool:
        """
        Wait until the button becomes enabled.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if button became enabled within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_enabled,
            timeout=timeout,
            error_message="Button did not become enabled"
        )


class Toolbar(UIElement):
    """Represents a toolbar control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def buttons(self) -> List[ToolbarButton]:
        """
        Get all buttons in the toolbar.

        Returns:
            List[ToolbarButton]: List of toolbar buttons
        """
        buttons = self._element.find_elements(by="type", value="button")
        return [ToolbarButton(button, self._session) for button in buttons]

    def get_button(self, text: str) -> Optional[ToolbarButton]:
        """
        Get a button by its text.

        Args:
            text (str): The text of the button to find

        Returns:
            Optional[ToolbarButton]: Found button or None if not found
        """
        for button in self.buttons:
            if button.text == text:
                return button
        return None

    def get_button_by_tooltip(self, tooltip: str) -> Optional[ToolbarButton]:
        """
        Get a button by its tooltip text.

        Args:
            tooltip (str): The tooltip text of the button to find

        Returns:
            Optional[ToolbarButton]: Found button or None if not found
        """
        for button in self.buttons:
            if button.tooltip == tooltip:
                return button
        return None

    def click_button(self, text: str) -> None:
        """
        Click a button by its text.

        Args:
            text (str): The text of the button to click

        Raises:
            ValueError: If button not found
        """
        button = self.get_button(text)
        if button:
            button.click()
        else:
            raise ValueError(f"Button '{text}' not found")

    def click_button_by_tooltip(self, tooltip: str) -> None:
        """
        Click a button by its tooltip text.

        Args:
            tooltip (str): The tooltip text of the button to click

        Raises:
            ValueError: If button not found
        """
        button = self.get_button_by_tooltip(tooltip)
        if button:
            button.click()
        else:
            raise ValueError(f"Button with tooltip '{tooltip}' not found")
