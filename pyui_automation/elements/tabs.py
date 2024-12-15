from typing import Optional, Any, List
from .base import UIElement


class TabItem(UIElement):
    """Represents a tab item element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text of the tab.

        Returns:
            str: Tab text
        """
        return self._element.get_property("text")

    @property
    def is_selected(self) -> bool:
        """
        Check if the tab is selected.

        Returns:
            bool: True if selected, False otherwise
        """
        return self._element.get_property("selected")

    @property
    def is_enabled(self) -> bool:
        """
        Check if the tab is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        return self._element.get_property("enabled")

    def select(self) -> None:
        """Select the tab if not already selected"""
        if not self.is_selected and self.is_enabled:
            self.click()

    def wait_until_selected(self, timeout: float = 10) -> bool:
        """
        Wait until the tab becomes selected.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if tab became selected within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_selected,
            timeout=timeout,
            error_message="Tab did not become selected"
        )


class TabControl(UIElement):
    """Represents a tab control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def tabs(self) -> List[TabItem]:
        """
        Get all tabs in the control.

        Returns:
            List[TabItem]: List of tabs
        """
        tabs = self._element.find_elements(by="type", value="tabitem")
        return [TabItem(tab, self._session) for tab in tabs]

    @property
    def selected_tab(self) -> Optional[TabItem]:
        """
        Get the currently selected tab.

        Returns:
            Optional[TabItem]: Selected tab or None if none selected
        """
        tab = self._element.find_element(by="state", value="selected")
        return TabItem(tab, self._session) if tab else None

    def get_tab(self, text: str) -> Optional[TabItem]:
        """
        Get a tab by its text.

        Args:
            text (str): The text of the tab to find

        Returns:
            Optional[TabItem]: Found tab or None if not found
        """
        for tab in self.tabs:
            if tab.text == text:
                return tab
        return None

    def select_tab(self, text: str) -> None:
        """
        Select a tab by its text.

        Args:
            text (str): The text of the tab to select

        Raises:
            ValueError: If tab not found
        """
        tab = self.get_tab(text)
        if tab:
            tab.select()
        else:
            raise ValueError(f"Tab '{text}' not found")

    def wait_until_tab_selected(self, text: str, timeout: float = 10) -> bool:
        """
        Wait until a specific tab becomes selected.

        Args:
            text (str): The text of the tab to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if tab became selected within timeout, False otherwise
        """
        def check_tab():
            tab = self.get_tab(text)
            return tab and tab.is_selected

        return self._session.wait_for_condition(
            check_tab,
            timeout=timeout,
            error_message=f"Tab '{text}' did not become selected"
        )
