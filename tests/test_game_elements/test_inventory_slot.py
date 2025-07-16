import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.inventory_slot import InventorySlot

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'has_item': True,
        'item_name': 'Sword',
        'item_count': 5,
        'item_rarity': 'rare',
        'item_level': 10,
        'item_properties': {'damage': 10},
        'selected': False,
        'locked': False,
    }.get(key)
    el.right_click = MagicMock()
    el.drag_to = MagicMock()
    el.shift_right_click = MagicMock()
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.send_keys = MagicMock()
    s.wait_for_condition = MagicMock(return_value=True)
    return s

@pytest.fixture
def slot(mock_element, mock_session):
    return InventorySlot(mock_element, mock_session)

def test_properties(slot):
    assert slot.is_empty is False
    assert slot.item_name == 'Sword'
    assert slot.item_count == 5
    assert slot.item_rarity == 'rare'
    assert slot.item_level == 10
    assert slot.item_properties == {'damage': 10}
    assert slot.is_selected is False
    assert slot.is_locked is False

def test_is_empty_true(slot, mock_element):
    mock_element.get_property.side_effect = lambda key: False if key == 'has_item' else None
    assert slot.is_empty is True
    assert slot.item_name is None
    assert slot.item_rarity is None
    assert slot.item_level is None

def test_item_count_default(slot, mock_element):
    mock_element.get_property.side_effect = lambda key: None
    assert slot.item_count == 0

def test_select(slot, mock_element):
    slot.select()
    mock_element.click.assert_called()

def test_right_click(slot, mock_element):
    slot.right_click()
    mock_element.right_click.assert_called()

def test_drag_to_success(slot, mock_element, mock_session):
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: True if key == 'has_item' else False
    target_el.get_property.side_effect = lambda key: False if key == 'locked' else True if key == 'has_item' else None
    target_slot = InventorySlot(target_el, mock_session)
    target_slot._element.get_property.side_effect = lambda key: False if key == 'locked' else None
    slot._element.get_property.side_effect = lambda key: True if key == 'has_item' else None
    slot._element.drag_to = MagicMock()
    slot.drag_to(target_slot)
    slot._element.drag_to.assert_called_with(target_slot._element)

def test_drag_to_empty_slot_raises(slot, mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: False if key == 'has_item' else None
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: False
    target_slot = InventorySlot(target_el, mock_session)
    with pytest.raises(ValueError):
        slot.drag_to(target_slot)

def test_drag_to_locked_slot_raises(slot, mock_element, mock_session):
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: True if key == 'locked' else None
    target_slot = InventorySlot(target_el, mock_session)
    with pytest.raises(ValueError):
        slot.drag_to(target_slot)

def test_drag_to_invalid_slot_raises(slot):
    with pytest.raises(ValueError):
        slot.drag_to(None)

def test_split_stack_success(slot, mock_element, mock_session):
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: False if key == 'locked' or key == 'has_item' else None
    target_slot = InventorySlot(target_el, mock_session)
    slot._element.get_property.side_effect = lambda key: True if key == 'has_item' else 5 if key == 'item_count' else None
    slot._element.shift_right_click = MagicMock()
    slot._session.send_keys = MagicMock()
    slot.split_stack(target_slot, 2)
    slot._element.shift_right_click.assert_called()
    slot._session.send_keys.assert_any_call('2')
    slot._session.send_keys.assert_any_call('Enter')

def test_split_stack_empty_raises(slot, mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: False if key == 'has_item' else None
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: False
    target_slot = InventorySlot(target_el, mock_session)
    with pytest.raises(ValueError):
        slot.split_stack(target_slot, 1)

def test_split_stack_amount_too_large_raises(slot, mock_element, mock_session):
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: False
    target_slot = InventorySlot(target_el, mock_session)
    slot._element.get_property.side_effect = lambda key: True if key == 'has_item' else 2 if key == 'item_count' else None
    with pytest.raises(ValueError):
        slot.split_stack(target_slot, 2)

def test_split_stack_locked_or_nonempty_target_raises(slot, mock_element, mock_session):
    target_el = MagicMock()
    target_el.get_property.side_effect = lambda key: True if key == 'locked' else True if key == 'has_item' else None
    target_slot = InventorySlot(target_el, mock_session)
    slot._element.get_property.side_effect = lambda key: True if key == 'has_item' else 5 if key == 'item_count' else None
    with pytest.raises(ValueError):
        slot.split_stack(target_slot, 1)

def test_get_property_exception(slot, mock_element):
    mock_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = slot.is_empty 