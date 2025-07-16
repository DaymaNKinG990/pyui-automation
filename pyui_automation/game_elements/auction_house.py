from typing import Optional, Any, List, TYPE_CHECKING
from datetime import timedelta
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class AuctionItem(UIElement):
    """Represents an item listing in the auction house"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get item name"""
        return self._element.get_property("name")

    @property
    def seller(self) -> str:
        """Get seller name"""
        return self._element.get_property("seller")

    @property
    def current_bid(self) -> int:
        """Get current bid amount"""
        return self._element.get_property("current_bid")

    @property
    def buyout_price(self) -> Optional[int]:
        """Get buyout price if available"""
        return self._element.get_property("buyout_price")

    @property
    def time_left(self) -> timedelta:
        """Get time remaining on auction"""
        return self._element.get_property("time_left")

    @property
    def quantity(self) -> int:
        """Get item quantity"""
        return self._element.get_property("quantity")

    @property
    def item_level(self) -> Optional[int]:
        """Get item level if applicable"""
        return self._element.get_property("item_level")

    @property
    def quality(self) -> str:
        """Get item quality/rarity"""
        return self._element.get_property("quality")

    def place_bid(self, amount: int) -> bool:
        """
        Place bid on item

        Args:
            amount (int): Bid amount

        Returns:
            bool: True if bid placed successfully
        """
        bid_button = self._element.find_element(by="type", value="bid_button")
        if bid_button and bid_button.is_enabled():
            bid_button.click()
            amount_input = self._element.find_element(by="type", value="bid_amount")
            if amount_input:
                amount_input.send_keys(str(amount))
                confirm_button = self._element.find_element(by="type", value="confirm_bid")
                if confirm_button:
                    confirm_button.click()
                    return True
        return False

    def buyout(self) -> bool:
        """
        Purchase item at buyout price

        Returns:
            bool: True if purchase successful
        """
        if not self.buyout_price:
            return False

        buyout_button = self._element.find_element(by="type", value="buyout_button")
        if buyout_button and buyout_button.is_enabled():
            buyout_button.click()
            confirm_button = self._element.find_element(by="type", value="confirm_buyout")
            if confirm_button:
                confirm_button.click()
                return True
        return False

    def cancel(self) -> bool:
        """
        Cancel this auction item (for own auctions)

        Returns:
            bool: True if cancelled successfully
        """
        cancel_button = self._element.find_element(by="type", value="cancel_button")
        if cancel_button and cancel_button.is_enabled():
            cancel_button.click()
            confirm_button = self._element.find_element(by="type", value="confirm_cancel")
            if confirm_button:
                confirm_button.click()
                return True
        return False


