import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements import SkillBar


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
    mock.wait_for_condition.return_value = True
    return mock

@pytest.fixture
def skill_bar(mock_element, mock_session):
    return SkillBar(mock_element, mock_session)


def test_use_skill(skill_bar, mock_element):
    """Test using a skill by slot"""
    skill = MagicMock()
    skill.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    skill.click = MagicMock()
    
    mock_element.find_elements.return_value = [skill]
    skill_bar.use_skill('Skill 1')
    skill.click.assert_called_once()


def test_use_skill_by_name(skill_bar, mock_element):
    """Test using a skill by name"""
    skill = MagicMock()
    skill.get_property.side_effect = lambda key: {
        'skill_name': 'Fireball',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    skill.click = MagicMock()
    
    mock_element.find_elements.return_value = [skill]
    skill_bar.use_skill_by_name('Fireball')
    skill.click.assert_called_once()


def test_is_skill_ready(skill_bar, mock_element):
    """Test checking if skill is ready"""
    skill = MagicMock()
    skill.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    
    mock_element.find_elements.return_value = [skill]
    assert skill_bar.is_skill_ready('Skill 1') is True


def test_wait_for_skill_ready(skill_bar, mock_element, mock_session):
    """Test waiting for skill to be ready"""
    skill = MagicMock()
    skill.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    
    mock_element.find_elements.return_value = [skill]
    mock_session.wait_for_condition.return_value = True
    
    assert skill_bar.wait_for_skill_ready('Skill 1') is True


def test_get_skill_cooldown(skill_bar, mock_element):
    """Test getting skill cooldown"""
    skill = MagicMock()
    skill.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 5.0,
        'charges': 1
    }.get(key)
    
    mock_element.find_elements.return_value = [skill]
    assert skill_bar.get_skill_cooldown('Skill 1') == 5.0


def test_get_skill_charges(skill_bar, mock_element):
    """Test getting skill charges"""
    skill = MagicMock()
    skill.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 2
    }.get(key)
    
    mock_element.find_elements.return_value = [skill]
    assert skill_bar.get_skill_charges('Skill 1') == 2
