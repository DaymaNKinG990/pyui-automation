from typing import Optional, Any, Dict
from ..elements.base import UIElement


class InventorySlot(UIElement):
    """Represents an inventory slot element in games"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_empty(self) -> bool:
        """
        Check if slot is empty.

        Returns:
            bool: True if empty, False if contains item
        """
        return not bool(self._element.get_property("has_item"))

    @property
    def item_name(self) -> Optional[str]:
        """
        Get name of item in slot.

        Returns:
            Optional[str]: Item name or None if empty
        """
        return self._element.get_property("item_name") if not self.is_empty else None

    @property
    def item_count(self) -> int:
        """
        Get quantity of items in stack.

        Returns:
            int: Item count (0 if empty)
        """
        return self._element.get_property("item_count") or 0

    @property
    def item_rarity(self) -> Optional[str]:
        """
        Get item rarity level.

        Returns:
            Optional[str]: Rarity (e.g., 'common', 'rare', 'epic') or None if empty
        """
        return self._element.get_property("item_rarity") if not self.is_empty else None

    @property
    def item_level(self) -> Optional[int]:
        """
        Get item level requirement.

        Returns:
            Optional[int]: Required level or None if empty/no requirement
        """
        return self._element.get_property("item_level") if not self.is_empty else None

    @property
    def item_properties(self) -> Dict[str, Any]:
        """
        Get all item properties.

        Returns:
            Dict[str, Any]: Dictionary of item properties or empty dict if slot empty
        """
        return self._element.get_property("item_properties") or {}

    @property
    def is_selected(self) -> bool:
        """
        Check if slot is currently selected.

        Returns:
            bool: True if selected, False otherwise
        """
        return bool(self._element.get_property("selected"))

    @property
    def is_locked(self) -> bool:
        """
        Check if slot is locked.

        Returns:
            bool: True if locked, False otherwise
        """
        return bool(self._element.get_property("locked"))

    def select(self) -> None:
        """Select the inventory slot"""
        if not self.is_selected:
            self.click()

    def right_click(self) -> None:
        """Right click the slot (usually opens context menu)"""
        self._element.right_click()

    def drag_to(self, target_slot: 'InventorySlot') -> None:
        """
        Drag item to another inventory slot.

        Args:
            target_slot (InventorySlot): Target slot to drag item to

        Raises:
            ValueError: If current slot is empty or target slot is invalid
        """
        if self.is_empty:
            raise ValueError("Cannot drag from empty slot")
        
        if not target_slot or target_slot.is_locked:
            raise ValueError("Invalid or locked target slot")

        self._element.drag_to(target_slot._element)

    def split_stack(self, target_slot: 'InventorySlot', amount: int) -> None:
        """
        Split a stack of items with another slot.

        Args:
            target_slot (InventorySlot): Target slot for split items
            amount (int): Number of items to split

        Raises:
            ValueError: If invalid split operation
        """
        if self.is_empty:
            raise ValueError("Cannot split empty slot")
            
        if amount >= self.item_count:
            raise ValueError("Split amount must be less than total count")

        if not target_slot or target_slot.is_locked or not target_slot.is_empty:
            raise ValueError("Invalid or non-empty target slot")

        # Simulate shift+right click and amount input
        self._element.shift_right_click()
        self._session.send_keys(str(amount))
        self._session.send_keys("Enter")

    def wait_until_item(self, item_name: str, timeout: float = 10) -> bool:
        """
        Wait until slot contains specific item.

        Args:
            item_name (str): Name of item to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item appeared within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.item_name == item_name,
            timeout=timeout,
            error_message=f"Slot did not receive item '{item_name}'"
        )

    def wait_until_empty(self, timeout: float = 10) -> bool:
        """
        Wait until slot becomes empty.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if slot became empty within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_empty,
            timeout=timeout,
            error_message="Slot did not become empty"
        )