class AuctionHouse(UIElement):
    """Represents the auction house interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def categories(self) -> List[str]:
        """Get available item categories"""
        return self._element.get_property("categories") or []

    @property
    def my_auctions(self) -> List[AuctionItem]:
        """Get list of own active auctions"""
        auctions = self._element.find_elements(
            by="type",
            value="auction_item",
            seller="player"
        )
        return [AuctionItem(a, self._session) for a in auctions]

    def search_items(self, 
                    name: Optional[str] = None,
                    category: Optional[str] = None,
                    min_level: Optional[int] = None,
                    max_level: Optional[int] = None,
                    quality: Optional[str] = None,
                    exact_match: bool = False) -> List[AuctionItem]:
        """
        Search auction house listings

        Args:
            name (Optional[str]): Item name to search for
            category (Optional[str]): Item category
            min_level (Optional[int]): Minimum item level
            max_level (Optional[int]): Maximum item level
            quality (Optional[str]): Item quality/rarity
            exact_match (bool): Require exact name match

        Returns:
            List[AuctionItem]: List of matching items
        """
        # Set search parameters
        if name:
            name_input = self._element.find_element(by="type", value="search_name")
            if name_input:
                name_input.send_keys(name)

        if category:
            category_dropdown = self._element.find_element(by="type", value="category_select")
            if category_dropdown:
                category_dropdown.select_option(category)

        if min_level is not None:
            min_level_input = self._element.find_element(by="type", value="min_level")
            if min_level_input:
                min_level_input.send_keys(str(min_level))

        if max_level is not None:
            max_level_input = self._element.find_element(by="type", value="max_level")
            if max_level_input:
                max_level_input.send_keys(str(max_level))

        if quality:
            quality_dropdown = self._element.find_element(by="type", value="quality_select")
            if quality_dropdown:
                quality_dropdown.select_option(quality)

        exact_match_checkbox = self._element.find_element(by="type", value="exact_match")
        if exact_match_checkbox:
            if exact_match_checkbox.is_checked() != exact_match:
                exact_match_checkbox.click()

        # Execute search
        search_button = self._element.find_element(by="type", value="search_button")
        if search_button:
            search_button.click()

        # Get results
        results = self._element.find_elements(by="type", value="auction_item")
        return [AuctionItem(r, self._session) for r in results]

    def create_auction(self,
                      item_name: str,
                      starting_bid: int,
                      buyout_price: Optional[int] = None,
                      duration: int = 24) -> bool:
        """
        Create new auction listing

        Args:
            item_name (str): Name of item to auction
            starting_bid (int): Starting bid amount
            buyout_price (Optional[int]): Optional buyout price
            duration (int): Auction duration in hours

        Returns:
            bool: True if auction created successfully
        """
        create_button = self._element.find_element(by="type", value="create_auction")
        if not create_button or not create_button.is_enabled():
            return False

        create_button.click()

        # Select item
        item_slot = self._element.find_element(by="type", value="item_slot")
        if not item_slot:
            return False

        # Find and select the item from inventory
        inventory = self._element.find_elements(by="type", value="inventory_item")
        item_found = False
        for item in inventory:
            if item.get_property("name") == item_name:
                item.click()
                item_found = True
                break

        if not item_found:
            return False

        # Set prices
        bid_input = self._element.find_element(by="type", value="starting_bid")
        if bid_input:
            bid_input.send_keys(str(starting_bid))

        if buyout_price is not None:
            buyout_input = self._element.find_element(by="type", value="buyout_price")
            if buyout_input:
                buyout_input.send_keys(str(buyout_price))

        # Set duration
        duration_dropdown = self._element.find_element(by="type", value="duration_select")
        if duration_dropdown:
            duration_dropdown.select_option(f"{duration}h")

        # Create auction
        confirm_button = self._element.find_element(by="type", value="confirm_create")
        if confirm_button and confirm_button.is_enabled():
            confirm_button.click()
            return True

        return False

    def cancel_auction(self, item_name: str) -> bool:
        """
        Cancel own auction

        Args:
            item_name (str): Name of item to cancel auction for

        Returns:
            bool: True if auction cancelled successfully
        """
        for auction in self.my_auctions:
            if auction.name == item_name:
                cancel_button = auction._element.find_element(by="type", value="cancel_button")
                if cancel_button and cancel_button.is_enabled():
                    cancel_button.click()
                    confirm_button = self._element.find_element(by="type", value="confirm_cancel")
                    if confirm_button:
                        confirm_button.click()
                        return True
        return False

    def collect_gold(self) -> bool:
        """
        Collect gold from completed auctions

        Returns:
            bool: True if gold collected successfully
        """
        collect_button = self._element.find_element(by="type", value="collect_gold")
        if collect_button and collect_button.is_enabled():
            collect_button.click()
            return True
        return False

    def wait_for_auction_end(self, item_name: str, timeout: float = 10) -> bool:
        """
        Wait for specific auction to end

        Args:
            item_name (str): Item name to wait for
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if auction ended within timeout
        """
        def auction_ended():
            for auction in self.my_auctions:
                if auction.name == item_name:
                    return False
            return True

        return self._session.wait_for_condition(
            auction_ended,
            timeout=timeout,
            error_message=f"Auction for '{item_name}' did not end"
        )

    def wait_for_price_below(self, item_name: str, target_price: int, timeout: float = 10) -> bool:
        """
        Wait for item price to drop below target

        Args:
            item_name (str): Item to monitor
            target_price (int): Target price threshold
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if price dropped within timeout
        """
        def check_price():
            items = self.search_items(name=item_name, exact_match=True)
            return any(i.buyout_price and i.buyout_price <= target_price for i in items)

        return self._session.wait_for_condition(
            check_price,
            timeout=timeout,
            error_message=f"Price for '{item_name}' did not drop below {target_price}"
        )
