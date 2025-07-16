import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.equipment_panel import EquipmentSlot, EquipmentSet, EquipmentPanel

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'slot_type': 'head',
        'item_name': 'Helmet',
        'item_level': 10,
        'durability_current': 5,
        'durability_max': 10,
        'stats': {'defense': 5.0},
        'requirements': {'level': 5},
        'name': 'Set1',
        'items': {'head': 'Helmet'},
        'average_item_level': 12.5,
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    s.find_element.return_value = MagicMock()
    return s

@pytest.fixture
def equipment_slot(mock_element, mock_session):
    return EquipmentSlot(mock_element, mock_session)

@pytest.fixture
def equipment_set(mock_element, mock_session):
    return EquipmentSet(mock_element, mock_session)

@pytest.fixture
def equipment_panel(mock_element, mock_session):
    return EquipmentPanel(mock_element, mock_session)

def test_equipment_slot_properties(equipment_slot):
    assert equipment_slot.slot_type == 'head'
    assert equipment_slot.item_name == 'Helmet'
    assert equipment_slot.item_level == 10
    assert equipment_slot.durability == (5, 10)
    assert equipment_slot.stats == {'defense': 5.0}
    assert equipment_slot.requirements == {'level': 5}
    assert equipment_slot.is_broken is False

def test_equipment_slot_is_broken_true(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 0 if key == 'durability_current' else 10 if key == 'durability_max' else 'Helmet' if key == 'item_name' else 'head' if key == 'slot_type' else None
    slot = EquipmentSlot(mock_element, mock_session)
    assert slot.is_broken is True

def test_equipment_slot_unequip_success(equipment_slot, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Unequip' else None
    equipment_slot.unequip()
    assert btn.click.called

def test_equipment_slot_unequip_fail(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: None if key == 'item_name' else 'head' if key == 'slot_type' else 10
    slot = EquipmentSlot(mock_element, mock_session)
    with pytest.raises(ValueError):
        slot.unequip()

def test_equipment_slot_repair_success(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 0 if key == 'durability_current' else 10 if key == 'durability_max' else 'Helmet' if key == 'item_name' else 'head' if key == 'slot_type' else None
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Repair' else None
    slot = EquipmentSlot(mock_element, mock_session)
    slot.repair()
    assert btn.click.called

def test_equipment_slot_repair_fail_not_broken(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 5 if key == 'durability_current' else 10 if key == 'durability_max' else 'Helmet' if key == 'item_name' else 'head' if key == 'slot_type' else None
    slot = EquipmentSlot(mock_element, mock_session)
    with pytest.raises(ValueError):
        slot.repair()

def test_equipment_slot_wait_until_equipped(equipment_slot, mock_session):
    assert equipment_slot.wait_until_equipped('Helmet', timeout=1.0) is True

def test_equipment_slot_wait_until_repaired(equipment_slot, mock_session):
    assert equipment_slot.wait_until_repaired(timeout=1.0) is True

def test_equipment_set_properties(equipment_set):
    assert equipment_set.name == 'Set1'
    assert equipment_set.items == {'head': 'Helmet'}

def test_equipment_set_equip(equipment_set, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Equip' else None
    equipment_set.equip()
    assert btn.click.called

def test_equipment_set_update(equipment_set, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Update' else None
    equipment_set.update()
    assert btn.click.called

def test_equipment_set_delete(equipment_set, mock_element, mock_session):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Delete' else None
    mock_session.find_element.return_value = MagicMock()
    equipment_set._session = mock_session
    equipment_set.delete()
    assert btn.click.called
    assert mock_session.find_element.return_value.click.called

def test_equipment_panel_slots(equipment_panel, mock_element, mock_session):
    slot_el = MagicMock()
    slot_el.get_property.side_effect = lambda key: 'head' if key == 'slot_type' else 'Helmet' if key == 'item_name' else 10 if key == 'item_level' else 5 if key == 'durability_current' else 10 if key == 'durability_max' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None: [slot_el] if value == 'equipment_slot' else []
    panel = EquipmentPanel(mock_element, mock_session)
    slots = panel.slots
    assert 'head' in slots
    assert isinstance(slots['head'], EquipmentSlot)

def test_equipment_panel_equipment_sets(equipment_panel, mock_element, mock_session):
    set_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [set_el] if value == 'equipment_set' else []
    panel = EquipmentPanel(mock_element, mock_session)
    sets = panel.equipment_sets
    assert all(isinstance(s, EquipmentSet) for s in sets)

def test_equipment_panel_average_item_level(equipment_panel):
    assert equipment_panel.average_item_level == 12.5

def test_equipment_panel_get_slot(equipment_panel, mock_element, mock_session):
    slot_el = MagicMock()
    slot_el.get_property.side_effect = lambda key: 'head' if key == 'slot_type' else 'Helmet' if key == 'item_name' else 10 if key == 'item_level' else 5 if key == 'durability_current' else 10 if key == 'durability_max' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None: [slot_el] if value == 'equipment_slot' else []
    panel = EquipmentPanel(mock_element, mock_session)
    slot = panel.get_slot('head')
    assert slot is not None
    assert slot.slot_type == 'head'

def test_equipment_panel_get_equipment_set(equipment_panel, mock_element, mock_session):
    set_el = MagicMock()
    set_el.get_property.side_effect = lambda key: 'Set1' if key == 'name' else {'head': 'Helmet'} if key == 'items' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None: [set_el] if value == 'equipment_set' else []
    panel = EquipmentPanel(mock_element, mock_session)
    eq_set = panel.get_equipment_set('Set1')
    assert eq_set is not None
    assert eq_set.name == 'Set1'

def test_equipment_panel_create_equipment_set(equipment_panel, mock_element, mock_session):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'CreateSet' else None
    mock_session.find_element.return_value = MagicMock()
    equipment_panel._session = mock_session
    equipment_panel.create_equipment_set('Set2')
    btn.click.assert_called()

def test_equipment_panel_create_equipment_set_no_button(equipment_panel, mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    equipment_panel._session = mock_session
    equipment_panel.create_equipment_set('Set2')  # Не должно быть исключения

def test_equipment_panel_repair_all(equipment_panel, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'RepairAll' else None
    equipment_panel.repair_all()
    assert btn.click.called

def test_equipment_panel_repair_all_no_button(equipment_panel, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    equipment_panel.repair_all()  # Не должно быть исключения

def test_equipment_panel_unequip_all(equipment_panel, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'UnequipAll' else None
    equipment_panel.unequip_all()
    btn.click.assert_called()

def test_equipment_panel_unequip_all_no_button(equipment_panel, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    equipment_panel.unequip_all()  # Не должно быть исключения

def test_equipment_panel_wait_until_item_level_success(equipment_panel, mock_session):
    mock_session.wait_for_condition.return_value = True
    equipment_panel._session = mock_session
    assert equipment_panel.wait_until_item_level(10.0, timeout=1.0) is True

def test_equipment_panel_wait_until_item_level_fail(equipment_panel, mock_session):
    mock_session.wait_for_condition.return_value = False
    equipment_panel._session = mock_session
    assert equipment_panel.wait_until_item_level(10.0, timeout=1.0) is False

def test_equipment_panel_wait_until_all_repaired_success(equipment_panel, mock_session):
    mock_session.wait_for_condition.return_value = True
    equipment_panel._session = mock_session
    assert equipment_panel.wait_until_all_repaired(timeout=1.0) is True

def test_equipment_panel_wait_until_all_repaired_fail(equipment_panel, mock_session):
    mock_session.wait_for_condition.return_value = False
    equipment_panel._session = mock_session
    assert equipment_panel.wait_until_all_repaired(timeout=1.0) is False 