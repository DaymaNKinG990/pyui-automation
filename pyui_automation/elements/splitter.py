from typing import Optional, Any, List, Tuple
from .base import UIElement


class SplitterPanel(UIElement):
    """Represents a panel within a splitter"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get the panel size.

        Returns:
            Tuple[int, int]: (width, height) of panel
        """
        return (
            self._element.get_property("width"),
            self._element.get_property("height")
        )

    @property
    def min_size(self) -> Tuple[int, int]:
        """
        Get the minimum panel size.

        Returns:
            Tuple[int, int]: (min_width, min_height)
        """
        return (
            self._element.get_property("min_width"),
            self._element.get_property("min_height")
        )

    @property
    def max_size(self) -> Tuple[int, int]:
        """
        Get the maximum panel size.

        Returns:
            Tuple[int, int]: (max_width, max_height)
        """
        return (
            self._element.get_property("max_width"),
            self._element.get_property("max_height")
        )

    @property
    def is_collapsed(self) -> bool:
        """
        Check if the panel is collapsed.

        Returns:
            bool: True if collapsed, False otherwise
        """
        return self._element.get_property("collapsed")


class Splitter(UIElement):
    """Represents a splitter element for resizable panels"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def orientation(self) -> str:
        """
        Get the splitter orientation.

        Returns:
            str: 'horizontal' or 'vertical'
        """
        return self._element.get_property("orientation")

    @property
    def panels(self) -> List[SplitterPanel]:
        """
        Get all splitter panels.

        Returns:
            List[SplitterPanel]: List of panels
        """
        panels = self._element.find_elements(by="type", value="panel")
        return [SplitterPanel(panel, self._session) for panel in panels]

    @property
    def panel_count(self) -> int:
        """
        Get the number of panels.

        Returns:
            int: Number of panels
        """
        return len(self.panels)

    def get_panel_at(self, index: int) -> Optional[SplitterPanel]:
        """
        Get panel at specific index.

        Args:
            index (int): Panel index

        Returns:
            Optional[SplitterPanel]: Panel at index or None if invalid
        """
        panels = self.panels
        return panels[index] if 0 <= index < len(panels) else None

    def get_panel_sizes(self) -> List[Tuple[int, int]]:
        """
        Get sizes of all panels.

        Returns:
            List[Tuple[int, int]]: List of (width, height) tuples
        """
        return [panel.size for panel in self.panels]

    def resize_panel(self, index: int, size: int) -> None:
        """
        Resize a panel by dragging its splitter handle.

        Args:
            index (int): Panel index
            size (int): New size (width for vertical, height for horizontal)

        Raises:
            ValueError: If index invalid or size out of range
        """
        panel = self.get_panel_at(index)
        if not panel:
            raise ValueError(f"Invalid panel index: {index}")

        min_size = panel.min_size[0 if self.orientation == "vertical" else 1]
        max_size = panel.max_size[0 if self.orientation == "vertical" else 1]

        if not min_size <= size <= max_size:
            raise ValueError(f"Size {size} out of range [{min_size}, {max_size}]")

        handle = self._element.find_element(by="type", value=f"handle{index}")
        if handle:
            current_size = panel.size[0 if self.orientation == "vertical" else 1]
            delta = size - current_size
            
            # Simulate dragging the handle
            if self.orientation == "vertical":
                handle.drag_by(delta, 0)
            else:
                handle.drag_by(0, delta)

    def collapse_panel(self, index: int) -> None:
        """
        Collapse a panel.

        Args:
            index (int): Panel index

        Raises:
            ValueError: If index invalid
        """
        panel = self.get_panel_at(index)
        if not panel:
            raise ValueError(f"Invalid panel index: {index}")

        if not panel.is_collapsed:
            button = panel._element.find_element(by="type", value="collapse")
            if button:
                button.click()

    def expand_panel(self, index: int) -> None:
        """
        Expand a collapsed panel.

        Args:
            index (int): Panel index

        Raises:
            ValueError: If index invalid
        """
        panel = self.get_panel_at(index)
        if not panel:
            raise ValueError(f"Invalid panel index: {index}")

        if panel.is_collapsed:
            button = panel._element.find_element(by="type", value="expand")
            if button:
                button.click()

    def wait_until_panel_size(self, index: int, size: int, timeout: float = 10) -> bool:
        """
        Wait until panel reaches specific size.

        Args:
            index (int): Panel index
            size (int): Target size
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if size reached within timeout, False otherwise
        """
        panel = self.get_panel_at(index)
        if not panel:
            return False

        def check_size():
            current = panel.size[0 if self.orientation == "vertical" else 1]
            return abs(current - size) < 1

        return self._session.wait_for_condition(
            check_size,
            timeout=timeout,
            error_message=f"Panel {index} did not reach size {size}"
        )

    def wait_until_panel_collapsed(self, index: int, timeout: float = 10) -> bool:
        """
        Wait until panel becomes collapsed.

        Args:
            index (int): Panel index
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if collapsed within timeout, False otherwise
        """
        panel = self.get_panel_at(index)
        if not panel:
            return False

        return self._session.wait_for_condition(
            lambda: panel.is_collapsed,
            timeout=timeout,
            error_message=f"Panel {index} did not collapse"
        )

    def wait_until_panel_expanded(self, index: int, timeout: float = 10) -> bool:
        """
        Wait until panel becomes expanded.

        Args:
            index (int): Panel index
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if expanded within timeout, False otherwise
        """
        panel = self.get_panel_at(index)
        if not panel:
            return False

        return self._session.wait_for_condition(
            lambda: not panel.is_collapsed,
            timeout=timeout,
            error_message=f"Panel {index} did not expand"
        )
