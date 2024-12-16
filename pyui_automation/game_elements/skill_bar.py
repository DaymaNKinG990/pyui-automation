from typing import Optional, Any, List, Dict, Tuple
from ..elements.base import UIElement


class SkillSlot(UIElement):
    """Represents a skill slot in the skill bar"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def skill_name(self) -> Optional[str]:
        """
        Get name of assigned skill.

        Returns:
            Optional[str]: Skill name or None if empty
        """
        return self._element.get_property("skill_name")

    @property
    def hotkey(self) -> Optional[str]:
        """
        Get assigned hotkey.

        Returns:
            Optional[str]: Hotkey or None if not assigned
        """
        return self._element.get_property("hotkey")

    @property
    def cooldown(self) -> float:
        """
        Get remaining cooldown in seconds.

        Returns:
            float: Cooldown time (0 if ready)
        """
        return self._element.get_property("cooldown") or 0.0

    @property
    def is_ready(self) -> bool:
        """
        Check if skill is ready to use.

        Returns:
            bool: True if ready, False if on cooldown
        """
        return self.cooldown <= 0

    @property
    def is_active(self) -> bool:
        """
        Check if skill is currently active.

        Returns:
            bool: True if active, False otherwise
        """
        return bool(self._element.get_property("active"))

    @property
    def charges(self) -> Tuple[int, int]:
        """
        Get current and maximum skill charges.

        Returns:
            Tuple[int, int]: (current, max) charges
        """
        return (
            self._element.get_property("current_charges") or 0,
            self._element.get_property("max_charges") or 0
        )

    @property
    def resource_cost(self) -> Dict[str, float]:
        """
        Get skill resource costs.

        Returns:
            Dict[str, float]: Resource costs (e.g., {'mana': 50})
        """
        return self._element.get_property("resource_cost") or {}

    def use(self) -> None:
        """
        Use the skill.

        Raises:
            ValueError: If skill not ready or no skill assigned
        """
        if not self.skill_name:
            raise ValueError("No skill assigned to slot")
        if not self.is_ready:
            raise ValueError("Skill is on cooldown")
        
        if self.hotkey:
            self._session.send_keys(self.hotkey)
        else:
            self.click()

    def wait_until_ready(self, timeout: float = 10) -> bool:
        """
        Wait until skill is ready to use.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if skill became ready within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_ready,
            timeout=timeout,
            error_message="Skill did not become ready"
        )

    def wait_until_active(self, timeout: float = 10) -> bool:
        """
        Wait until skill becomes active.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if skill became active within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_active,
            timeout=timeout,
            error_message="Skill did not become active"
        )


class SkillBar(UIElement):
    """Represents a skill bar/hotbar element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def slots(self) -> List[SkillSlot]:
        """
        Get all skill slots.

        Returns:
            List[SkillSlot]: List of skill slots
        """
        slots = self._element.find_elements(by="type", value="skill_slot")
        return [SkillSlot(slot, self._session) for slot in slots]

    def get_slot(self, index: int) -> Optional[SkillSlot]:
        """
        Get skill slot by index.

        Args:
            index (int): Slot index

        Returns:
            Optional[SkillSlot]: Found slot or None
        """
        slots = self.slots
        return slots[index] if 0 <= index < len(slots) else None

    def get_slot_by_skill(self, skill_name: str) -> Optional[SkillSlot]:
        """
        Get slot containing specific skill.

        Args:
            skill_name (str): Skill name to find

        Returns:
            Optional[SkillSlot]: Found slot or None
        """
        for slot in self.slots:
            if slot.skill_name == skill_name:
                return slot
        return None

    def get_slot_by_hotkey(self, hotkey: str) -> Optional[SkillSlot]:
        """
        Get slot with specific hotkey.

        Args:
            hotkey (str): Hotkey to find

        Returns:
            Optional[SkillSlot]: Found slot or None
        """
        for slot in self.slots:
            if slot.hotkey == hotkey:
                return slot
        return None

    def use_skill(self, skill_name: str) -> None:
        """
        Use a skill by name.

        Args:
            skill_name (str): Name of skill to use

        Raises:
            ValueError: If skill not found or not ready
        """
        slot = self.get_slot_by_skill(skill_name)
        if not slot:
            raise ValueError(f"Skill '{skill_name}' not found")
        slot.use()

    def use_hotkey(self, hotkey: str) -> None:
        """
        Use a skill by hotkey.

        Args:
            hotkey (str): Hotkey to use

        Raises:
            ValueError: If hotkey not found
        """
        slot = self.get_slot_by_hotkey(hotkey)
        if not slot:
            raise ValueError(f"No skill assigned to hotkey '{hotkey}'")
        slot.use()

    def wait_until_skill_ready(self, skill_name: str, timeout: float = 10) -> bool:
        """
        Wait until specific skill is ready.

        Args:
            skill_name (str): Skill name
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if skill became ready within timeout, False otherwise
        """
        slot = self.get_slot_by_skill(skill_name)
        return slot.wait_until_ready(timeout) if slot else False

    def wait_until_any_ready(self, timeout: float = 10) -> bool:
        """
        Wait until any skill becomes ready.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if any skill became ready within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: any(slot.is_ready for slot in self.slots),
            timeout=timeout,
            error_message="No skills became ready"
        )

    def use_skill_by_name(self, skill_name: str) -> None:
        """
        Alias for use_skill method.

        Args:
            skill_name (str): Name of skill to use

        Raises:
            ValueError: If skill not found or not ready
        """
        return self.use_skill(skill_name)

    def is_skill_ready(self, skill_name: str) -> bool:
        """
        Check if a skill is ready to use.

        Args:
            skill_name (str): Name of skill to check

        Returns:
            bool: True if skill is ready, False otherwise
        """
        slot = self.get_slot_by_skill(skill_name)
        if not slot:
            raise ValueError(f"Skill '{skill_name}' not found")
        return slot.is_ready

    def wait_for_skill_ready(self, skill_name: str, timeout: float = 10) -> bool:
        """
        Alias for wait_until_skill_ready method.

        Args:
            skill_name (str): Skill name
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if skill became ready within timeout, False otherwise
        """
        return self.wait_until_skill_ready(skill_name, timeout)

    def get_skill_cooldown(self, skill_name: str) -> float:
        """
        Get remaining cooldown for a skill.

        Args:
            skill_name (str): Name of skill to check

        Returns:
            float: Remaining cooldown in seconds (0 if ready)

        Raises:
            ValueError: If skill not found
        """
        slot = self.get_slot_by_skill(skill_name)
        if not slot:
            raise ValueError(f"Skill '{skill_name}' not found")
        return slot.cooldown

    def get_skill_charges(self, skill_name: str) -> Tuple[int, int]:
        """
        Get remaining charges for a skill.

        Args:
            skill_name (str): Name of skill to check

        Returns:
            Tuple[int, int]: Number of charges remaining

        Raises:
            ValueError: If skill not found
        """
        slot = self.get_slot_by_skill(skill_name)
        if not slot:
            raise ValueError(f"Skill '{skill_name}' not found")
        return slot.charges
