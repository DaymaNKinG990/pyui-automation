import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.mount_pet_panel import Mount, Pet, MountPetPanel

@pytest.fixture
def mock_mount_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Horse',
        'type': 'ground',
        'speed': 100,
        'favorite': False,
        'active': False,
        'unlocked': True,
    }.get(key)
    el.find_element.side_effect = lambda by=None, value=None: None
    el.click = MagicMock()
    return el

@pytest.fixture
def mock_pet_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Wolf',
        'type': 'beast',
        'level': 5,
        'happiness': 80,
        'favorite': False,
        'active': False,
        'abilities': ['Bite', 'Howl'],
    }.get(key)
    el.find_element.side_effect = lambda by=None, value=None: None
    el.click = MagicMock()
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_panel_element():
    el = MagicMock()
    el.find_element.side_effect = lambda *a, **kw: None
    el.find_elements.side_effect = lambda *a, **kw: []
    return el

@pytest.fixture
def mount(mock_mount_element, mock_session):
    return Mount(mock_mount_element, mock_session)

@pytest.fixture
def pet(mock_pet_element, mock_session):
    return Pet(mock_pet_element, mock_session)

@pytest.fixture
def panel(mock_panel_element, mock_session):
    return MountPetPanel(mock_panel_element, mock_session)

def test_mount_properties(mount):
    assert mount.name == 'Horse'
    assert mount.type == 'ground'
    assert mount.speed == 100
    assert mount.is_favorite is False
    assert mount.is_active is False
    assert mount.is_unlocked is True

def test_mount_summon_success(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: True if key == 'unlocked' else False if key == 'active' else 'Horse' if key == 'name' else 100 if key == 'speed' else False
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_mount_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'summon_button' else None
    assert mount.summon() is True
    assert btn.click.called

def test_mount_summon_locked(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: False if key == 'unlocked' else False
    assert mount.summon() is False

def test_mount_summon_already_active(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: True if key == 'active' else True
    assert mount.summon() is False

def test_mount_summon_button_disabled(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: True if key == 'unlocked' else False
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_mount_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'summon_button' else None
    assert mount.summon() is False

def test_mount_set_favorite_success(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: False if key == 'favorite' else None
    btn = MagicMock()
    btn.click = MagicMock()
    mock_mount_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'favorite_button' else None
    assert mount.set_favorite(True) is True
    assert btn.click.called

def test_mount_set_favorite_no_change(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: True if key == 'favorite' else None
    assert mount.set_favorite(True) is False

def test_mount_set_favorite_no_button(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: False if key == 'favorite' else None
    mock_mount_element.find_element.side_effect = lambda by=None, value=None: None
    assert mount.set_favorite(True) is False

def test_mount_get_property_exception(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = mount.name

def test_mount_summon_find_element_exception(mount, mock_mount_element):
    mock_mount_element.get_property.side_effect = lambda key: True if key == 'unlocked' else False
    mock_mount_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        mount.summon()

def test_pet_properties(pet):
    assert pet.name == 'Wolf'
    assert pet.type == 'beast'
    assert pet.level == 5
    assert pet.happiness == 80
    assert pet.is_favorite is False
    assert pet.is_active is False
    assert pet.abilities == ['Bite', 'Howl']

def test_pet_summon_success(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: False if key == 'active' else 'Wolf' if key == 'name' else 5 if key == 'level' else 80 if key == 'happiness' else False
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'summon_button' else None
    assert pet.summon() is True
    assert btn.click.called

def test_pet_summon_already_active(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: True if key == 'active' else False
    assert pet.summon() is False

def test_pet_summon_button_disabled(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: False if key == 'active' else False
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'summon_button' else None
    assert pet.summon() is False

def test_pet_dismiss_success(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: True if key == 'active' else False
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'dismiss_button' else None
    assert pet.dismiss() is True
    assert btn.click.called

def test_pet_dismiss_not_active(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: False if key == 'active' else False
    assert pet.dismiss() is False

def test_pet_dismiss_button_disabled(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: True if key == 'active' else False
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'dismiss_button' else None
    assert pet.dismiss() is False

def test_pet_rename_success(pet, mock_pet_element):
    btn = MagicMock()
    btn.click = MagicMock()
    name_input = MagicMock()
    name_input.send_keys = MagicMock()
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'rename_button' else name_input if value == 'name_input' else None
    assert pet.rename('Fang') is True
    assert btn.click.called
    assert name_input.send_keys.call_count == 2

def test_pet_rename_no_button(pet, mock_pet_element):
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: None
    assert pet.rename('Fang') is False

def test_pet_set_favorite_success(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: False if key == 'favorite' else None
    btn = MagicMock()
    btn.click = MagicMock()
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'favorite_button' else None
    assert pet.set_favorite(True) is True
    assert btn.click.called

def test_pet_set_favorite_no_change(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: True if key == 'favorite' else None
    assert pet.set_favorite(True) is False

def test_pet_set_favorite_no_button(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: False if key == 'favorite' else None
    mock_pet_element.find_element.side_effect = lambda by=None, value=None: None
    assert pet.set_favorite(True) is False

def test_pet_get_property_exception(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = pet.name

def test_pet_summon_find_element_exception(pet, mock_pet_element):
    mock_pet_element.get_property.side_effect = lambda key: False if key == 'active' else False
    mock_pet_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        pet.summon()

def test_active_mount_none(panel, mock_panel_element):
    mock_panel_element.find_element.side_effect = lambda *a, **kw: None
    assert panel.active_mount is None

def test_active_pet_none(panel, mock_panel_element):
    mock_panel_element.find_element.side_effect = lambda *a, **kw: None
    assert panel.active_pet is None

def test_get_mounts_empty(panel, mock_panel_element):
    mock_panel_element.find_elements.side_effect = lambda *a, **kw: []
    assert panel.get_mounts() == []

def test_get_pets_empty(panel, mock_panel_element):
    mock_panel_element.find_elements.side_effect = lambda *a, **kw: []
    assert panel.get_pets() == []

def test_get_mount_none(panel, mock_panel_element):
    mock_panel_element.find_element.side_effect = lambda *a, **kw: None
    assert panel.get_mount('Horse') is None

def test_get_pet_none(panel, mock_panel_element):
    mock_panel_element.find_element.side_effect = lambda *a, **kw: None
    assert panel.get_pet('Wolf') is None

def test_get_favorite_mounts_empty(panel, mock_panel_element):
    mock_panel_element.find_elements.side_effect = lambda *a, **kw: []
    assert panel.get_favorite_mounts() == []

def test_get_favorite_pets_empty(panel, mock_panel_element):
    mock_panel_element.find_elements.side_effect = lambda *a, **kw: []
    assert panel.get_favorite_pets() == []

def test_summon_random_favorite_success(panel, mock_panel_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_panel_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'random_button' else None
    assert panel.summon_random_favorite(mount=True) is True
    assert btn.click.called

def test_summon_random_favorite_disabled(panel, mock_panel_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_panel_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'random_button' else None
    assert panel.summon_random_favorite(mount=True) is False

def test_summon_random_favorite_no_button(panel, mock_panel_element):
    mock_panel_element.find_element.side_effect = lambda *a, **kw: None
    assert panel.summon_random_favorite(mount=True) is False

def test_active_mount_find_element_exception(panel, mock_panel_element):
    mock_panel_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = panel.active_mount

def test_get_mounts_find_elements_exception(panel, mock_panel_element):
    mock_panel_element.find_elements.side_effect = Exception('fail')
    with pytest.raises(Exception):
        panel.get_mounts() 