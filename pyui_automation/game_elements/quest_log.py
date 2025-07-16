from typing import Optional, Any, List, Dict, Tuple, TYPE_CHECKING
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class QuestObjective(UIElement):
    """Represents a quest objective"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def description(self) -> str:
        """
        Get objective description.

        Returns:
            str: Objective description text
        """
        return self._element.get_property("description")

    @property
    def progress(self) -> Tuple[int, int]:
        """
        Get objective progress.

        Returns:
            Tuple[int, int]: (current, required) progress values
        """
        return (
            self._element.get_property("current_progress"),
            self._element.get_property("required_progress")
        )

    @property
    def is_completed(self) -> bool:
        """
        Check if objective is completed.

        Returns:
            bool: True if completed, False otherwise
        """
        current, required = self.progress
        return current >= required

    @property
    def location(self) -> Optional[Tuple[float, float]]:
        """
        Get objective location if available.

        Returns:
            Optional[Tuple[float, float]]: (x, y) coordinates or None
        """
        x = self._element.get_property("location_x")
        y = self._element.get_property("location_y")
        return (x, y) if x is not None and y is not None else None


class Quest(UIElement):
    """Represents an individual quest"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def title(self) -> str:
        """
        Get quest title.

        Returns:
            str: Quest title
        """
        return self._element.get_property("title")

    @property
    def description(self) -> str:
        """
        Get quest description.

        Returns:
            str: Quest description
        """
        return self._element.get_property("description")

    @property
    def level(self) -> int:
        """
        Get quest level requirement.

        Returns:
            int: Required level
        """
        return self._element.get_property("level")

    @property
    def status(self) -> str:
        """
        Get quest status.

        Returns:
            str: Status (e.g., 'active', 'completed', 'failed')
        """
        return self._element.get_property("status")

    @property
    def objectives(self) -> List[QuestObjective]:
        """
        Get quest objectives.

        Returns:
            List[QuestObjective]: List of objectives
        """
        objectives = self._element.find_elements(by="type", value="objective")
        return [QuestObjective(obj, self._session) for obj in objectives]

    @property
    def rewards(self) -> Dict[str, Any]:
        """
        Get quest rewards.

        Returns:
            Dict[str, Any]: Dictionary of rewards
        """
        return self._element.get_property("rewards") or {}

    @property
    def is_tracked(self) -> bool:
        """
        Check if quest is being tracked.

        Returns:
            bool: True if tracked, False otherwise
        """
        return bool(self._element.get_property("tracked"))

    def track(self) -> None:
        """Start tracking the quest"""
        if not self.is_tracked:
            track_button = self._element.find_element(by="name", value="Track")
            if track_button:
                track_button.click()

    def untrack(self) -> None:
        """Stop tracking the quest"""
        if self.is_tracked:
            untrack_button = self._element.find_element(by="name", value="Untrack")
            if untrack_button:
                untrack_button.click()

    def abandon(self) -> None:
        """
        Abandon the quest.

        Raises:
            ValueError: If quest cannot be abandoned
        """
        if self.status == "completed":
            raise ValueError("Cannot abandon completed quest")

        abandon_button = self._element.find_element(by="name", value="Abandon")
        if abandon_button:
            abandon_button.click()
            # Confirm abandon if needed
            confirm = self._session.find_element(by="name", value="Confirm")
            if confirm:
                confirm.click()

    def show_on_map(self) -> None:
        """Show quest location on map"""
        map_button = self._element.find_element(by="name", value="ShowOnMap")
        if map_button:
            map_button.click()


class QuestLog(UIElement):
    """Represents a quest log/journal element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def active_quests(self) -> List[Quest]:
        """
        Get all active quests.

        Returns:
            List[Quest]: List of active quests
        """
        quests = self._element.find_elements(
            by="state", 
            value={"status": "active"}
        )
        return [Quest(q, self._session) for q in quests]

    @property
    def completed_quests(self) -> List[Quest]:
        """
        Get all completed quests.

        Returns:
            List[Quest]: List of completed quests
        """
        quests = self._element.find_elements(
            by="state", 
            value={"status": "completed"}
        )
        return [Quest(q, self._session) for q in quests]

    @property
    def tracked_quests(self) -> List[Quest]:
        """
        Get currently tracked quests.

        Returns:
            List[Quest]: List of tracked quests
        """
        return [q for q in self.active_quests if q.is_tracked]

    def get_quest(self, title: str) -> Optional[Quest]:
        """
        Find quest by title.

        Args:
            title (str): Quest title to find

        Returns:
            Optional[Quest]: Found quest or None
        """
        for quest in self.active_quests + self.completed_quests:
            if quest.title == title:
                return quest
        return None

    def get_quests_by_level(self, min_level: int, max_level: int) -> List[Quest]:
        """
        Get quests within level range.

        Args:
            min_level (int): Minimum quest level
            max_level (int): Maximum quest level

        Returns:
            List[Quest]: List of matching quests
        """
        return [q for q in self.active_quests 
                if min_level <= q.level <= max_level]

    def wait_until_quest_completed(self, title: str, timeout: float = 10) -> bool:
        """
        Wait until specific quest is completed.

        Args:
            title (str): Quest title
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if quest completed within timeout, False otherwise
        """
        def check_completed():
            quest = self.get_quest(title)
            return quest and quest.status == "completed"

        return self._session.wait_for_condition(
            check_completed,
            timeout=timeout,
            error_message=f"Quest '{title}' was not completed"
        )

    def wait_until_objective_completed(self, quest_title: str, 
                                     objective_desc: str, timeout: float = 10) -> bool:
        """
        Wait until specific quest objective is completed.

        Args:
            quest_title (str): Quest title
            objective_desc (str): Objective description
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if objective completed within timeout, False otherwise
        """
        def check_objective():
            quest = self.get_quest(quest_title)
            if not quest:
                return False
            for obj in quest.objectives:
                if obj.description == objective_desc:
                    return obj.is_completed
            return False

        return self._session.wait_for_condition(
            check_objective,
            timeout=timeout,
            error_message=f"Objective '{objective_desc}' was not completed"
        )
