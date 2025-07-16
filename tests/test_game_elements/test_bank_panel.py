import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.bank_panel import BankTab, BankSlot, BankPanel

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Tab1',
        'icon': 'icon.png',
        'locked': False,
        'slots_used': 5,
        'slots_total': 10,
        'item_name': 'Sword',
        'current_stack': 3,
        'max_stack': 10,
        'visible': True,
        'gold': 1000,
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    return s

@pytest.fixture
def bank_tab(mock_element, mock_session):
    return BankTab(mock_element, mock_session)

@pytest.fixture
def bank_slot(mock_element, mock_session):
    return BankSlot(mock_element, mock_session)

@pytest.fixture
def bank_panel(mock_element, mock_session):
    return BankPanel(mock_element, mock_session)

def test_bank_tab_properties(bank_tab):
    assert bank_tab.name == 'Tab1'
    assert bank_tab.icon == 'icon.png'
    assert bank_tab.is_locked is False
    assert bank_tab.slots_used == 5
    assert bank_tab.slots_total == 10

def test_bank_tab_select_unlocked(bank_tab, mock_element):
    mock_element.get_property.side_effect = lambda key: False if key == 'locked' else 'x'
    bank_tab._element.click = MagicMock()
    assert bank_tab.select() is True
    assert bank_tab._element.click.called

def test_bank_tab_select_locked(bank_tab, mock_element):
    mock_element.get_property.side_effect = lambda key: True if key == 'locked' else 'x'
    assert bank_tab.select() is False

def test_bank_slot_properties(bank_slot):
    assert bank_slot.item_name == 'Sword'
    assert bank_slot.stack_size == (3, 10)
    assert bank_slot.is_empty is False

def test_bank_slot_is_empty_true(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: None if key == 'item_name' else 'x'
    slot = BankSlot(mock_element, mock_session)
    assert slot.is_empty is True

def test_bank_slot_deposit_item_success(bank_slot, mock_element):
    mock_element.get_property.side_effect = lambda key: None if key == 'item_name' else 'x'
    bank_slot._element.click = MagicMock()
    assert bank_slot.deposit_item() is True
    assert bank_slot._element.click.called

def test_bank_slot_deposit_item_fail(bank_slot, mock_element):
    mock_element.get_property.side_effect = lambda key: 'Sword' if key == 'item_name' else 'x'
    assert bank_slot.deposit_item() is False

def test_bank_slot_withdraw_item_all(bank_slot, mock_element):
    mock_element.get_property.side_effect = lambda key: 'Sword' if key == 'item_name' else 'x'
    bank_slot._element.click = MagicMock()
    assert bank_slot.withdraw_item() is True
    assert bank_slot._element.click.called

def test_bank_slot_withdraw_item_amount(bank_slot, mock_element):
    mock_element.get_property.side_effect = lambda key: 'Sword' if key == 'item_name' else 'x'
    bank_slot._element.right_click = MagicMock()
    amount_input = MagicMock()
    bank_slot._element.find_element = MagicMock(return_value=amount_input)
    assert bank_slot.withdraw_item(amount=2) is True
    assert bank_slot._element.right_click.called
    assert amount_input.send_keys.called

def test_bank_slot_withdraw_item_fail(bank_slot, mock_element):
    mock_element.get_property.side_effect = lambda key: None if key == 'item_name' else 'x'
    assert bank_slot.withdraw_item() is False

def test_bank_slot_wait_until_empty(bank_slot, mock_session):
    assert bank_slot.wait_until_empty(timeout=1.0) is True

def test_bank_slot_wait_for_item(bank_slot, mock_session):
    assert bank_slot.wait_for_item('Sword', timeout=1.0) is True

def test_bank_panel_properties(bank_panel):
    assert bank_panel.is_open is True
    assert bank_panel.gold == 1000

def test_bank_panel_tabs(bank_panel, mock_element, mock_session):
    tab_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'bank_tab' else []
    panel = BankPanel(mock_element, mock_session)
    tabs = panel.tabs
    assert all(isinstance(t, BankTab) for t in tabs)

def test_bank_panel_get_tab(bank_panel, mock_element, mock_session):
    tab_el = MagicMock()
    tab_el.get_property.side_effect = lambda key: 'Tab1' if key == 'name' else False if key == 'locked' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'bank_tab' else []
    panel = BankPanel(mock_element, mock_session)
    tab = panel.get_tab('Tab1')
    assert tab is not None
    assert tab.name == 'Tab1'

def test_bank_panel_get_slots(bank_panel, mock_element, mock_session):
    slot_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [slot_el] if value == 'bank_slot' else []
    panel = BankPanel(mock_element, mock_session)
    slots = panel.get_slots()
    assert all(isinstance(s, BankSlot) for s in slots)

def test_bank_panel_find_item(bank_panel, mock_element, mock_session):
    tab_el = MagicMock()
    tab_el.get_property.side_effect = lambda key: False if key == 'locked' else 'Tab1' if key == 'name' else 'x'
    slot_el = MagicMock()
    slot_el.get_property.side_effect = lambda key: 'Sword' if key == 'item_name' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'bank_tab' else [slot_el] if value == 'bank_slot' else []
    panel = BankPanel(mock_element, mock_session)
    slot = panel.find_item('Sword')
    assert slot is not None
    assert slot.item_name == 'Sword'

def test_bank_panel_find_item_not_found(bank_panel, mock_element, mock_session):
    tab_el = MagicMock()
    tab_el.get_property.side_effect = lambda key: False if key == 'locked' else 'Tab1' if key == 'name' else 'x'
    slot_el = MagicMock()
    slot_el.get_property.side_effect = lambda key: None if key == 'item_name' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'bank_tab' else [slot_el] if value == 'bank_slot' else []
    panel = BankPanel(mock_element, mock_session)
    slot = panel.find_item('Sword')
    assert slot is None

def test_bank_panel_deposit_gold_success(bank_panel, mock_element):
    deposit_btn = MagicMock()
    amount_input = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: deposit_btn if value == 'deposit_gold' else amount_input if value == 'gold_input' else None
    assert bank_panel.deposit_gold(100) is True
    assert deposit_btn.click.called
    assert amount_input.send_keys.called

def test_bank_panel_deposit_gold_fail(bank_panel, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    assert bank_panel.deposit_gold(100) is False

def test_bank_panel_withdraw_gold_success(bank_panel, mock_element):
    mock_element.get_property.side_effect = lambda key: 1000 if key == 'gold' else 'x'
    withdraw_btn = MagicMock()
    amount_input = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: withdraw_btn if value == 'withdraw_gold' else amount_input if value == 'gold_input' else None
    assert bank_panel.withdraw_gold(100) is True
    assert withdraw_btn.click.called
    assert amount_input.send_keys.called

def test_bank_panel_withdraw_gold_fail_not_enough(bank_panel, mock_element):
    mock_element.get_property.side_effect = lambda key: 10 if key == 'gold' else 'x'
    assert bank_panel.withdraw_gold(100) is False

def test_bank_panel_withdraw_gold_fail_no_button(bank_panel, mock_element):
    mock_element.get_property.side_effect = lambda key: 1000 if key == 'gold' else 'x'
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    assert bank_panel.withdraw_gold(100) is False 