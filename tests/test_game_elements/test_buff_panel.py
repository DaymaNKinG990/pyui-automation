import pytest
from pyui_automation.game_elements import BuffPanel, Buff, Debuff
from ..conftest import create_mock_element


@pytest.fixture
def buff_panel(mock_element, mock_session):
    return BuffPanel(mock_element, mock_session)


def test_get_active_buffs(buff_panel, mock_element):
    """Test getting active buffs"""
    buff1 = create_mock_element({'name': 'Strength', 'duration': 300})
    buff2 = create_mock_element({'name': 'Agility', 'duration': 600})
    mock_element.children = [buff1, buff2]
    
    buffs = buff_panel.get_active_buffs()
    assert len(buffs) == 2
    assert buffs[0].name == 'Strength'
    assert buffs[1].name == 'Agility'


def test_get_active_debuffs(buff_panel, mock_element):
    """Test getting active debuffs"""
    debuff1 = create_mock_element({'name': 'Poison', 'duration': 10})
    debuff2 = create_mock_element({'name': 'Slow', 'duration': 5})
    mock_element.children = [debuff1, debuff2]
    
    debuffs = buff_panel.get_active_debuffs()
    assert len(debuffs) == 2
    assert debuffs[0].name == 'Poison'
    assert debuffs[1].name == 'Slow'


def test_has_buff(buff_panel, mock_element):
    """Test checking for specific buff"""
    buff = create_mock_element({'name': 'Strength'})
    mock_element.children = [buff]
    
    assert buff_panel.has_buff('Strength') is True
    assert buff_panel.has_buff('Agility') is False


def test_has_debuff(buff_panel, mock_element):
    """Test checking for specific debuff"""
    debuff = create_mock_element({'name': 'Poison'})
    mock_element.children = [debuff]
    
    assert buff_panel.has_debuff('Poison') is True
    assert buff_panel.has_debuff('Slow') is False


def test_cancel_buff(buff_panel, mock_element):
    """Test canceling a buff"""
    buff = create_mock_element({'name': 'Strength'})
    mock_element.children = [buff]
    
    buff_panel.cancel_buff('Strength')
    assert buff.right_clicks == 1


def test_wait_for_buff(buff_panel, mock_element):
    """Test waiting for buff to appear"""
    buff = create_mock_element({'name': 'Strength'})
    mock_element.children = [buff]
    
    assert buff_panel.wait_for_buff('Strength', timeout=1.0) is True


def test_wait_for_buff_expire(buff_panel, mock_element):
    """Test waiting for buff to expire"""
    buff = create_mock_element({'name': 'Strength', 'duration': 0})
    mock_element.children = [buff]
    
    assert buff_panel.wait_for_buff_expire('Strength', timeout=1.0) is True
