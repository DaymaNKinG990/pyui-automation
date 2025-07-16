from typing import Optional, Any, Dict, List, Tuple, TYPE_CHECKING
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class StatAttribute(UIElement):
    """Represents a character attribute/stat"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """
        Get attribute name.

        Returns:
            str: Attribute name
        """
        return self._element.get_property("name")

    @property
    def value(self) -> float:
        """
        Get current attribute value.

        Returns:
            float: Current value
        """
        return self._element.get_property("value")

    @property
    def base_value(self) -> float:
        """
        Get base attribute value without modifiers.

        Returns:
            float: Base value
        """
        return self._element.get_property("base_value")

    @property
    def bonus_value(self) -> float:
        """
        Get bonus value from modifiers.

        Returns:
            float: Bonus value
        """
        return self.value - self.base_value

    @property
    def modifiers(self) -> List[Dict[str, Any]]:
        """
        Get list of active modifiers.

        Returns:
            List[Dict[str, Any]]: List of modifier details
        """
        return self._element.get_property("modifiers") or []

    def wait_until_value_above(self, threshold: float, timeout: float = 10) -> bool:
        """
        Wait until attribute value exceeds threshold.

        Args:
            threshold (float): Value threshold
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if value exceeded threshold within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.value > threshold,
            timeout=timeout,
            error_message=f"Attribute '{self.name}' did not exceed {threshold}"
        )

    def wait_until_value_below(self, threshold: float, timeout: float = 10) -> bool:
        """
        Wait until attribute value falls below threshold.

        Args:
            threshold (float): Value threshold
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if value fell below threshold within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.value < threshold,
            timeout=timeout,
            error_message=f"Attribute '{self.name}' did not fall below {threshold}"
        )


class CharacterStats(UIElement):
    """Represents a character stats panel"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def level(self) -> int:
        """
        Get character level.

        Returns:
            int: Current level
        """
        return self._element.get_property("level")

    @property
    def experience(self) -> Tuple[int, int]:
        """
        Get current and required experience.

        Returns:
            Tuple[int, int]: (current_xp, required_xp)
        """
        return (
            self._element.get_property("current_xp"),
            self._element.get_property("required_xp")
        )

    @property
    def attributes(self) -> List[StatAttribute]:
        """
        Get all character attributes.

        Returns:
            List[StatAttribute]: List of attributes
        """
        attrs = self._element.find_elements(by="type", value="attribute")
        return [StatAttribute(attr, self._session) for attr in attrs]

    @property
    def unspent_points(self) -> int:
        """
        Get number of unspent attribute points.

        Returns:
            int: Unspent points
        """
        return self._element.get_property("unspent_points") or 0

    def get_attribute(self, name: str) -> Optional[StatAttribute]:
        """
        Get attribute by name.

        Args:
            name (str): Attribute name

        Returns:
            Optional[StatAttribute]: Found attribute or None
        """
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None

    def increase_attribute(self, name: str, points: int = 1) -> None:
        """
        Increase attribute by spending points.

        Args:
            name (str): Attribute name
            points (int): Points to spend

        Raises:
            ValueError: If not enough points or attribute not found
        """
        if points > self.unspent_points:
            raise ValueError("Not enough unspent points")

        attr = self.get_attribute(name)
        if not attr:
            raise ValueError(f"Attribute '{name}' not found")

        for _ in range(points):
            increase_button = attr._element.find_element(by="name", value="Increase")
            if increase_button:
                increase_button.click()

    def reset_attributes(self) -> None:
        """
        Reset all attribute points.

        Raises:
            ValueError: If reset not available
        """
        reset_button = self._element.find_element(by="name", value="Reset")
        if not reset_button:
            raise ValueError("Attribute reset not available")

        reset_button.click()
        # Confirm reset if needed
        confirm = self._session.find_element(by="name", value="Confirm")
        if confirm:
            confirm.click()

    def wait_until_level_up(self, timeout: float = 10) -> bool:
        """
        Wait until character levels up.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if leveled up within timeout, False otherwise
        """
        current_level = self.level
        return self._session.wait_for_condition(
            lambda: self.level > current_level,
            timeout=timeout,
            error_message="Character did not level up"
        )

    def wait_until_points_available(self, points: int = 1, timeout: float = 10) -> bool:
        """
        Wait until specific number of attribute points available.

        Args:
            points (int): Required points
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if points became available within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.unspent_points >= points,
            timeout=timeout,
            error_message=f"Did not receive {points} attribute points"
        )
