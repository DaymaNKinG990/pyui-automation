from typing import Optional, Any, List, Dict, Tuple
from datetime import datetime
from ..elements.base import UIElement


class AchievementCriteria(UIElement):
    """Represents an achievement criteria/requirement"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def description(self) -> str:
        """
        Get criteria description.

        Returns:
            str: Criteria description
        """
        return self._element.get_property("description")

    @property
    def progress(self) -> Tuple[int, int]:
        """
        Get criteria progress.

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
        Check if criteria is completed.

        Returns:
            bool: True if completed, False otherwise
        """
        current, required = self.progress
        return current >= required


class Achievement(UIElement):
    """Represents an individual achievement"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def title(self) -> str:
        """
        Get achievement title.

        Returns:
            str: Achievement title
        """
        return self._element.get_property("title")

    @property
    def description(self) -> str:
        """
        Get achievement description.

        Returns:
            str: Achievement description
        """
        return self._element.get_property("description")

    @property
    def points(self) -> int:
        """
        Get achievement points value.

        Returns:
            int: Points value
        """
        return self._element.get_property("points") or 0

    @property
    def category(self) -> str:
        """
        Get achievement category.

        Returns:
            str: Category name
        """
        return self._element.get_property("category")

    @property
    def is_completed(self) -> bool:
        """
        Check if achievement is completed.

        Returns:
            bool: True if completed, False otherwise
        """
        return bool(self._element.get_property("completed"))

    @property
    def completion_date(self) -> Optional[datetime]:
        """
        Get achievement completion date.

        Returns:
            Optional[datetime]: Completion date or None if not completed
        """
        ts = self._element.get_property("completion_timestamp")
        return datetime.fromtimestamp(ts) if ts else None

    @property
    def criteria(self) -> List[AchievementCriteria]:
        """
        Get achievement criteria.

        Returns:
            List[AchievementCriteria]: List of criteria
        """
        criteria = self._element.find_elements(by="type", value="criteria")
        return [AchievementCriteria(c, self._session) for c in criteria]

    @property
    def rewards(self) -> Dict[str, Any]:
        """
        Get achievement rewards.

        Returns:
            Dict[str, Any]: Dictionary of rewards
        """
        return self._element.get_property("rewards") or {}

    def track(self) -> None:
        """Start tracking this achievement"""
        track_button = self._element.find_element(by="name", value="Track")
        if track_button:
            track_button.click()

    def show_in_map(self) -> None:
        """Show achievement location in map if applicable"""
        map_button = self._element.find_element(by="name", value="ShowInMap")
        if map_button:
            map_button.click()

    def wait_until_completed(self, timeout: float = 10) -> bool:
        """
        Wait until achievement is completed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if completed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_completed,
            timeout=timeout,
            error_message=f"Achievement '{self.title}' was not completed"
        )


class AchievementPanel(UIElement):
    """Represents an achievement tracking panel"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def total_points(self) -> int:
        """
        Get total achievement points earned.

        Returns:
            int: Total points
        """
        return self._element.get_property("total_points") or 0

    @property
    def completed_count(self) -> int:
        """
        Get number of completed achievements.

        Returns:
            int: Completed count
        """
        return self._element.get_property("completed_count") or 0

    @property
    def categories(self) -> List[str]:
        """
        Get available achievement categories.

        Returns:
            List[str]: List of category names
        """
        return self._element.get_property("categories") or []

    @property
    def tracked_achievements(self) -> List[Achievement]:
        """
        Get currently tracked achievements.

        Returns:
            List[Achievement]: List of tracked achievements
        """
        tracked = self._element.find_elements(
            by="state",
            value={"tracked": True}
        )
        return [Achievement(a, self._session) for a in tracked]

    def get_achievements(self, 
                        category: Optional[str] = None,
                        completed_only: bool = False) -> List[Achievement]:
        """
        Get achievements filtered by criteria.

        Args:
            category (Optional[str]): Filter by category
            completed_only (bool): Only show completed achievements

        Returns:
            List[Achievement]: List of matching achievements
        """
        achievements = self._element.find_elements(by="type", value="achievement")
        result = [Achievement(a, self._session) for a in achievements]

        if category:
            result = [a for a in result if a.category == category]
        if completed_only:
            result = [a for a in result if a.is_completed]

        return result

    def get_achievement(self, title: str) -> Optional[Achievement]:
        """
        Find achievement by title.

        Args:
            title (str): Achievement title

        Returns:
            Optional[Achievement]: Found achievement or None
        """
        for achievement in self.get_achievements():
            if achievement.title == title:
                return achievement
        return None

    def search(self, query: str) -> List[Achievement]:
        """
        Search achievements by text.

        Args:
            query (str): Search query

        Returns:
            List[Achievement]: List of matching achievements
        """
        search_box = self._element.find_element(by="type", value="search")
        if search_box:
            search_box.send_keys(query)

        results = self._element.find_elements(by="type", value="search_result")
        return [Achievement(r, self._session) for r in results]

    def select_category(self, category: str) -> None:
        """
        Select achievement category.

        Args:
            category (str): Category to select

        Raises:
            ValueError: If category not found
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' not found")

        category_list = self._element.find_element(by="type", value="category_list")
        if category_list:
            category_item = category_list.find_element(by="name", value=category)
            if category_item:
                category_item.click()

    def wait_until_achievement_unlocked(self, title: str, timeout: float = 10) -> bool:
        """
        Wait until specific achievement is unlocked.

        Args:
            title (str): Achievement title
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if unlocked within timeout, False otherwise
        """
        def check_unlocked():
            achievement = self.get_achievement(title)
            return achievement and achievement.is_completed

        return self._session.wait_for_condition(
            check_unlocked,
            timeout=timeout,
            error_message=f"Achievement '{title}' was not unlocked"
        )

    def wait_until_points_earned(self, points: int, timeout: float = 10) -> bool:
        """
        Wait until total points reaches threshold.

        Args:
            points (int): Points threshold
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if points reached within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.total_points >= points,
            timeout=timeout,
            error_message=f"Did not reach {points} achievement points"
        )
