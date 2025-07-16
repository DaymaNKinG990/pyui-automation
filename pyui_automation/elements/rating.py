from typing import Any, TYPE_CHECKING
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class Rating(UIElement):
    """Represents a rating control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)
        self._value = self._element.get_property("value")
        self._readonly = self._element.get_property("readonly")
        self.mouse = session.mouse

    def click_at_offset(self, x: int, y: int):
        """Click at specific offset"""
        self.mouse.click_at_offset(self, x, y)

    def hover_at_offset(self, x: int, y: int):
        """Hover at specific offset"""
        self.mouse.hover_at_offset(self, x, y)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @value.deleter
    def value(self):
        self._value = 0

    @property
    def is_readonly(self):
        return self._readonly

    @is_readonly.setter
    def is_readonly(self, val):
        self._readonly = val

    @is_readonly.deleter
    def is_readonly(self):
        self._readonly = True

    @property
    def maximum(self) -> int:
        """
        Get the maximum rating value.

        Returns:
            int: Maximum value (usually 5)
        """
        return self._element.get_property("maximum")

    @property
    def allows_half_stars(self) -> bool:
        """
        Check if half-star ratings are allowed.

        Returns:
            bool: True if half-stars allowed, False otherwise
        """
        return self._element.get_property("half_stars")

    def set_rating(self, value: float) -> None:
        """
        Set the rating value.

        Args:
            value (float): Rating value to set

        Raises:
            ValueError: If value out of range or half-stars not allowed
        """
        if value < 0 or value > self.maximum:
            raise ValueError(f"Rating must be between 0 and {self.maximum}")
        
        if not self.allows_half_stars and not value.is_integer():
            raise ValueError("Half-star ratings are not allowed")

        if not self.is_readonly:
            # Calculate the position to click based on the value
            star_width = self._element.get_property("star_width")
            x_offset = int(value * star_width)
            self.click_at_offset(x_offset, 0)

    def clear(self) -> None:
        """Clear the rating (set to 0) if not read-only"""
        if not self.is_readonly:
            self.set_rating(0)

    def hover_rating(self, value: float) -> None:
        """
        Hover over a specific rating value.

        Args:
            value (float): Rating value to hover over

        Raises:
            ValueError: If value out of range
        """
        if value < 0 or value > self.maximum:
            raise ValueError(f"Rating must be between 0 and {self.maximum}")

        # Calculate the position to hover based on the value
        star_width = self._element.get_property("star_width")
        x_offset = int(value * star_width)
        self.hover_at_offset(x_offset, 0)

    def wait_until_value(self, value: float, timeout: float = 10) -> bool:
        """
        Wait until rating reaches a specific value.

        Args:
            value (float): Rating value to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if rating matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: abs(self.value - value) < 0.1,
            timeout=timeout,
            error_message=f"Rating did not become {value}"
        )

    def wait_until_interactive(self, timeout: float = 10) -> bool:
        """
        Wait until rating becomes interactive (not read-only).

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if rating became interactive within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_readonly,
            timeout=timeout,
            error_message="Rating did not become interactive"
        )
