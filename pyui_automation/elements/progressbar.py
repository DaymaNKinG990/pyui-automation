from typing import Optional, Any, Union
from .base import UIElement


class ProgressBar(UIElement):
    """Represents a progress bar control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def value(self) -> float:
        """
        Get the current progress value.

        Returns:
            float: Current value
        """
        return self._element.get_property("value")

    @property
    def minimum(self) -> float:
        """
        Get the minimum value.

        Returns:
            float: Minimum value
        """
        return self._element.get_property("minimum")

    @property
    def maximum(self) -> float:
        """
        Get the maximum value.

        Returns:
            float: Maximum value
        """
        return self._element.get_property("maximum")

    @property
    def percentage(self) -> float:
        """
        Get the progress percentage.

        Returns:
            float: Progress percentage (0-100)
        """
        if self.maximum == self.minimum:
            return 0.0
        return ((self.value - self.minimum) / (self.maximum - self.minimum)) * 100

    @property
    def is_indeterminate(self) -> bool:
        """
        Check if the progress bar is in indeterminate mode.

        Returns:
            bool: True if indeterminate, False otherwise
        """
        return self._element.get_property("indeterminate")

    @property
    def status_text(self) -> Optional[str]:
        """
        Get the status text if available.

        Returns:
            Optional[str]: Status text or None if not available
        """
        return self._element.get_property("status")

    def wait_until_complete(self, timeout: float = 10) -> bool:
        """
        Wait until progress reaches maximum value.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if progress completed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.value >= self.maximum,
            timeout=timeout,
            error_message="Progress did not complete"
        )

    def wait_until_value(self, value: float, timeout: float = 10) -> bool:
        """
        Wait until progress reaches a specific value.

        Args:
            value (float): Value to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if value was reached within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.value >= value,
            timeout=timeout,
            error_message=f"Progress did not reach value {value}"
        )

    def wait_until_percentage(self, percentage: float, timeout: float = 10) -> bool:
        """
        Wait until progress reaches a specific percentage.

        Args:
            percentage (float): Percentage to wait for (0-100)
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if percentage was reached within timeout, False otherwise
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
            
        return self._session.wait_for_condition(
            lambda: self.percentage >= percentage,
            timeout=timeout,
            error_message=f"Progress did not reach {percentage}%"
        )

    def wait_until_status(self, status: str, timeout: float = 10) -> bool:
        """
        Wait until status text matches expected value.

        Args:
            status (str): Status text to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if status matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.status_text == status,
            timeout=timeout,
            error_message=f"Status did not become '{status}'"
        )
