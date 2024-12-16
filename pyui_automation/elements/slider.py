from typing import Optional, Any
from .base import UIElement


class Slider(UIElement):
    """Represents a slider/progress bar control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def value(self) -> float:
        """
        Get the current value of the slider.

        Returns:
            float: Current value
        """
        return self._element.get_property("value")

    @value.deleter
    def value(self):
        self._value = 0

    @property
    def minimum(self) -> float:
        """
        Get the minimum value of the slider.

        Returns:
            float: Minimum value
        """
        return self._element.get_property("minimum")

    @property
    def maximum(self) -> float:
        """
        Get the maximum value of the slider.

        Returns:
            float: Maximum value
        """
        return self._element.get_property("maximum")

    @property
    def step(self) -> float:
        """
        Get the step value of the slider.

        Returns:
            float: Step value
        """
        return self._element.get_property("step")

    def set_value(self, value: float) -> None:
        """
        Set the slider to a specific value.

        Args:
            value (float): The value to set
        """
        if value < self.minimum or value > self.maximum:
            raise ValueError(f"Value must be between {self.minimum} and {self.maximum}")
        
        self._element.set_property("value", value)

    def increment(self) -> None:
        """Increment the slider value by one step"""
        new_value = min(self.value + self.step, self.maximum)
        self.set_value(new_value)

    def decrement(self) -> None:
        """Decrement the slider value by one step"""
        new_value = max(self.value - self.step, self.minimum)
        self.set_value(new_value)

    def wait_until_value(self, value: float, timeout: float = 10) -> bool:
        """
        Wait until the slider reaches a specific value.

        Args:
            value (float): The value to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if value was reached within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: abs(self.value - value) < self.step,
            timeout=timeout,
            error_message=f"Slider did not reach value {value}"
        )

    def wait_until_minimum(self, timeout: float = 10) -> bool:
        """
        Wait until the slider reaches its minimum value.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if minimum was reached within timeout, False otherwise
        """
        return self.wait_until_value(self.minimum, timeout)

    def wait_until_maximum(self, timeout: float = 10) -> bool:
        """
        Wait until the slider reaches its maximum value.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if maximum was reached within timeout, False otherwise
        """
        return self.wait_until_value(self.maximum, timeout)
