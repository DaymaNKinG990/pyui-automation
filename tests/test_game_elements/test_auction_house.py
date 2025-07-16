import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.auction_house import AuctionItem, AuctionHouse
from datetime import timedelta

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Sword',
        'seller': 'Player1',
        'current_bid': 100,
        'buyout_price': 200,
        'time_left': timedelta(hours=1),
        'quantity': 2,
        'item_level': 10,
        'quality': 'Rare',
        'categories': ['Weapon', 'Armor'],
    }.get(key)
    el.find_elements.side_effect = lambda **kwargs: []
    el.find_element.side_effect = lambda **kwargs: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    return s

@pytest.fixture
def auction_item(mock_element, mock_session):
    return AuctionItem(mock_element, mock_session)

@pytest.fixture
def auction_house(mock_element, mock_session):
    return AuctionHouse(mock_element, mock_session)

def test_auction_item_properties(auction_item):
    assert auction_item.name == 'Sword'
    assert auction_item.seller == 'Player1'
    assert auction_item.current_bid == 100
    assert auction_item.buyout_price == 200
    assert auction_item.time_left == timedelta(hours=1)
    assert auction_item.quantity == 2
    assert auction_item.item_level == 10
    assert auction_item.quality == 'Rare'

def test_auction_item_place_bid_success(mock_element, mock_session):
    bid_btn = MagicMock()
    bid_btn.is_enabled.return_value = True
    amount_input = MagicMock()
    confirm_btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: (
        bid_btn if value == 'bid_button' else
        amount_input if value == 'bid_amount' else
        confirm_btn if value == 'confirm_bid' else None)
    auction = AuctionItem(mock_element, mock_session)
    assert auction.place_bid(150) is True
    assert bid_btn.click.called
    assert amount_input.send_keys.called
    assert confirm_btn.click.called

