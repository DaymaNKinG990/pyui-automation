from typing import Optional, Any, Union
from .base import UIElement


class Spinner(UIElement):
    """Represents a spinner/number input control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def value(self) -> Union[int, float]:
        """
        Get the current value.

        Returns:
            Union[int, float]: Current value
        """
        return self._element.get_property("value")

    @value.deleter
    def value(self):
        self._value = 0

    @property
    def minimum(self) -> Union[int, float]:
        """
        Get the minimum allowed value.

        Returns:
            Union[int, float]: Minimum value
        """
        return self._element.get_property("minimum")

    @property
    def maximum(self) -> Union[int, float]:
        """
        Get the maximum allowed value.

        Returns:
            Union[int, float]: Maximum value
        """
        return self._element.get_property("maximum")

    @property
    def step(self) -> Union[int, float]:
        """
        Get the step value.

        Returns:
            Union[int, float]: Step value
        """
        return self._element.get_property("step")

    @property
    def is_enabled(self) -> bool:
        """
        Check if the spinner is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        return self._element.get_property("enabled")

    def set_value(self, value: Union[int, float]) -> None:
        """
        Set the spinner value.

        Args:
            value (Union[int, float]): Value to set

        Raises:
            ValueError: If value out of range
        """
        if not self.minimum <= value <= self.maximum:
            raise ValueError(f"Value must be between {self.minimum} and {self.maximum}")
        self._element.set_property("value", value)

    def increment(self) -> None:
        """Increment the value by one step if not at maximum"""
        if self.value < self.maximum:
            new_value = min(self.value + self.step, self.maximum)
            self.set_value(new_value)

    def decrement(self) -> None:
        """Decrement the value by one step if not at minimum"""
        if self.value > self.minimum:
            new_value = max(self.value - self.step, self.minimum)
            self.set_value(new_value)

    def wait_until_value(self, value: Union[int, float], timeout: float = 10) -> bool:
        """
        Wait until the spinner reaches a specific value.

        Args:
            value (Union[int, float]): Value to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if value was reached within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: abs(self.value - value) < self.step,
            timeout=timeout,
            error_message=f"Spinner did not reach value {value}"
        )

    def wait_until_enabled(self, timeout: float = 10) -> bool:
        """
        Wait until the spinner becomes enabled.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if spinner became enabled within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_enabled,
            timeout=timeout,
            error_message="Spinner did not become enabled"
        )
