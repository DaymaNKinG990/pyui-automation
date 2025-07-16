from typing import Any, TYPE_CHECKING, Tuple, Dict
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class HealthBar(UIElement):
    """Represents a health/HP bar element commonly found in games"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def current_health(self) -> float:
        """
        Get the current health value.

        Returns:
            float: Current health value
        """
        return self._element.get_property("value")

    @property
    def max_health(self) -> float:
        """
        Get the maximum health value.

        Returns:
            float: Maximum health value
        """
        return self._element.get_property("max_value")

    @property
    def health_percentage(self) -> float:
        """
        Get health as percentage.

        Returns:
            float: Health percentage (0-100)
        """
        if self.max_health > 0:
            return (self.current_health / self.max_health) * 100
        return 0.0

    @property
    def color(self) -> Tuple[int, int, int]:
        """
        Get the health bar color (RGB).

        Returns:
            Tuple[int, int, int]: RGB color values
        """
        return (
            self._element.get_property("color_r"),
            self._element.get_property("color_g"),
            self._element.get_property("color_b")
        )

    @property
    def is_critical(self) -> bool:
        """
        Check if health is at critical level (usually <25%).

        Returns:
            bool: True if critical, False otherwise
        """
        return self.health_percentage <= 25.0

    def wait_until_health_above(self, threshold: float, timeout: float = 10) -> bool:
        """
        Wait until health rises above threshold.

        Args:
            threshold (float): Health threshold
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if health exceeded threshold within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.current_health > threshold,
            timeout=timeout,
            error_message=f"Health did not rise above {threshold}"
        )

    def wait_until_health_below(self, threshold: float, timeout: float = 10) -> bool:
        """
        Wait until health falls below threshold.

        Args:
            threshold (float): Health threshold
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if health fell below threshold within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.current_health < threshold,
            timeout=timeout,
            error_message=f"Health did not fall below {threshold}"
        )

    def wait_until_full(self, timeout: float = 10) -> bool:
        """
        Wait until health is full.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if health became full within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.current_health >= self.max_health,
            timeout=timeout,
            error_message="Health did not become full"
        )

    def wait_until_critical(self, timeout: float = 10) -> bool:
        """
        Wait until health becomes critical.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if health became critical within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_critical,
            timeout=timeout,
            error_message="Health did not become critical"
        )
