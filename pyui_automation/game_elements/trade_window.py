from typing import Optional, Any, List, Dict, Tuple
from ..elements.base import UIElement
from .inventory_slot import InventorySlot


class TradeSlot(InventorySlot):
    """Represents a slot in the trade window"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_locked(self) -> bool:
        """
        Check if slot is locked (can't be modified).

        Returns:
            bool: True if locked, False otherwise
        """
        return bool(self._element.get_property("locked"))

    @property
    def is_confirmed(self) -> bool:
        """
        Check if item in slot is confirmed.

        Returns:
            bool: True if confirmed, False otherwise
        """
        return bool(self._element.get_property("confirmed"))


class TradeOffer(UIElement):
    """Represents one side of a trade (player's or partner's)"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def player_name(self) -> str:
        """
        Get name of player making the offer.

        Returns:
            str: Player name
        """
        return self._element.get_property("player_name")

    @property
    def slots(self) -> List[TradeSlot]:
        """
        Get all trade slots.

        Returns:
            List[TradeSlot]: List of trade slots
        """
        slots = self._element.find_elements(by="type", value="trade_slot")
        return [TradeSlot(slot, self._session) for slot in slots]

    @property
    def money_offered(self) -> int:
        """
        Get amount of money offered.

        Returns:
            int: Money amount
        """
        return self._element.get_property("money") or 0

    @property
    def is_confirmed(self) -> bool:
        """
        Check if this side confirmed the trade.

        Returns:
            bool: True if confirmed, False otherwise
        """
        return bool(self._element.get_property("confirmed"))

    def get_empty_slot(self) -> Optional[TradeSlot]:
        """
        Get first empty trade slot.

        Returns:
            Optional[TradeSlot]: Empty slot or None if full
        """
        for slot in self.slots:
            if slot.is_empty and not slot.is_locked:
                return slot
        return None

    def set_money(self, amount: int) -> None:
        """
        Set money amount to offer.

        Args:
            amount (int): Money amount

        Raises:
            ValueError: If amount invalid or can't be modified
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        money_input = self._element.find_element(by="type", value="money_input")
        if not money_input:
            raise ValueError("Cannot modify money amount")

        money_input.send_keys(str(amount))
        money_input.send_keys("Enter")


class TradeWindow(UIElement):
    """Represents a trading window between players"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def my_offer(self) -> TradeOffer:
        """
        Get player's trade offer.

        Returns:
            TradeOffer: Player's offer
        """
        offer = self._element.find_element(by="type", value="my_offer")
        return TradeOffer(offer, self._session)

    @property
    def their_offer(self) -> TradeOffer:
        """
        Get trading partner's offer.

        Returns:
            TradeOffer: Partner's offer
        """
        offer = self._element.find_element(by="type", value="their_offer")
        return TradeOffer(offer, self._session)

    @property
    def is_confirmed(self) -> bool:
        """
        Check if trade is confirmed by both sides.

        Returns:
            bool: True if both confirmed, False otherwise
        """
        return self.my_offer.is_confirmed and self.their_offer.is_confirmed

    @property
    def countdown(self) -> Optional[int]:
        """
        Get trade countdown timer.

        Returns:
            Optional[int]: Seconds remaining or None if not counting
        """
        return self._element.get_property("countdown")

    def add_item(self, item_name: str, slot: Optional[TradeSlot] = None) -> None:
        """
        Add item to trade.

        Args:
            item_name (str): Name of item to add
            slot (Optional[TradeSlot]): Specific slot or None for first empty

        Raises:
            ValueError: If item not found or can't be added
        """
        if not slot:
            slot = self.my_offer.get_empty_slot()
            if not slot:
                raise ValueError("No empty slots available")

        # Find item in inventory
        inventory = self._session.find_element(by="type", value="inventory")
        if not inventory:
            raise ValueError("Cannot access inventory")

        item = None
        for inv_slot in inventory.find_elements(by="type", value="slot"):
            if inv_slot.get_property("item_name") == item_name:
                item = inv_slot
                break

        if not item:
            raise ValueError(f"Item '{item_name}' not found in inventory")

        # Drag item to trade slot
        item.drag_to(slot._element)

    def confirm_trade(self) -> None:
        """
        Confirm the trade.

        Raises:
            ValueError: If trade cannot be confirmed
        """
        confirm_button = self._element.find_element(by="name", value="Confirm")
        if not confirm_button or not confirm_button.get_property("enabled"):
            raise ValueError("Cannot confirm trade")
        confirm_button.click()

    def cancel_trade(self) -> None:
        """Cancel the trade"""
        cancel_button = self._element.find_element(by="name", value="Cancel")
        if cancel_button:
            cancel_button.click()

    def wait_until_partner_confirms(self, timeout: float = 10) -> bool:
        """
        Wait until trading partner confirms.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if partner confirmed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.their_offer.is_confirmed,
            timeout=timeout,
            error_message="Partner did not confirm trade"
        )

    def wait_until_trade_complete(self, timeout: float = 10) -> bool:
        """
        Wait until trade is completed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if trade completed within timeout, False otherwise
        """
        def check_complete():
            # Trade window should close when complete
            try:
                return not self._element.is_visible()
            except:
                return True

        return self._session.wait_for_condition(
            check_complete,
            timeout=timeout,
            error_message="Trade was not completed"
        )

    def wait_until_item_added(self, item_name: str, 
                            their_side: bool = False, timeout: float = 10) -> bool:
        """
        Wait until specific item is added to trade.

        Args:
            item_name (str): Item name to wait for
            their_side (bool): Check partner's offer instead of yours
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if item was added within timeout, False otherwise
        """
        offer = self.their_offer if their_side else self.my_offer
        
        def check_item():
            for slot in offer.slots:
                if slot.item_name == item_name:
                    return True
            return False

        return self._session.wait_for_condition(
            check_item,
            timeout=timeout,
            error_message=f"Item '{item_name}' was not added to trade"
        )
