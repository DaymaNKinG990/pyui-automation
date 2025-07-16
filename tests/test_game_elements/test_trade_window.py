import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.trade_window import TradeSlot, TradeOffer, TradeWindow

@pytest.fixture
def mock_slot_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'locked': False,
        'confirmed': False,
        'item_name': None,
    }.get(key)
    el.is_empty = True
    return el

@pytest.fixture
def mock_offer_element(mock_slot_element):
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'player_name': 'Player1',
        'money': 100,
        'confirmed': False,
    }.get(key)
    el.find_elements.side_effect = lambda *a, **kw: [mock_slot_element]
    el.find_element.side_effect = lambda *a, **kw: None
    return el

@pytest.fixture
def mock_window_element(mock_offer_element):
    el = MagicMock()
    el.find_element.side_effect = lambda *a, **kw: mock_offer_element if kw.get('value') in ['my_offer', 'their_offer'] else None
    el.get_property.side_effect = lambda key: 5 if key == 'countdown' else None
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def slot(mock_slot_element, mock_session):
    return TradeSlot(mock_slot_element, mock_session)

@pytest.fixture
def offer(mock_offer_element, mock_session):
    return TradeOffer(mock_offer_element, mock_session)

@pytest.fixture
def window(mock_window_element, mock_session):
    return TradeWindow(mock_window_element, mock_session)

def test_slot_properties(slot):
    assert slot.is_locked is False
    assert slot.is_confirmed is False

def test_offer_properties(offer):
    assert offer.player_name == 'Player1'
    assert offer.money_offered == 100
    assert offer.is_confirmed is False
    assert isinstance(offer.slots[0], TradeSlot)

def test_offer_get_empty_slot_found(offer, mock_offer_element, mock_slot_element):
    mock_slot_element.is_empty = True
    mock_slot_element.get_property.side_effect = lambda key: False if key == 'locked' else None
    mock_offer_element.find_elements.side_effect = lambda *a, **kw: [mock_slot_element]
    slot = offer.get_empty_slot()
    assert slot is not None

def test_offer_get_empty_slot_none(offer, mock_offer_element, mock_slot_element):
    mock_slot_element.get_property.side_effect = lambda key: 'Sword' if key == 'item_name' else None
    mock_offer_element.find_elements.side_effect = lambda *a, **kw: [mock_slot_element]
    assert offer.get_empty_slot() is None

def test_offer_set_money_success(offer, mock_offer_element):
    money_input = MagicMock()
    money_input.send_keys = MagicMock()
    mock_offer_element.find_element.side_effect = lambda *a, **kw: money_input if kw.get('value') == 'money_input' else None
    offer.set_money(50)
    assert money_input.send_keys.call_count == 2

def test_offer_set_money_negative(offer):
    with pytest.raises(ValueError):
        offer.set_money(-10)

def test_offer_set_money_no_input(offer, mock_offer_element):
    mock_offer_element.find_element.side_effect = lambda *a, **kw: None
    with pytest.raises(ValueError):
        offer.set_money(10)

def test_window_properties(window):
    assert isinstance(window.my_offer, TradeOffer)
    assert isinstance(window.their_offer, TradeOffer)
    assert window.countdown == 5

def test_window_is_confirmed(window, mock_window_element, mock_offer_element):
    mock_offer_element.get_property.side_effect = lambda key: True if key == 'confirmed' else None
    assert window.is_confirmed is True

def test_window_add_item_no_slot(window, mock_session, mock_window_element, mock_offer_element):
    mock_offer_element.get_empty_slot = MagicMock(return_value=None)
    with pytest.raises(ValueError):
        window.add_item('Sword')

def test_window_add_item_no_inventory(window, mock_session, mock_window_element, mock_offer_element):
    mock_offer_element.get_empty_slot = MagicMock(return_value=MagicMock())
    mock_session.find_element = MagicMock(return_value=None)
    with pytest.raises(ValueError):
        window.add_item('Sword')

def test_window_add_item_no_item(window, mock_session, mock_window_element, mock_offer_element):
    mock_offer_element.get_empty_slot = MagicMock(return_value=MagicMock())
    inventory = MagicMock()
    inventory.find_elements.return_value = []
    mock_session.find_element = MagicMock(return_value=inventory)
    with pytest.raises(ValueError):
        window.add_item('Sword')

def test_window_add_item_success(window, mock_session, mock_window_element, mock_offer_element):
    slot = MagicMock()
    slot._element = MagicMock()
    mock_offer_element.get_empty_slot = MagicMock(return_value=slot)
    inventory = MagicMock()
    item = MagicMock()
    item.get_property.return_value = 'Sword'
    item.drag_to = MagicMock()
    inventory.find_elements.return_value = [item]
    mock_session.find_element = MagicMock(return_value=inventory)
    window.add_item('Sword')
    assert item.drag_to.called 