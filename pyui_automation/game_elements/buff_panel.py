from typing import Optional, Any, Dict, List, Tuple
from datetime import timedelta
from ..elements.base import UIElement


class Buff(UIElement):
    """Represents a buff effect"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get buff name"""
        return self._element.get_property("name")

    @property
    def description(self) -> str:
        """Get buff description"""
        return self._element.get_property("description")

    @property
    def icon(self) -> str:
        """Get buff icon path"""
        return self._element.get_property("icon")

    @property
    def duration(self) -> Optional[timedelta]:
        """Get remaining duration"""
        return self._element.get_property("duration")

    @property
    def stacks(self) -> int:
        """Get number of stacks"""
        return self._element.get_property("stacks") or 1

    @property
    def source(self) -> Optional[str]:
        """Get buff source/caster"""
        return self._element.get_property("source")

    @property
    def is_permanent(self) -> bool:
        """Check if buff is permanent"""
        return self.duration is None

    @property
    def type(self) -> str:
        """Get buff type (magic/physical/etc)"""
        return self._element.get_property("type")

    @property
    def effects(self) -> List[Dict[str, Any]]:
        """Get buff effects"""
        return self._element.get_property("effects") or []

    def cancel(self) -> bool:
        """
        Cancel the buff if possible

        Returns:
            bool: True if successful
        """
        cancel_button = self._element.find_element(by="type", value="cancel_button")
        if cancel_button and cancel_button.is_enabled():
            cancel_button.click()
            return True
        return False

    def wait_until_expired(self, timeout: float = 10) -> bool:
        """
        Wait until buff expires

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if expired within timeout
        """
        return self._session.wait_for_condition(
            lambda: not self._element.exists(),
            timeout=timeout,
            error_message=f"Buff '{self.name}' did not expire"
        )


class Debuff(UIElement):
    """Represents a debuff effect"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get debuff name"""
        return self._element.get_property("name")

    @property
    def description(self) -> str:
        """Get debuff description"""
        return self._element.get_property("description")

    @property
    def icon(self) -> str:
        """Get debuff icon path"""
        return self._element.get_property("icon")

    @property
    def duration(self) -> Optional[timedelta]:
        """Get remaining duration"""
        return self._element.get_property("duration")

    @property
    def stacks(self) -> int:
        """Get number of stacks"""
        return self._element.get_property("stacks") or 1

    @property
    def source(self) -> Optional[str]:
        """Get debuff source/caster"""
        return self._element.get_property("source")

    @property
    def is_permanent(self) -> bool:
        """Check if debuff is permanent"""
        return self.duration is None

    @property
    def type(self) -> str:
        """Get debuff type (magic/physical/etc)"""
        return self._element.get_property("type")

    @property
    def is_dispellable(self) -> bool:
        """Check if debuff can be dispelled"""
        return self._element.get_property("dispellable")

    @property
    def effects(self) -> List[Dict[str, Any]]:
        """Get debuff effects"""
        return self._element.get_property("effects") or []

    def wait_until_expired(self, timeout: float = 10) -> bool:
        """
        Wait until debuff expires

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if expired within timeout
        """
        return self._session.wait_for_condition(
            lambda: not self._element.exists(),
            timeout=timeout,
            error_message=f"Debuff '{self.name}' did not expire"
        )


