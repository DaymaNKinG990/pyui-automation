from typing import Optional, Any, Tuple
from .base import UIElement


class ScrollBar(UIElement):
    """Represents a scrollbar element for controlling scrollable content"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def orientation(self) -> str:
        """
        Get the scrollbar orientation.

        Returns:
            str: 'horizontal' or 'vertical'
        """
        return self._element.get_property("orientation")

    @property
    def value(self) -> float:
        """
        Get the current scroll position as a percentage (0-100).

        Returns:
            float: Current scroll position percentage
        """
        return self._element.get_property("value")

    @property
    def min_value(self) -> float:
        """
        Get the minimum scroll value.

        Returns:
            float: Minimum value (usually 0)
        """
        return self._element.get_property("min")

    @property
    def max_value(self) -> float:
        """
        Get the maximum scroll value.

        Returns:
            float: Maximum value (usually 100)
        """
        return self._element.get_property("max")

    @property
    def step_size(self) -> float:
        """
        Get the step size for small increments.

        Returns:
            float: Step size value
        """
        return self._element.get_property("step")

    @property
    def page_size(self) -> float:
        """
        Get the page size for large increments.

        Returns:
            float: Page size value
        """
        return self._element.get_property("page")

    @property
    def is_enabled(self) -> bool:
        """
        Check if the scrollbar is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        return self._element.get_property("enabled")

    @property
    def viewport_size(self) -> Tuple[int, int]:
        """
        Get the size of the viewport.

        Returns:
            Tuple[int, int]: (width, height) of viewport
        """
        viewport = self._element.find_element(by="type", value="viewport")
        if viewport:
            return (
                viewport.get_property("width"),
                viewport.get_property("height")
            )
        return (0, 0)

    def scroll_to(self, value: float) -> None:
        """
        Scroll to a specific position.

        Args:
            value (float): Position to scroll to (0-100)

        Raises:
            ValueError: If value is out of range
        """
        if not self.min_value <= value <= self.max_value:
            raise ValueError(f"Value {value} out of range [{self.min_value}, {self.max_value}]")
        self._element.set_property("value", value)

    def scroll_to_start(self) -> None:
        """Scroll to the start position"""
        self.scroll_to(self.min_value)

    def scroll_to_end(self) -> None:
        """Scroll to the end position"""
        self.scroll_to(self.max_value)

    def scroll_by(self, delta: float) -> None:
        """
        Scroll by a relative amount.

        Args:
            delta (float): Amount to scroll by (positive or negative)
        """
        new_value = max(self.min_value, min(self.max_value, self.value + delta))
        self.scroll_to(new_value)

    def scroll_step_forward(self) -> None:
        """Scroll forward by one step"""
        self.scroll_by(self.step_size)

    def scroll_step_backward(self) -> None:
        """Scroll backward by one step"""
        self.scroll_by(-self.step_size)

    def scroll_page_forward(self) -> None:
        """Scroll forward by one page"""
        self.scroll_by(self.page_size)

    def scroll_page_backward(self) -> None:
        """Scroll backward by one page"""
        self.scroll_by(-self.page_size)

    def is_at_start(self) -> bool:
        """
        Check if scrolled to start.

        Returns:
            bool: True if at start, False otherwise
        """
        return abs(self.value - self.min_value) < 0.001

    def is_at_end(self) -> bool:
        """
        Check if scrolled to end.

        Returns:
            bool: True if at end, False otherwise
        """
        return abs(self.value - self.max_value) < 0.001

    def wait_until_value(self, value: float, timeout: float = 10) -> bool:
        """
        Wait until scrollbar reaches specific value.

        Args:
            value (float): Value to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if value reached within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: abs(self.value - value) < 0.001,
            timeout=timeout,
            error_message=f"Scrollbar did not reach value {value}"
        )

    def wait_until_at_start(self, timeout: float = 10) -> bool:
        """
        Wait until scrolled to start.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if reached start within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            self.is_at_start,
            timeout=timeout,
            error_message="Scrollbar did not reach start"
        )

    def wait_until_at_end(self, timeout: float = 10) -> bool:
        """
        Wait until scrolled to end.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if reached end within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            self.is_at_end,
            timeout=timeout,
            error_message="Scrollbar did not reach end"
        )
