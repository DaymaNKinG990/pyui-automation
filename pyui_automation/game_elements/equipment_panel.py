from typing import Optional, Any, Dict, List, Tuple
from ..elements.base import UIElement


class EquipmentSlot(UIElement):
    """Represents an equipment slot for a specific gear type"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def slot_type(self) -> str:
        """
        Get equipment slot type.

        Returns:
            str: Slot type (e.g., 'head', 'chest', 'weapon')
        """
        return self._element.get_property("slot_type")

    @property
    def item_name(self) -> Optional[str]:
        """
        Get name of equipped item.

        Returns:
            Optional[str]: Item name or None if empty
        """
        return self._element.get_property("item_name")

    @property
    def item_level(self) -> Optional[int]:
        """
        Get item level.

        Returns:
            Optional[int]: Item level or None if empty
        """
        return self._element.get_property("item_level")

    @property
    def durability(self) -> Optional[Tuple[int, int]]:
        """
        Get item durability.

        Returns:
            Optional[Tuple[int, int]]: (current, max) durability or None if empty
        """
        current = self._element.get_property("durability_current")
        maximum = self._element.get_property("durability_max")
        return (current, maximum) if current is not None else None

    @property
    def stats(self) -> Dict[str, float]:
        """
        Get item stats.

        Returns:
            Dict[str, float]: Dictionary of stat bonuses
        """
        return self._element.get_property("stats") or {}

    @property
    def requirements(self) -> Dict[str, Any]:
        """
        Get item requirements.

        Returns:
            Dict[str, Any]: Dictionary of requirements
        """
        return self._element.get_property("requirements") or {}

    @property
    def is_broken(self) -> bool:
        """
        Check if item is broken.

        Returns:
            bool: True if broken, False otherwise
        """
        durability = self.durability
        return durability and durability[0] <= 0

    def unequip(self) -> None:
        """
        Unequip item from slot.

        Raises:
            ValueError: If slot empty or action not allowed
        """
        if not self.item_name:
            raise ValueError("No item to unequip")

        unequip_button = self._element.find_element(by="name", value="Unequip")
        if unequip_button:
            unequip_button.click()

    def repair(self) -> None:
        """
        Repair equipped item.

        Raises:
            ValueError: If item can't be repaired
        """
        if not self.is_broken:
            raise ValueError("Item is not broken")

        repair_button = self._element.find_element(by="name", value="Repair")
        if repair_button:
            repair_button.click()

    def wait_until_equipped(self, item_name: str, timeout: float = 10) -> bool:
        """
        Wait until specific item is equipped.

        Args:
            item_name (str): Expected item name
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item equipped within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.item_name == item_name,
            timeout=timeout,
            error_message=f"Item '{item_name}' was not equipped"
        )

    def wait_until_repaired(self, timeout: float = 10) -> bool:
        """
        Wait until item is fully repaired.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if repaired within timeout, False otherwise
        """
        def check_repaired():
            durability = self.durability
            return durability and durability[0] >= durability[1]

        return self._session.wait_for_condition(
            check_repaired,
            timeout=timeout,
            error_message="Item was not repaired"
        )


class EquipmentSet(UIElement):
    """Represents a saved equipment set"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """
        Get set name.

        Returns:
            str: Set name
        """
        return self._element.get_property("name")

    @property
    def items(self) -> Dict[str, str]:
        """
        Get items in set.

        Returns:
            Dict[str, str]: Dictionary of slot_type -> item_name
        """
        return self._element.get_property("items") or {}

    def equip(self) -> None:
        """Equip all items in the set"""
        equip_button = self._element.find_element(by="name", value="Equip")
        if equip_button:
            equip_button.click()

    def update(self) -> None:
        """Update set with currently equipped items"""
        update_button = self._element.find_element(by="name", value="Update")
        if update_button:
            update_button.click()

    def delete(self) -> None:
        """Delete this equipment set"""
        delete_button = self._element.find_element(by="name", value="Delete")
        if delete_button:
            delete_button.click()
            # Confirm deletion if needed
            confirm = self._session.find_element(by="name", value="Confirm")
            if confirm:
                confirm.click()


class EquipmentPanel(UIElement):
    """Represents a character equipment panel"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def slots(self) -> Dict[str, EquipmentSlot]:
        """
        Get all equipment slots.

        Returns:
            Dict[str, EquipmentSlot]: Dictionary of slot_type -> slot
        """
        slots = self._element.find_elements(by="type", value="equipment_slot")
        return {
            slot.get_property("slot_type"): EquipmentSlot(slot, self._session)
            for slot in slots
        }

    @property
    def equipment_sets(self) -> List[EquipmentSet]:
        """
        Get saved equipment sets.

        Returns:
            List[EquipmentSet]: List of equipment sets
        """
        sets = self._element.find_elements(by="type", value="equipment_set")
        return [EquipmentSet(s, self._session) for s in sets]

    @property
    def average_item_level(self) -> float:
        """
        Get average item level across all slots.

        Returns:
            float: Average item level
        """
        return self._element.get_property("average_item_level") or 0.0

    def get_slot(self, slot_type: str) -> Optional[EquipmentSlot]:
        """
        Get equipment slot by type.

        Args:
            slot_type (str): Slot type to find

        Returns:
            Optional[EquipmentSlot]: Found slot or None
        """
        return self.slots.get(slot_type)

    def get_equipment_set(self, name: str) -> Optional[EquipmentSet]:
        """
        Get equipment set by name.

        Args:
            name (str): Set name to find

        Returns:
            Optional[EquipmentSet]: Found set or None
        """
        for equipment_set in self.equipment_sets:
            if equipment_set.name == name:
                return equipment_set
        return None

    def create_equipment_set(self, name: str) -> None:
        """
        Create new equipment set.

        Args:
            name (str): Set name

        Raises:
            ValueError: If name already exists
        """
        if self.get_equipment_set(name):
            raise ValueError(f"Equipment set '{name}' already exists")

        new_set = self._element.find_element(by="name", value="NewSet")
        if new_set:
            new_set.click()
            name_input = self._session.find_element(by="type", value="input")
            if name_input:
                name_input.send_keys(name)
                name_input.send_keys("Enter")

    def repair_all(self) -> None:
        """Repair all equipped items"""
        repair_all = self._element.find_element(by="name", value="RepairAll")
        if repair_all:
            repair_all.click()

    def unequip_all(self) -> None:
        """Unequip all items"""
        for slot in self.slots.values():
            if slot.item_name:
                slot.unequip()

    def wait_until_item_level(self, level: float, timeout: float = 10) -> bool:
        """
        Wait until average item level reaches threshold.

        Args:
            level (float): Target item level
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if level reached within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.average_item_level >= level,
            timeout=timeout,
            error_message=f"Average item level did not reach {level}"
        )

    def wait_until_all_repaired(self, timeout: float = 10) -> bool:
        """
        Wait until all items are fully repaired.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if all repaired within timeout, False otherwise
        """
        def check_all_repaired():
            for slot in self.slots.values():
                if slot.item_name:
                    durability = slot.durability
                    if not durability or durability[0] < durability[1]:
                        return False
            return True

        return self._session.wait_for_condition(
            check_all_repaired,
            timeout=timeout,
            error_message="Not all items were repaired"
        )
