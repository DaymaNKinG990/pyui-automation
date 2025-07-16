from typing import Optional, Any, List, TYPE_CHECKING
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class AccordionPanel(UIElement):
    """Represents an individual accordion panel"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def header_text(self) -> str:
        """
        Get the panel header text.

        Returns:
            str: Header text
        """
        header = self._element.find_element(by="type", value="header")
        return header.get_property("text") if header else ""

    @property
    def content_text(self) -> str:
        """
        Get the panel content text.

        Returns:
            str: Content text
        """
        content = self._element.find_element(by="type", value="content")
        return content.get_property("text") if content else ""

    @property
    def is_expanded(self) -> bool:
        """Check if the panel is expanded."""
        try:
            return bool(self._element.get_property("expanded"))
        except Exception:
            return False

    def expand(self) -> None:
        """Expand the panel if it's collapsed"""
        if not self.is_expanded:
            header = self._element.find_element(by="type", value="header")
            if header:
                header.click()

    def collapse(self) -> None:
        """Collapse the panel if it's expanded"""
        if self.is_expanded:
            header = self._element.find_element(by="type", value="header")
            if header:
                header.click()

    def wait_until_expanded(self, timeout: float = 10) -> bool:
        """
        Wait until the panel becomes expanded.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if panel became expanded within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_expanded,
            timeout=timeout,
            error_message="Panel did not expand"
        )

    def wait_until_collapsed(self, timeout: float = 10) -> bool:
        """
        Wait until the panel becomes collapsed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if panel became collapsed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_expanded,
            timeout=timeout,
            error_message="Panel did not collapse"
        )


class Accordion(UIElement):
    """Represents an accordion container element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def panels(self) -> List[AccordionPanel]:
        """
        Get all accordion panels.

        Returns:
            List[AccordionPanel]: List of accordion panels
        """
        panels = self._element.find_elements(by="type", value="panel")
        return [AccordionPanel(panel, self._session) for panel in panels]

    @property
    def expanded_panels(self) -> List[AccordionPanel]:
        """
        Get all expanded panels.

        Returns:
            List[AccordionPanel]: List of expanded panels
        """
        return [panel for panel in self.panels if panel.is_expanded]

    def get_panel(self, header_text: str) -> Optional[AccordionPanel]:
        """
        Get a panel by its header text.

        Args:
            header_text (str): Header text to search for

        Returns:
            Optional[AccordionPanel]: Found panel or None if not found
        """
        for panel in self.panels:
            if panel.header_text == header_text:
                return panel
        return None

    def expand_panel(self, header_text: str) -> None:
        """
        Expand a panel by its header text.

        Args:
            header_text (str): Header text of panel to expand

        Raises:
            ValueError: If panel not found
        """
        panel = self.get_panel(header_text)
        if panel:
            panel.expand()
        else:
            raise ValueError(f"Panel with header '{header_text}' not found")

    def collapse_panel(self, header_text: str) -> None:
        """
        Collapse a panel by its header text.

        Args:
            header_text (str): Header text of panel to collapse

        Raises:
            ValueError: If panel not found
        """
        panel = self.get_panel(header_text)
        if panel:
            panel.collapse()
        else:
            raise ValueError(f"Panel with header '{header_text}' not found")

    def expand_all(self) -> None:
        """Expand all panels"""
        for panel in self.panels:
            panel.expand()

    def collapse_all(self) -> None:
        """Collapse all panels"""
        for panel in self.panels:
            panel.collapse()

    def wait_until_panel_expanded(self, header_text: str, timeout: float = 10) -> bool:
        """
        Wait until a specific panel becomes expanded.

        Args:
            header_text (str): Header text of panel to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if panel became expanded within timeout, False otherwise
        """
        panel = self.get_panel(header_text)
        if panel:
            return panel.wait_until_expanded(timeout)
        return False

    def wait_until_panel_collapsed(self, header_text: str, timeout: float = 10) -> bool:
        """
        Wait until a specific panel becomes collapsed.

        Args:
            header_text (str): Header text of panel to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if panel became collapsed within timeout, False otherwise
        """
        panel = self.get_panel(header_text)
        if panel:
            return panel.wait_until_collapsed(timeout)
        return False
