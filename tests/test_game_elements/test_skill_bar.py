import pytest
from pyui_automation.game_elements import SkillBar
from ..conftest import create_mock_element


@pytest.fixture
def skill_bar(mock_element, mock_session):
    return SkillBar(mock_element, mock_session)


def test_use_skill(skill_bar, mock_element):
    """Test using a skill by slot"""
    slot = create_mock_element({'enabled': True})
    mock_element.children = [slot]
    
    skill_bar.use_skill(1)
    assert slot.clicks == 1


def test_use_skill_by_name(skill_bar, mock_element):
    """Test using a skill by name"""
    skill = create_mock_element({'name': 'Fireball', 'enabled': True})
    mock_element.children = [skill]
    
    skill_bar.use_skill_by_name('Fireball')
    assert skill.clicks == 1


def test_is_skill_ready(skill_bar, mock_element):
    """Test checking if skill is ready"""
    skill = create_mock_element({'enabled': True})
    mock_element.children = [skill]
    
    assert skill_bar.is_skill_ready(1) is True
    
    skill.enabled = False
    assert skill_bar.is_skill_ready(1) is False


def test_wait_for_skill_ready(skill_bar, mock_element):
    """Test waiting for skill to be ready"""
    skill = create_mock_element({'enabled': True})
    mock_element.children = [skill]
    
    assert skill_bar.wait_for_skill_ready(1, timeout=1.0) is True


def test_get_skill_cooldown(skill_bar, mock_element):
    """Test getting skill cooldown"""
    skill = create_mock_element({'cooldown': 5.0})
    mock_element.children = [skill]
    
    assert skill_bar.get_skill_cooldown(1) == 5.0


def test_get_skill_charges(skill_bar, mock_element):
    """Test getting skill charges"""
    skill = create_mock_element({'charges': 2})
    mock_element.children = [skill]
    
    assert skill_bar.get_skill_charges(1) == 2
