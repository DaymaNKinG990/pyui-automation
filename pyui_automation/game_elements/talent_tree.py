from typing import Optional, Any, Dict, List, Tuple
from ..elements.base import UIElement


class TalentNode(UIElement):
    """Represents a single talent node in the talent tree"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get talent name"""
        return self._element.get_property("name")

    @property
    def description(self) -> str:
        """Get talent description"""
        return self._element.get_property("description")

    @property
    def rank(self) -> Tuple[int, int]:
        """Get current and maximum ranks"""
        return (
            self._element.get_property("current_rank"),
            self._element.get_property("max_rank")
        )

    @property
    def is_available(self) -> bool:
        """Check if talent can be learned"""
        return self._element.get_property("available")

    @property
    def prerequisites(self) -> List[str]:
        """Get prerequisite talent names"""
        return self._element.get_property("prerequisites") or []

    @property
    def is_maxed(self) -> bool:
        """Check if talent is at maximum rank"""
        current, maximum = self.rank
        return current >= maximum

    def learn(self) -> bool:
        """
        Learn/rank up the talent

        Returns:
            bool: True if successful
        """
        if not self.is_available or self.is_maxed:
            return False

        learn_button = self._element.find_element(by="type", value="learn_button")
        if learn_button and learn_button.is_enabled():
            learn_button.click()
            return True
        return False

    def wait_until_available(self, timeout: float = 10) -> bool:
        """
        Wait until talent becomes available

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if available within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.is_available,
            timeout=timeout,
            error_message=f"Talent '{self.name}' did not become available"
        )


class TalentSpec(UIElement):
    """Represents a talent specialization"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get specialization name"""
        return self._element.get_property("name")

    @property
    def description(self) -> str:
        """Get specialization description"""
        return self._element.get_property("description")

    @property
    def is_active(self) -> bool:
        """Check if this is the active spec"""
        return self._element.get_property("active")

    @property
    def points_spent(self) -> int:
        """Get total points spent in this spec"""
        return self._element.get_property("points_spent")

    def activate(self) -> bool:
        """
        Switch to this specialization

        Returns:
            bool: True if successful
        """
        if self.is_active:
            return True

        activate_button = self._element.find_element(by="type", value="activate_button")
        if activate_button and activate_button.is_enabled():
            activate_button.click()
            return True
        return False


class TalentTree(UIElement):
    """Represents the talent tree interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def available_points(self) -> int:
        """Get number of unspent talent points"""
        return self._element.get_property("available_points")

    @property
    def level_requirement(self) -> int:
        """Get required level for next talent point"""
        return self._element.get_property("level_requirement")

    @property
    def specializations(self) -> List[TalentSpec]:
        """Get all available specializations"""
        specs = self._element.find_elements(by="type", value="specialization")
        return [TalentSpec(s, self._session) for s in specs]

    @property
    def active_spec(self) -> Optional[TalentSpec]:
        """Get currently active specialization"""
        for spec in self.specializations:
            if spec.is_active:
                return spec
        return None

    def get_talent(self, name: str) -> Optional[TalentNode]:
        """
        Find talent by name

        Args:
            name (str): Talent name

        Returns:
            Optional[TalentNode]: Found talent or None
        """
        talent = self._element.find_element(by="name", value=name)
        return TalentNode(talent, self._session) if talent else None

    def get_available_talents(self) -> List[TalentNode]:
        """Get all currently learnable talents"""
        talents = self._element.find_elements(
            by="type",
            value="talent",
            available=True
        )
        return [TalentNode(t, self._session) for t in talents]

    def reset_talents(self) -> bool:
        """
        Reset all talents in current spec

        Returns:
            bool: True if successful
        """
        reset_button = self._element.find_element(by="type", value="reset_button")
        if reset_button and reset_button.is_enabled():
            reset_button.click()
            confirm_button = self._element.find_element(by="type", value="confirm_reset")
            if confirm_button:
                confirm_button.click()
                return True
        return False

    def learn_talent_path(self, talent_names: List[str]) -> bool:
        """
        Attempt to learn a sequence of talents

        Args:
            talent_names (List[str]): Ordered list of talents to learn

        Returns:
            bool: True if all talents were learned
        """
        for name in talent_names:
            talent = self.get_talent(name)
            if not talent or not talent.learn():
                return False
        return True

    def wait_for_points(self, points: int = 1, timeout: float = 10) -> bool:
        """
        Wait until having specified number of talent points

        Args:
            points (int): Required number of points
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if condition met within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.available_points >= points,
            timeout=timeout,
            error_message=f"Did not receive {points} talent points"
        )

    def export_build(self) -> Dict[str, int]:
        """
        Export current talent build

        Returns:
            Dict[str, int]: Mapping of talent names to ranks
        """
        talents = self._element.find_elements(by="type", value="talent")
        return {
            TalentNode(t, self._session).name: TalentNode(t, self._session).rank[0]
            for t in talents
            if TalentNode(t, self._session).rank[0] > 0
        }

    def import_build(self, build: Dict[str, int]) -> bool:
        """
        Import and apply a talent build

        Args:
            build (Dict[str, int]): Mapping of talent names to desired ranks

        Returns:
            bool: True if build was fully applied
        """
        self.reset_talents()
        
        for name, target_rank in build.items():
            talent = self.get_talent(name)
            if not talent:
                return False
                
            current_rank = 0
            while current_rank < target_rank:
                if not talent.learn():
                    return False
                current_rank += 1
                
        return True
