import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements import BuffPanel, Buff, Debuff


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


def test_has_buff(buff_panel, mock_element):
    """Test checking for specific buff"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: {'name': 'Strength'}.get(key)
    
    mock_element.find_elements.return_value = [buff]
    
    assert buff_panel.has_buff('Strength') is True
    assert buff_panel.has_buff('Agility') is False


def test_has_debuff(buff_panel, mock_element):
    """Test checking for specific debuff"""
    debuff = MagicMock()
    debuff.get_property.side_effect = lambda key: {'name': 'Poison'}.get(key)
    
    mock_element.find_elements.return_value = [debuff]
    
    assert buff_panel.has_debuff('Poison') is True
    assert buff_panel.has_debuff('Slow') is False


def test_cancel_buff(buff_panel, mock_element):
    """Test canceling a buff"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: {'name': 'Strength'}.get(key)
    buff.clicks = 0
    buff.right_click = lambda: setattr(buff, 'clicks', buff.clicks + 1)
    
    mock_element.find_elements.return_value = [buff]
    
    buff_panel.cancel_buff('Strength')
    assert buff.clicks == 1


def test_wait_for_buff(buff_panel, mock_element):
    """Test waiting for buff to appear"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: {'name': 'Strength'}.get(key)
    
    mock_element.find_elements.return_value = [buff]
    
    assert buff_panel.wait_for_buff('Strength', timeout=1.0) is True


def test_wait_for_buff_expire(buff_panel, mock_element):
    """Test waiting for buff to expire"""
    buff = MagicMock()
    buff.get_property.side_effect = lambda key: {'name': 'Strength', 'duration': 0}.get(key)
    
    mock_element.find_elements.return_value = [buff]
    
    assert buff_panel.wait_for_buff_expire('Strength', timeout=1.0) is True
