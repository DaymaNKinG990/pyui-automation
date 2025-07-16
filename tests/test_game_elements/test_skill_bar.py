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
    return SkillBar(mock_element({}), mock_session)


def test_use_skill(skill_bar, mock_element):
    """Test using a skill by slot"""
    slot = MagicMock()
    slot.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    slot.click = MagicMock()
    # Мокаем find_elements для слотов
    mock_element.find_elements.return_value = [slot]
    mock_element.find_elements.side_effect = lambda **kwargs: [slot] if kwargs.get('by') == 'type' and kwargs.get('value') == 'skill_slot' else []
    skill_bar = SkillBar(mock_element, MagicMock())
    skill_bar.use_skill('Skill 1')
    slot.click.assert_called_once()


def test_use_skill_by_name(skill_bar, mock_element):
    """Test using a skill by name"""
    slot = MagicMock()
    slot.get_property.side_effect = lambda key: {
        'skill_name': 'Fireball',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    slot.click = MagicMock()
    mock_element.find_elements.return_value = [slot]
    mock_element.find_elements.side_effect = lambda **kwargs: [slot] if kwargs.get('by') == 'type' and kwargs.get('value') == 'skill_slot' else []
    skill_bar = SkillBar(mock_element, MagicMock())
    skill_bar.use_skill_by_name('Fireball')
    slot.click.assert_called_once()


def test_is_skill_ready(skill_bar, mock_element):
    """Test checking if skill is ready"""
    slot = MagicMock()
    slot.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    mock_element.find_elements.return_value = [slot]
    mock_element.find_elements.side_effect = lambda **kwargs: [slot] if kwargs.get('by') == 'type' and kwargs.get('value') == 'skill_slot' else []
    skill_bar = SkillBar(mock_element, MagicMock())
    assert skill_bar.is_skill_ready('Skill 1') is True


def test_wait_for_skill_ready(skill_bar, mock_element, mock_session):
    """Test waiting for skill to be ready"""
    slot = MagicMock()
    slot.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 1
    }.get(key)
    mock_element.find_elements.return_value = [slot]
    mock_element.find_elements.side_effect = lambda **kwargs: [slot] if kwargs.get('by') == 'type' and kwargs.get('value') == 'skill_slot' else []
    skill_bar = SkillBar(mock_element, mock_session)
    mock_session.wait_for_condition.return_value = True
    assert skill_bar.wait_for_skill_ready('Skill 1') is True


def test_get_skill_cooldown(skill_bar, mock_element):
    """Test getting skill cooldown"""
    slot = MagicMock()
    slot.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 5.0,
        'charges': 1
    }.get(key)
    mock_element.find_elements.return_value = [slot]
    mock_element.find_elements.side_effect = lambda **kwargs: [slot] if kwargs.get('by') == 'type' and kwargs.get('value') == 'skill_slot' else []
    skill_bar = SkillBar(mock_element, MagicMock())
    assert skill_bar.get_skill_cooldown('Skill 1') == 5.0


def test_get_skill_charges(skill_bar, mock_element):
    """Test getting skill charges"""
    slot = MagicMock()
    slot.get_property.side_effect = lambda key: {
        'skill_name': 'Skill 1',
        'cooldown': 0.0,
        'charges': 2,
        'current_charges': 2,
        'max_charges': 2
    }.get(key)
    mock_element.find_elements.return_value = [slot]
    mock_element.find_elements.side_effect = lambda **kwargs: [slot] if kwargs.get('by') == 'type' and kwargs.get('value') == 'skill_slot' else []
    skill_bar = SkillBar(mock_element, MagicMock())
    assert skill_bar.get_skill_charges('Skill 1')[0] == 2
