from typing import Optional, Any, Dict, List, Tuple
from ..elements.base import UIElement


class BankTab(UIElement):
    """Represents a bank tab for organizing items"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get tab name"""
        return self._element.get_property("name")

    @property
    def icon(self) -> str:
        """Get tab icon path"""
        return self._element.get_property("icon")

    @property
    def is_locked(self) -> bool:
        """Check if tab is locked"""
        return self._element.get_property("locked")

    @property
    def slots_used(self) -> int:
        """Get number of used slots"""
        return self._element.get_property("slots_used")

    @property
    def slots_total(self) -> int:
        """Get total number of slots"""
        return self._element.get_property("slots_total")

    def select(self) -> bool:
        """
        Select this tab

        Returns:
            bool: True if successful
        """
        if not self.is_locked:
            self._element.click()
            return True
        return False


class BankSlot(UIElement):
    """Represents a single bank slot"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def item_name(self) -> Optional[str]:
        """Get name of item in slot"""
        return self._element.get_property("item_name")

    @property
    def stack_size(self) -> Tuple[int, int]:
        """Get current and maximum stack size"""
        return (
            self._element.get_property("current_stack"),
            self._element.get_property("max_stack")
        )

    @property
    def is_empty(self) -> bool:
        """Check if slot is empty"""
        return self.item_name is None

    def deposit_item(self) -> bool:
        """
        Deposit dragged item into slot

        Returns:
            bool: True if successful
        """
        if self.is_empty:
            self._element.click()
            return True
        return False

    def withdraw_item(self, amount: Optional[int] = None) -> bool:
        """
        Withdraw item from slot

        Args:
            amount (Optional[int]): Stack size to withdraw, None for all

        Returns:
            bool: True if successful
        """
        if not self.is_empty:
            if amount:
                self._element.right_click()
                amount_input = self._element.find_element(by="type", value="stack_input")
                if amount_input:
                    amount_input.send_keys(str(amount))
                    amount_input.send_keys("\n")
            else:
                self._element.click()
            return True
        return False

    def wait_until_empty(self, timeout: float = 10) -> bool:
        """
        Wait until slot becomes empty

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if empty within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.is_empty,
            timeout=timeout,
            error_message="Slot did not become empty"
        )

    def wait_for_item(self, item_name: str, timeout: float = 10) -> bool:
        """
        Wait for specific item to appear in slot

        Args:
            item_name (str): Expected item name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if item appears within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.item_name == item_name,
            timeout=timeout,
            error_message=f"Item '{item_name}' did not appear"
        )


class BankPanel(UIElement):
    """Represents the bank/vault interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_open(self) -> bool:
        """Check if bank is open"""
        return self._element.get_property("visible")

    @property
    def gold(self) -> int:
        """Get stored gold amount"""
        return self._element.get_property("gold")

    @property
    def tabs(self) -> List[BankTab]:
        """Get all bank tabs"""
        tabs = self._element.find_elements(by="type", value="bank_tab")
        return [BankTab(t, self._session) for t in tabs]

    def get_tab(self, name: str) -> Optional[BankTab]:
        """
        Find tab by name

        Args:
            name (str): Tab name

        Returns:
            Optional[BankTab]: Found tab or None
        """
        for tab in self.tabs:
            if tab.name == name:
                return tab
        return None

    def get_slots(self, tab: Optional[BankTab] = None) -> List[BankSlot]:
        """
        Get slots in specified tab or current tab

        Args:
            tab (Optional[BankTab]): Target tab, None for current

        Returns:
            List[BankSlot]: List of bank slots
        """
        if tab:
            tab.select()

        slots = self._element.find_elements(by="type", value="bank_slot")
        return [BankSlot(s, self._session) for s in slots]

    def find_item(self, item_name: str) -> Optional[BankSlot]:
        """
        Find first slot containing specified item

        Args:
            item_name (str): Item to find

        Returns:
            Optional[BankSlot]: Slot with item or None
        """
        for tab in self.tabs:
            if tab.is_locked:
                continue
            tab.select()
            for slot in self.get_slots(tab):
                if slot.item_name == item_name:
                    return slot
        return None

    def deposit_gold(self, amount: int) -> bool:
        """
        Deposit gold into bank

        Args:
            amount (int): Amount to deposit

        Returns:
            bool: True if successful
        """
        deposit_button = self._element.find_element(by="type", value="deposit_gold")
        if deposit_button:
            deposit_button.click()
            amount_input = self._element.find_element(by="type", value="gold_input")
            if amount_input:
                amount_input.send_keys(str(amount))
                amount_input.send_keys("\n")
                return True
        return False

    def withdraw_gold(self, amount: int) -> bool:
        """
        Withdraw gold from bank

        Args:
            amount (int): Amount to withdraw

        Returns:
            bool: True if successful
        """
        if amount > self.gold:
            return False

        withdraw_button = self._element.find_element(by="type", value="withdraw_gold")
        if withdraw_button:
            withdraw_button.click()
            amount_input = self._element.find_element(by="type", value="gold_input")
            if amount_input:
                amount_input.send_keys(str(amount))
                amount_input.send_keys("\n")
                return True
        return False

    def wait_until_open(self, timeout: float = 10) -> bool:
        """
        Wait until bank window opens

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if opened within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.is_open,
            timeout=timeout,
            error_message="Bank did not open"
        )