class BuffPanel(UIElement):
    """Represents the buff/debuff tracking interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def buff_limit(self) -> int:
        """Get maximum number of buffs"""
        return self._element.get_property("buff_limit")

    @property
    def debuff_limit(self) -> int:
        """Get maximum number of debuffs"""
        return self._element.get_property("debuff_limit")

    def get_buffs(self, buff_type: Optional[str] = None) -> List[Buff]:
        """
        Get active buffs

        Args:
            buff_type (Optional[str]): Filter by buff type

        Returns:
            List[Buff]: List of buffs
        """
        buffs = self._element.find_elements(
            by="type",
            value="buff",
            buff_type=buff_type
        )
        return [Buff(b, self._session) for b in buffs]

    def get_debuffs(self, debuff_type: Optional[str] = None) -> List[Debuff]:
        """
        Get active debuffs

        Args:
            debuff_type (Optional[str]): Filter by debuff type

        Returns:
            List[Debuff]: List of debuffs
        """
        debuffs = self._element.find_elements(
            by="type",
            value="debuff",
            debuff_type=debuff_type
        )
        return [Debuff(d, self._session) for d in debuffs]

    def get_buff(self, name: str) -> Optional[Buff]:
        """
        Find buff by name

        Args:
            name (str): Buff name

        Returns:
            Optional[Buff]: Found buff or None
        """
        buff = self._element.find_element(
            by="type",
            value="buff",
            name=name
        )
        return Buff(buff, self._session) if buff else None

    def get_debuff(self, name: str) -> Optional[Debuff]:
        """
        Find debuff by name

        Args:
            name (str): Debuff name

        Returns:
            Optional[Debuff]: Found debuff or None
        """
        debuff = self._element.find_element(
            by="type",
            value="debuff",
            name=name
        )
        return Debuff(debuff, self._session) if debuff else None

    def cancel_buff(self, name: str) -> bool:
        """
        Cancel specific buff

        Args:
            name (str): Buff name

        Returns:
            bool: True if successful
        """
        buff = self.get_buff(name)
        return buff.cancel() if buff else False

    def cancel_all_buffs(self) -> bool:
        """
        Cancel all cancellable buffs

        Returns:
            bool: True if any buffs were cancelled
        """
        cancelled = False
        for buff in self.get_buffs():
            if buff.cancel():
                cancelled = True
        return cancelled

    def has_buff_type(self, buff_type: str) -> bool:
        """
        Check if any buff of type exists

        Args:
            buff_type (str): Buff type to check

        Returns:
            bool: True if buff type found
        """
        return len(self.get_buffs(buff_type)) > 0

    def has_debuff_type(self, debuff_type: str) -> bool:
        """
        Check if any debuff of type exists

        Args:
            debuff_type (str): Debuff type to check

        Returns:
            bool: True if debuff type found
        """
        return len(self.get_debuffs(debuff_type)) > 0

    def get_dispellable_debuffs(self) -> List[Debuff]:
        """
        Get all dispellable debuffs

        Returns:
            List[Debuff]: List of dispellable debuffs
        """
        return [d for d in self.get_debuffs() if d.is_dispellable]

    def wait_for_buff(self, name: str, timeout: float = 10) -> bool:
        """
        Wait for buff to appear

        Args:
            name (str): Buff name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if buff appears within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.get_buff(name) is not None,
            timeout=timeout,
            error_message=f"Buff '{name}' did not appear"
        )

    def wait_for_debuff(self, name: str, timeout: float = 10) -> bool:
        """
        Wait for debuff to appear

        Args:
            name (str): Debuff name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if debuff appears within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.get_debuff(name) is not None,
            timeout=timeout,
            error_message=f"Debuff '{name}' did not appear"
        )

    def wait_until_buff_stacks(self, name: str, stacks: int, timeout: float = 10) -> bool:
        """
        Wait until buff reaches stack count

        Args:
            name (str): Buff name
            stacks (int): Required stacks
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if stack count reached within timeout
        """
        def check_stacks():
            buff = self.get_buff(name)
            return buff and buff.stacks >= stacks

        return self._session.wait_for_condition(
            check_stacks,
            timeout=timeout,
            error_message=f"Buff '{name}' did not reach {stacks} stacks"
        )

    def wait_until_no_debuffs(self, timeout: float = 10) -> bool:
        """
        Wait until all debuffs are gone

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if all debuffs gone within timeout
        """
        return self._session.wait_for_condition(
            lambda: len(self.get_debuffs()) == 0,
            timeout=timeout,
            error_message="Debuffs did not clear"
        )