def test_auction_item_place_bid_fail(mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    auction = AuctionItem(mock_element, mock_session)
    assert auction.place_bid(150) is False

def test_auction_item_buyout_success(mock_element, mock_session):
    buyout_btn = MagicMock()
    buyout_btn.is_enabled.return_value = True
    confirm_btn = MagicMock()
    mock_element.get_property.side_effect = lambda key: 200 if key == 'buyout_price' else 'x'
    mock_element.find_element.side_effect = lambda by=None, value=None: (
        buyout_btn if value == 'buyout_button' else
        confirm_btn if value == 'confirm_buyout' else None)
    auction = AuctionItem(mock_element, mock_session)
    assert auction.buyout() is True
    assert buyout_btn.click.called
    assert confirm_btn.click.called

def test_auction_item_buyout_fail_no_price(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: None if key == 'buyout_price' else 'x'
    auction = AuctionItem(mock_element, mock_session)
    assert auction.buyout() is False

def test_auction_item_buyout_fail_no_button(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 200 if key == 'buyout_price' else 'x'
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    auction = AuctionItem(mock_element, mock_session)
    assert auction.buyout() is False

def test_auction_house_categories(auction_house):
    assert auction_house.categories == ['Weapon', 'Armor']

def test_auction_house_my_auctions(mock_element, mock_session):
    auction_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None, seller=None: [auction_el] if seller == 'player' else []
    house = AuctionHouse(mock_element, mock_session)
    my_auctions = house.my_auctions
    assert all(isinstance(a, AuctionItem) for a in my_auctions)

def test_search_items_all_fields(mock_element, mock_session):
    name_input = MagicMock()
    category_dropdown = MagicMock()
    min_level_input = MagicMock()
    max_level_input = MagicMock()
    quality_dropdown = MagicMock()
    exact_checkbox = MagicMock()
    exact_checkbox.is_checked.return_value = False
    search_btn = MagicMock()
    result_el = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: {
        'search_name': name_input,
        'category_select': category_dropdown,
        'min_level': min_level_input,
        'max_level': max_level_input,
        'quality_select': quality_dropdown,
        'exact_match': exact_checkbox,
        'search_button': search_btn
    }.get(value)
    mock_element.find_elements.side_effect = lambda by=None, value=None: [result_el] if value == 'auction_item' else []
    house = AuctionHouse(mock_element, mock_session)
    items = house.search_items(name='Sword', category='Weapon', min_level=1, max_level=10, quality='Rare', exact_match=True)
    assert all(isinstance(i, AuctionItem) for i in items)
    assert name_input.send_keys.called
    assert category_dropdown.select_option.called
    assert min_level_input.send_keys.called
    assert max_level_input.send_keys.called
    assert quality_dropdown.select_option.called
    assert exact_checkbox.click.called
    assert search_btn.click.called

def test_search_items_no_results(mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    house = AuctionHouse(mock_element, mock_session)
    items = house.search_items()
    assert items == [] 

def test_create_auction_success(mock_element, mock_session):
    create_btn = MagicMock()
    create_btn.is_enabled.return_value = True
    item_slot = MagicMock()
    inventory_item = MagicMock()
    inventory_item.get_property.return_value = 'Sword'
    bid_input = MagicMock()
    buyout_input = MagicMock()
    duration_dropdown = MagicMock()
    confirm_btn = MagicMock()
    confirm_btn.is_enabled.return_value = True
    mock_element.find_element.side_effect = lambda by=None, value=None: {
        'create_auction': create_btn,
        'item_slot': item_slot,
        'starting_bid': bid_input,
        'buyout_price': buyout_input,
        'duration_select': duration_dropdown,
        'confirm_create': confirm_btn
    }.get(value)
    mock_element.find_elements.side_effect = lambda by=None, value=None: [inventory_item] if value == 'inventory_item' else []
    house = AuctionHouse(mock_element, mock_session)
    assert house.create_auction('Sword', 100, buyout_price=200, duration=24) is True
    assert create_btn.click.called
    assert item_slot is not None
    assert bid_input.send_keys.called
    assert buyout_input.send_keys.called
    assert duration_dropdown.select_option.called
    assert confirm_btn.click.called

def test_create_auction_fail_no_create_btn(mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    house = AuctionHouse(mock_element, mock_session)
    assert house.create_auction('Sword', 100) is False

def test_create_auction_fail_no_item_slot(mock_element, mock_session):
    create_btn = MagicMock()
    create_btn.is_enabled.return_value = True
    mock_element.find_element.side_effect = lambda by=None, value=None: create_btn if value == 'create_auction' else None
    house = AuctionHouse(mock_element, mock_session)
    assert house.create_auction('Sword', 100) is False

def test_create_auction_fail_no_inventory_item(mock_element, mock_session):
    create_btn = MagicMock()
    create_btn.is_enabled.return_value = True
    item_slot = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: create_btn if value == 'create_auction' else item_slot if value == 'item_slot' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    house = AuctionHouse(mock_element, mock_session)
    assert house.create_auction('Sword', 100) is False

def test_create_auction_fail_no_confirm(mock_element, mock_session):
    create_btn = MagicMock()
    create_btn.is_enabled.return_value = True
    item_slot = MagicMock()
    inventory_item = MagicMock()
    inventory_item.get_property.return_value = 'Sword'
    bid_input = MagicMock()
    duration_dropdown = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: {
        'create_auction': create_btn,
        'item_slot': item_slot,
        'starting_bid': bid_input,
        'duration_select': duration_dropdown,
        'confirm_create': None
    }.get(value)
    mock_element.find_elements.side_effect = lambda by=None, value=None: [inventory_item] if value == 'inventory_item' else []
    house = AuctionHouse(mock_element, mock_session)
    assert house.create_auction('Sword', 100) is False

def test_cancel_auction_success(mock_element, mock_session):
    auction_el = MagicMock()
    auction_el.get_property.side_effect = lambda key: 'Sword' if key == 'name' else None
    auction_el.cancel = MagicMock(return_value=True)
    mock_element.find_elements.side_effect = lambda by=None, value=None, seller=None: [auction_el] if seller == 'player' else []
    house = AuctionHouse(mock_element, mock_session)
    # Проверяем, что отмена работает через метод cancel
    assert house.my_auctions[0].cancel() is True

def test_cancel_auction_not_found(mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None, seller=None: []
    house = AuctionHouse(mock_element, mock_session)
    assert house.cancel_auction('NotExist') is False

def test_collect_gold_success(mock_element, mock_session):
    collect_btn = MagicMock()
    collect_btn.is_enabled.return_value = True
    mock_element.find_element.side_effect = lambda by=None, value=None: collect_btn if value == 'collect_gold' else None
    house = AuctionHouse(mock_element, mock_session)
    assert house.collect_gold() is True
    assert collect_btn.click.called

def test_collect_gold_fail(mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    house = AuctionHouse(mock_element, mock_session)
    assert house.collect_gold() is False

def test_wait_for_auction_end_success(mock_element, mock_session):
    mock_session.wait_for_condition.return_value = True
    house = AuctionHouse(mock_element, mock_session)
    assert house.wait_for_auction_end('Sword', timeout=1.0) is True

def test_wait_for_auction_end_fail(mock_element, mock_session):
    mock_session.wait_for_condition.return_value = False
    house = AuctionHouse(mock_element, mock_session)
    assert house.wait_for_auction_end('Sword', timeout=1.0) is False

def test_wait_for_price_below_success(mock_element, mock_session):
    mock_session.wait_for_condition.return_value = True
    house = AuctionHouse(mock_element, mock_session)
    assert house.wait_for_price_below('Sword', 50, timeout=1.0) is True

def test_wait_for_price_below_fail(mock_element, mock_session):
    mock_session.wait_for_condition.return_value = False
    house = AuctionHouse(mock_element, mock_session)
    assert house.wait_for_price_below('Sword', 50, timeout=1.0) is False 