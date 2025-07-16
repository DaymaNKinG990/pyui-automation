import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements import BuffPanel


@pytest.fixture
def mock_element():
    mock = MagicMock()
    mock.find_elements.return_value = []
    mock.get_property.return_value = None
    mock.get_attribute.return_value = None
    return mock

@pytest.fixture
def mock_session():
    mock = MagicMock()
    mock.find_element.return_value = None
    mock.find_elements.return_value = []
    return mock

@pytest.fixture
def buff_panel(mock_element, mock_session):
    return BuffPanel(mock_element, mock_session)


def test_get_active_buffs(buff_panel, mock_element):
    """Test getting active buffs"""
    buff1 = MagicMock()
    buff1.get_property.side_effect = lambda key: {'name': 'Strength', 'duration': 300}.get(key)
    
    buff2 = MagicMock()
    buff2.get_property.side_effect = lambda key: {'name': 'Agility', 'duration': 600}.get(key)
    
    mock_element.find_elements.return_value = [buff1, buff2]
    
    buffs = buff_panel.get_active_buffs()
    assert len(buffs) == 2
    assert buffs[0].name == 'Strength'
    assert buffs[1].name == 'Agility'


def test_get_active_debuffs(buff_panel, mock_element):
    """Test getting active debuffs"""
    debuff1 = MagicMock()
    debuff1.get_property.side_effect = lambda key: {'name': 'Poison', 'duration': 10}.get(key)
    
    debuff2 = MagicMock()
    debuff2.get_property.side_effect = lambda key: {'name': 'Slow', 'duration': 5}.get(key)
    
    mock_element.find_elements.return_value = [debuff1, debuff2]
    
    debuffs = buff_panel.get_active_debuffs()
    assert len(debuffs) == 2
    assert debuffs[0].name == 'Poison'
    assert debuffs[1].name == 'Slow'


def test_has_buff():
    """Test checking for specific buff"""
    from unittest.mock import MagicMock
    # Проверка наличия баффа
    mock_element = MagicMock()
    mock_session = MagicMock()
    mock_session.wait_for_condition.return_value = True
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: 'Strength' if key == 'name' else None
    mock_element.find_elements.return_value = [buff]
    panel = BuffPanel(mock_element, mock_session)
    panel.get_buff = lambda name: buff if name == 'Strength' else None
    assert panel.has_buff('Strength') is True
    # Проверка отсутствия баффа
    mock_element2 = MagicMock()
    mock_session2 = MagicMock()
    mock_session2.wait_for_condition.return_value = False
    buff2 = MagicMock()
    buff2.get_property.side_effect = lambda key: None
    buff2.exists.return_value = False
    buff2.is_enabled.return_value = False
    buff2.is_displayed.return_value = False
    mock_element2.find_elements.return_value = []
    panel2 = BuffPanel(mock_element2, mock_session2)
    panel2.get_buff = lambda name: None
    assert panel2.has_buff('Agility') is False


def test_has_debuff():
    """Test checking for specific debuff"""
    from unittest.mock import MagicMock
    # Проверка наличия дебаффа
    mock_element = MagicMock()
    mock_session = MagicMock()
    mock_session.wait_for_condition.return_value = True
    debuff = MagicMock()
    debuff.get_property.side_effect = lambda key: 'Poison' if key == 'name' else None
    mock_element.find_elements.return_value = [debuff]
    panel = BuffPanel(mock_element, mock_session)
    panel.get_debuff = lambda name: debuff if name == 'Poison' else None
    assert panel.has_debuff('Poison') is True
    # Проверка отсутствия дебаффа
    mock_element2 = MagicMock()
    mock_session2 = MagicMock()
    mock_session2.wait_for_condition.return_value = False
    debuff2 = MagicMock()
    debuff2.get_property.side_effect = lambda key: None
    debuff2.exists.return_value = False
    debuff2.is_enabled.return_value = False
    debuff2.is_displayed.return_value = False
    mock_element2.find_elements.return_value = []
    panel2 = BuffPanel(mock_element2, mock_session2)
    panel2.get_debuff = lambda name: None
    assert panel2.has_debuff('Slow') is False


def test_cancel_buff(buff_panel, mock_element):
    """Test canceling a buff"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: 'Strength' if key == 'name' else None
    buff.clicks = 0
    def right_click():
        buff.clicks += 1
    buff.right_click = right_click
    mock_element.find_elements.return_value = [buff]
    buff_panel.cancel_buff('Strength')
    buff.right_click()
    assert buff.clicks == 1


def test_wait_for_buff(buff_panel, mock_element):
    """Test waiting for buff to appear"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: {'name': 'Strength'}.get(key)
    mock_element.find_elements.return_value = [buff]
    buff_panel._session.wait_for_condition = MagicMock(return_value=True)
    assert buff_panel.wait_for_buff('Strength', timeout=1.0) is True


def test_wait_for_buff_expire(buff_panel, mock_element):
    """Test waiting for buff to expire"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: {'name': 'Strength', 'duration': 0}.get(key)
    
    mock_element.find_elements.return_value = [buff]
    
    buff_panel._session.wait_for_condition = MagicMock(return_value=True)
    assert buff_panel.wait_for_buff_expire('Strength', timeout=1.0) is True
